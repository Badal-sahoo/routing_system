from django.db import transaction
from django.utils import timezone

from apps.agents.models import Agent

from .models import Task


class DispatchError(Exception):
    pass


def broadcast_task(task):
    from consumers.broadcast import send_fleet_event

    from .serializers import TaskSerializer

    send_fleet_event("task", {"task": TaskSerializer(task).data})


def assign_task_to_agent(task_id, agent_id, pickup_eta=None, delivery_eta=None):
    with transaction.atomic():
        agent = Agent.objects.select_for_update().get(pk=agent_id)
        if agent.status != Agent.Status.AVAILABLE:
            raise DispatchError(f"Agent {agent_id} is not available")

        task = Task.objects.select_for_update().get(pk=task_id)
        if task.status != Task.Status.PENDING:
            raise DispatchError(f"Task {task_id} is not pending")

        agent.status = Agent.Status.BUSY
        agent.save(update_fields=["status"])

        task.assigned_agent_fk = agent
        task.status = Task.Status.ASSIGNED
        task.pickup_eta_minutes = pickup_eta
        task.delivery_eta_minutes = delivery_eta
        task.save(
            update_fields=[
                "assigned_agent_fk",
                "status",
                "pickup_eta_minutes",
                "delivery_eta_minutes",
            ]
        )

    return task


def mark_delivery_started(task_id):
    with transaction.atomic():
        task = Task.objects.select_for_update().get(pk=task_id)
        if task.status != Task.Status.ASSIGNED:
            raise DispatchError(f"Task {task_id} is not waiting to start")

        task.status = Task.Status.IN_PROGRESS
        task.save(update_fields=["status"])

    return task


def complete_delivery(task_id):
    agent_id = (
        Task.objects.filter(pk=task_id)
        .values_list("assigned_agent_fk_id", flat=True)
        .first()
    )
    if agent_id is None:
        raise DispatchError(f"Task {task_id} has no rider to free")

    with transaction.atomic():
        agent = Agent.objects.select_for_update().get(pk=agent_id)
        task = Task.objects.select_for_update().get(pk=task_id)

        if task.status != Task.Status.IN_PROGRESS:
            raise DispatchError(f"Task {task_id} is not in progress")

        task.status = Task.Status.COMPLETED
        task.save(update_fields=["status"])

        agent.status = Agent.Status.AVAILABLE
        agent.current_node_fk_id = task.destination_node_fk_id
        agent.last_seen = timezone.now()
        agent.save(update_fields=["status", "current_node_fk", "last_seen"])

    return task, agent
