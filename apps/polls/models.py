import datetime

from django.db import models
from django.utils import timezone

from common.util import utils


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    published_date = models.DateTimeField('date published')

    __str__ = lambda self: self.question_text

    def was_published_recently(self):
        return self.published_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return utils.object_to_string(self)