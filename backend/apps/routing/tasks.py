from celery import shared_task
from django.conf import settings

from apps.agents.services import broadcast_agent, record_location
from apps.tasks.models import Task
from apps.tasks.services import (
    DispatchError,
    broadcast_task,
    complete_delivery,
    mark_delivery_started,
)

from .services import delivery_route, dispatch_task_to_nearest_agent


@shared_task
def dispatch_task(task_id):
    result = dispatch_task_to_nearest_agent(task_id)

    if result["status"] == "assigned":
        task = Task.objects.get(pk=task_id)
        broadcast_task(task)
        broadcast_agent(task.assigned_agent_fk)

        begin_delivery.apply_async(
            (task_id,), countdown=settings.DELIVERY_START_DELAY_SECONDS
        )

    return result


@shared_task
def begin_delivery(task_id):
    task = (
        Task.objects.select_related("assigned_agent_fk")
        .filter(pk=task_id)
        .first()
    )
    if task is None or task.assigned_agent_fk is None:
        return {"task_id": task_id, "status": "task_not_found"}

    agent = task.assigned_agent_fk
    if agent.current_node_fk_id is None:
        return {"task_id": task_id, "status": "rider_has_no_position"}

    waypoints = delivery_route(
        agent.current_node_fk_id, task.origin_node_fk_id, task.destination_node_fk_id
    )
    if not waypoints:
        return {"task_id": task_id, "status": "no_route"}

    try:
        task = mark_delivery_started(task_id)
    except DispatchError:
        return {"task_id": task_id, "status": "not_startable"}

    broadcast_task(task)
    advance_delivery.delay(task_id, waypoints, 0)

    return {"task_id": task_id, "status": "started", "waypoints": len(waypoints)}


@shared_task
def advance_delivery(task_id, waypoints, index):
    task = (
        Task.objects.filter(pk=task_id)
        .only("id", "status", "assigned_agent_fk")
        .first()
    )
    if task is None or task.status != Task.Status.IN_PROGRESS:
        return {"task_id": task_id, "status": "abandoned"}

    latitude, longitude = waypoints[index]
    record_location(task.assigned_agent_fk_id, latitude, longitude)

    if index + 1 < len(waypoints):
        advance_delivery.apply_async(
            (task_id, waypoints, index + 1),
            countdown=settings.DELIVERY_TICK_SECONDS,
        )
        return {"task_id": task_id, "status": "moving", "step": index + 1}

    try:
        completed_task, agent = complete_delivery(task_id)
    except DispatchError:
        return {"task_id": task_id, "status": "already_finished"}

    broadcast_task(completed_task)
    broadcast_agent(agent)

    return {"task_id": task_id, "status": "completed", "agent_id": agent.id}
