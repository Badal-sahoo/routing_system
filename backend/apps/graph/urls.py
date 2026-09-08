from rest_framework.routers import SimpleRouter

from .views import EdgeViewSet, NodeViewSet

router = SimpleRouter()
router.register("nodes", NodeViewSet)
router.register("edges", EdgeViewSet)

urlpatterns = router.urls
