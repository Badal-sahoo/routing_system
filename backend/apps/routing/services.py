from django.conf import settings

from apps.agents.models import Agent
from apps.graph.models import Node
from apps.graph.services import build_adjacency, reverse_adjacency
from apps.tasks.models import Task
from apps.tasks.services import DispatchError, assign_task_to_agent

from .algorithms import dijkstra, shortest_path


def travel_times_to(node_id, adjacency=None):
    if adjacency is None:
        adjacency = build_adjacency()
    return dijkstra(reverse_adjacency(adjacency), node_id)


def find_nearest_agent(origin_node_id, travel_to_origin=None):
    if travel_to_origin is None:
        travel_to_origin = travel_times_to(origin_node_id)

    candidates = Agent.objects.filter(
        status=Agent.Status.AVAILABLE, current_node_fk__isnull=False
    ).only("id", "current_node_fk")

    best_agent = None
    best_distance = None
    for agent in candidates:
        distance = travel_to_origin.get(agent.current_node_fk_id)
        if distance is None:
            continue
        if best_distance is None or distance < best_distance:
            best_agent = agent
            best_distance = distance

    return best_agent, best_distance


def road_minutes(adjacency, from_node_id, to_node_id):
    weights = [
        weight
        for neighbour, weight in adjacency[from_node_id]
        if neighbour == to_node_id
    ]
    return min(weights)


def delivery_route(start_node_id, origin_node_id, destination_node_id, minutes_per_step=None):
    if minutes_per_step is None:
        minutes_per_step = settings.DELIVERY_MINUTES_PER_STEP

    adjacency = build_adjacency()
    to_pickup, _ = shortest_path(adjacency, start_node_id, origin_node_id)
    to_dropoff, _ = shortest_path(adjacency, origin_node_id, destination_node_id)
    if to_pickup is None or to_dropoff is None:
        return []

    path = to_pickup + to_dropoff[1:]
    nodes = Node.objects.in_bulk(set(path))

    waypoints = []
    for current_id, next_id in zip(path, path[1:]):
        minutes = road_minutes(adjacency, current_id, next_id)
        steps = max(1, round(minutes / minutes_per_step))

        here = nodes[current_id]
        there = nodes[next_id]
        from_lat = float(here.lat)
        from_lng = float(here.lng)
        to_lat = float(there.lat)
        to_lng = float(there.lng)

        for step in range(1, steps + 1):
            fraction = step / steps
            lat = from_lat + (to_lat - from_lat) * fraction
            lng = from_lng + (to_lng - from_lng) * fraction
            waypoints.append((round(lat, 6), round(lng, 6)))

    return waypoints


def dispatch_task_to_nearest_agent(task_id):
    task = (
        Task.objects.filter(pk=task_id)
        .only("id", "status", "origin_node_fk", "destination_node_fk")
        .first()
    )
    if task is None:
        return {"task_id": task_id, "status": "task_not_found"}

    if task.status != Task.Status.PENDING:
        return {"task_id": task_id, "status": "already_dispatched"}

    adjacency = build_adjacency()

    travel_to_pickup = travel_times_to(task.origin_node_fk_id, adjacency)

    agent, pickup_eta = find_nearest_agent(task.origin_node_fk_id, travel_to_pickup)
    if agent is None:
        return {"task_id": task_id, "status": "no_agent_available"}

    travel_from_pickup = dijkstra(adjacency, task.origin_node_fk_id)
    delivery_eta = travel_from_pickup.get(task.destination_node_fk_id)

    try:
        assign_task_to_agent(task_id, agent.id, pickup_eta, delivery_eta)
    except DispatchError:
        return {"task_id": task_id, "status": "agent_unavailable"}

    return {
        "task_id": task_id,
        "agent_id": agent.id,
        "distance": pickup_eta,
        "pickup_eta_minutes": pickup_eta,
        "delivery_eta_minutes": delivery_eta,
        "status": "assigned",
    }
