from task_manager.celery import app

from .models import CeleryTask
from .tasks import send_email


# Отправка уведомления о создании задачи
def celery_created(instance):
    subject = 'Добавление задачи'
    message = 'Назначена новая задача \'%s\'. Планируемая дата выполнения: %s.' % \
              (instance.title, instance.due_date.strftime("%d.%m.%Y %H:%M"))

    send_email.delay(instance.id, subject, message, True)


# Отправка уведомления об изменении статуса задачи
def celery_status_updated(instance):
    subject = 'Изменение статуса задачи'
    message = 'Изменен статус задачи \'%s\'. Новый статус: %s.' % \
              (instance.title, instance.get_status_display())

    send_email.delay(instance.id, subject, message)


# Отправка уведомления об истечении срока выполнения задачи
def celery_expiration_scheduled(instance):
    task_tuple = (
        instance.id,
        'Срок выполнения задачи истек',
        'Срок выполнения задачи \'%s\' истек.' % instance.title,
        True
    )

    process_task = send_email.apply_async(args=task_tuple, eta=instance.due_date)

    try:
        celery = CeleryTask.objects.get(task__id=instance.id)
        celery.celery_id = process_task.task_id
    except CeleryTask.DoesNotExist:
        celery = CeleryTask.objects.create(
            task=instance,
            celery_id=process_task.task_id
        )
        celery.save()


# Удаление уведомления об истечении строка выполнения задачи
def celery_revoke(instance):
    try:
        celery = CeleryTask.objects.get(task__id=instance.id)
        app.control.revoke(celery.celery_id)
    except CeleryTask.DoesNotExist:
        pass
