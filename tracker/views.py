from django.utils import timezone

from rest_framework import viewsets
from rest_framework import permissions


from .models import Task, StatusChange, Notification, CeleryTask
from .serializers import TaskSerializer, StatusChangeSerializer, NotificationSerializer
from .rules import celery_created, celery_status_updated, celery_expiration_scheduled, celery_revoke


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task = serializer.save()

        # Отправить уведемление о создании задачи
        celery_created(task)

        # Запланировать отправку уведомления об истечении планируемого срока окончания при создании задачи с
        # незавершенным статусом и сроком окончания позднее текущего времени
        if task.status != 'fin' and task.due_date > timezone.localtime(timezone.now()):
            celery_expiration_scheduled(task)

    def perform_update(self, serializer):
        instance = self.get_object()
        task = serializer.save()

        # Создать новый объект изменения статуса, если предыдущий статус не равен новому
        if instance.status != task.status:
            status_change = StatusChange.objects.create(
                task=instance,
                prev_status=instance.status,
                curr_status=task.status,
                changer=self.request.user
            )
            status_change.save()

            # Отправить уведомление об изменении статуса
            celery_status_updated(task)

            # Запланировать отправку уведомления об истечении планируемого срока окончания при изменении статуса ранее
            # завершенной задачи
            if instance.status == 'fin':
                celery_revoke(task)
                celery_expiration_scheduled(task)

            # Уничтожить запланированное уведомление об истечении планируемого срока окончания задачи при ее завершении
            if task.status == 'fin':
                celery_revoke(task)

        # Изменить дату отправки уведомления при изменении планируемого срока окончания незавершенной задачи
        if timezone.localtime(instance.due_date) != task.due_date and task.status != 'fin':
            celery_revoke(task)
            celery_expiration_scheduled(task)

    def perform_destroy(self, instance):
        # Уничтожить запланированное уведомление об истечении планируемого срока окончания задачи при ее удалении
        celery_revoke(instance)
        celery = CeleryTask.objects.get(task__id=instance.id)
        celery.delete()

        instance.delete()


class StatusChangeViewSet(viewsets.ModelViewSet):
    queryset = StatusChange.objects.all()
    serializer_class = StatusChangeSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]
