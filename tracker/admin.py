from django.contrib import admin

from .models import Task, StatusChange, Notification


admin.site.register(Task)
admin.site.register(StatusChange)
admin.site.register(Notification)
