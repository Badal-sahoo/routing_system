from django.contrib import admin

from .models import Edge, Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["id", "label", "lat", "lng"]
    search_fields = ["label"]


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ["id", "from_node_fk", "to_node_fk", "weight", "is_bidirectional"]
    list_filter = ["is_bidirectional"]
