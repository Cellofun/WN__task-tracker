from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase

from tracker.models import Task, StatusChange, Notification


class TestModels(TestCase):

    def setUp(self):
        self.doer = User.objects.create(
            username='doer',
            password='qwerty123',
            email='test1@gmail.com'
        )
        self.task = Task.objects.create(
            title='simple task',
            desc='simple description',
            doer=self.doer,
            status='act',
            start_date=datetime(2021, 1, 29, 12, 0, 0, 0),
            end_date=datetime(2021, 1, 30, 17, 0, 0, 0),
            due_date=datetime(2021, 1, 30, 18, 0, 0, 0)
        )
        self.status = StatusChange.objects.create(
            task=self.task,
            changer=self.doer,
            prev_status='act',
            curr_status='fin'
        )
        self.notification = Notification.objects.create(
            title='notification',
            task=self.task
        )
        users = User.objects.all()
        self.notification.watchers.set(users)
        self.task.watchers.set(users)

    def tearDown(self):
        self.doer.delete()
        self.task.delete()
        self.status.delete()
        self.notification.delete()

    def test_task_content(self):
        task = Task.objects.get(title='simple task')

        start_date = pytz.timezone('Asia/Almaty').localize(self.task.start_date)
        end_date = pytz.timezone('Asia/Almaty').localize(self.task.end_date)
        due_date = pytz.timezone('Asia/Almaty').localize(self.task.due_date)

        desc = f'{task.desc}'
        doer = f'{task.doer.username}'
        status = f'{task.status}'
        start_date = f'{start_date}'
        end_date = f'{end_date}'
        due_date = f'{due_date}'

        self.assertEquals(desc, 'simple description')
        self.assertEquals(doer, 'doer')
        self.assertEquals(status, 'act')
        self.assertEquals(start_date, '2021-01-29 12:00:00+06:00')
        self.assertEquals(end_date, '2021-01-30 17:00:00+06:00')
        self.assertEquals(due_date, '2021-01-30 18:00:00+06:00')

    def test_status_change_content(self):
        status_change = StatusChange.objects.get(task=self.task)

        task_title = f'{status_change.task.title}'
        changer = f'{status_change.changer.username}'
        prev_status = f'{status_change.prev_status}'
        curr_status = f'{status_change.curr_status}'

        self.assertEquals(task_title, 'simple task')
        self.assertEquals(changer, 'doer')
        self.assertEquals(prev_status, 'act')
        self.assertEquals(curr_status, 'fin')

    def test_notification_content(self):
        notification = Notification.objects.get(task=self.task)

        task_title = f'{notification.task.title}'
        title = f'{notification.title}'

        self.assertEquals(task_title, 'simple task')
        self.assertEquals(title, 'notification')
