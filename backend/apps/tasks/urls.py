from rest_framework.routers import SimpleRouter

from .views import TaskViewSet

router = SimpleRouter()
router.register("tasks", TaskViewSet)

urlpatterns = router.urls
