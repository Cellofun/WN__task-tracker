from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, StatusChangeViewSet, NotificationViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')
router.register('statuses', StatusChangeViewSet, basename='statuses')
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = router.urls
