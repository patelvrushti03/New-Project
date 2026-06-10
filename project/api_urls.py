from rest_framework.routers import DefaultRouter

from project.views import ContactModelViewSet, ProjectModelViewSet

router = DefaultRouter()
router.register("project", ProjectModelViewSet)
router.register("contact", ContactModelViewSet)

urlpatterns = router.urls
