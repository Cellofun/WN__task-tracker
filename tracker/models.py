from django.db import models
from django.contrib.auth.models import User


PLANNED = 'plan'
ACTIVE = 'act'
CONTROLLED = 'cont'
FINISHED = 'fin'
STATUS_CHOICES = [
    (PLANNED, 'Планируется'),
    (ACTIVE, 'Активная'),
    (CONTROLLED, 'Контроль'),
    (FINISHED, 'Завершена'),
]


class Task(models.Model):
    title = models.CharField(
        max_length=50
    )
    desc = models.TextField(
        blank=True
    )
    doer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doer'
    )
    watchers = models.ManyToManyField(
        User,
        blank=True,
        related_name='watchers'
    )
    status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICES
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        null=True,
        blank=True
    )
    due_date = models.DateTimeField()
    celery = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return '%s: %s' % (self.title, self.due_date)


class StatusChange(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='status_task'
    )
    changer = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )
    prev_status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICES
    )
    curr_status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICES
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Изменение статуса задачи'
        verbose_name_plural = 'Изменения статуса задач'

    def __str__(self):
        return '%s: %s' % (self.task.title, self.get_curr_status_display())


class Notification(models.Model):
    title = models.CharField(
        max_length=255
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='notification_task'
    )
    watchers = models.ManyToManyField(
        User,
        related_name='notification_watchers'
    )

    def __str__(self):
        return self.task.title

    class Meta:
        ordering = ['-id']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


# Модель, предназначенная для планирования отправки уведомлений
class CeleryTask(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )
    celery_id = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.task.title

    class Meta:
        ordering = ['-id']
        verbose_name = 'Задача Celery'
        verbose_name_plural = 'Задачи Celery'
