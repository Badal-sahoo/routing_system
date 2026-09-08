from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "status", "current_node_fk", "last_seen"]
    list_filter = ["status"]
    search_fields = ["name"]
