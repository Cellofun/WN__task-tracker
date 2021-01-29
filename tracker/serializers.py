from rest_framework import serializers

from .models import Task, StatusChange, Notification


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'desc', 'doer', 'watchers', 'status', 'start_date', 'end_date', 'due_date']


class StatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusChange
        fields = ['id', 'task', 'prev_status', 'curr_status', 'changer']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'task', 'title', 'watchers']
