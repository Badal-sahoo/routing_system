from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "origin_node_fk",
        "destination_node_fk",
        "status",
        "assigned_agent_fk",
        "created_at",
    ]
    list_filter = ["status"]
