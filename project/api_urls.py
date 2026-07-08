from rest_framework.routers import DefaultRouter

from project.views import ProjectModelViewSet

router = DefaultRouter()
router.register("project", ProjectModelViewSet)

urlpatterns = router.urls
