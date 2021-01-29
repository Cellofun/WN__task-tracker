from django.core.mail import send_mail

from decouple import config
from celery import shared_task

from .models import Task, Notification


@shared_task
def send_email(id, subject, message, doer=False):
    task = Task.objects.get(id=id)
    notification = Notification.objects.create(
        title=message,
        task=task
    )

    users = task.watchers.all()
    notification.watchers.set(users)

    recipient_list = []
    if doer:
        recipient_list.append(task.doer.email)
    else:
        [recipient_list.append(watcher.email) for watcher in users]

    send_mail(
        subject,
        message,
        config('EMAIL_HOST_USER'),
        recipient_list,
        fail_silently=False
    )
