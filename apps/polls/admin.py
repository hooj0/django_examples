from django.contrib import admin

from apps.polls.models import Question

# Register your models here.
admin.site.register(Question)