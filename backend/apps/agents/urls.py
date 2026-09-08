from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import AgentLocationView, AgentViewSet

router = SimpleRouter()
router.register("agents", AgentViewSet)

urlpatterns = [
    path(
        "agents/<int:agent_id>/location/",
        AgentLocationView.as_view(),
        name="agent-location",
    ),
] + router.urls
