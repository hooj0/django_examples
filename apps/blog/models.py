from datetime import timezone
from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)
    content = models.TextField(blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='media/images/')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.BooleanField(default=False, db_comment='Published or not')

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    __str__ = lambda self: self.title

class Tags(models.Model):
    tag_name = models.CharField(max_length=50, blank=False, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    __str__ = lambda self: self.tag_name