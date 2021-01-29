import json
from datetime import datetime

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from rest_framework.test import force_authenticate
from rest_framework.test import APIClient

from tracker.models import Task, StatusChange, Notification
from tracker.views import TaskViewSet, StatusChangeViewSet, NotificationViewSet


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create(
            username='doer',
            password='qwerty123',
            email='test1@gmail.com',
            is_superuser=True,
            is_staff=True
        )
        self.user = User.objects.create(
            username='watcher',
            password='qwerty123',
            email='test2@gmail.com'
        )
        self.task = Task.objects.create(
            title='simple task',
            desc='simple description',
            doer=self.superuser,
            status='act',
            start_date=datetime(2021, 1, 29, 12, 0, 0, 0),
            end_date=datetime(2021, 1, 30, 17, 0, 0, 0),
            due_date=datetime(2021, 1, 30, 18, 0, 0, 0)
        )
        self.status = StatusChange.objects.create(
            task=self.task,
            changer=self.superuser,
            prev_status='act',
            curr_status='fin'
        )
        self.notification = Notification.objects.create(
            title='notification',
            task=self.task
        )

    def tearDown(self):
        self.superuser.delete()
        self.user.delete()
        self.task.delete()
        self.status.delete()
        self.notification.delete()

    def test_get_task_without_auth(self):
        request = self.factory.get('/api/tasks')
        response = TaskViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_get_task_user(self):
        request = self.factory.get('/api/tasks')
        force_authenticate(request, user=self.user)
        response = TaskViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.data['results'][0]['title'], 'simple task')
        self.assertEqual(response.status_code, 200)

    def test_post_task_user(self):
        data = json.dumps({
            "title": "test",
            "desc": "a task for unit testing",
            "doer": 1,
            "watchers": [],
            "status": "plan",
            "start_date": "2021-01-29T10:00:00+06:00",
            "end_date": "",
            "due_date": "2021-02-01T18:00:00+06:00"
        })
        client = APIClient()
        client.force_authenticate(user=self.superuser)
        response = client.post('/api/tasks', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results']['desc'], 'a task for unit testing')

    def test_get_status_change_without_auth(self):
        request = self.factory.get('/api/statuses')
        response = StatusChangeViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_get_status_change_user(self):
        request = self.factory.get('/api/statuses')
        force_authenticate(request, user=self.user)
        response = StatusChangeViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_get_status_change_superuser(self):
        request = self.factory.get('/api/statuses')
        force_authenticate(request, user=self.superuser)
        response = StatusChangeViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.data['results'][0]['prev_status'], 'act')
        self.assertEqual(response.status_code, 200)

    def test_get_notification_without_auth(self):
        request = self.factory.get('/api/notification')
        response = NotificationViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_get_notification_user(self):
        request = self.factory.get('/api/notification')
        force_authenticate(request, user=self.user)
        response = NotificationViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_get_notification_superuser(self):
        request = self.factory.get('/api/notification')
        force_authenticate(request, user=self.superuser)
        response = NotificationViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.data['results'][0]['title'], 'notification')
        self.assertEqual(response.status_code, 200)
