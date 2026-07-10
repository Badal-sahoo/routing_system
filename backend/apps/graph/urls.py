from django.urls import path

from .views import AgentLocationView

urlpatterns = [
    path(
        "agents/<int:agent_id>/location/",
        AgentLocationView.as_view(),
        name="agent-location",
    ),
]
