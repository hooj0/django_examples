from django.db import models
from django.utils import timezone

from common.util import utils


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

    __str__ = lambda self: utils.object_to_string(self)


class TagsManager(models.Manager):
    def create_tag(self, tags, post_id):
        print(f"tags: {tags}, post_id: {post_id}")
        tag = self.create(tags=tags, post_id=post_id)
        print(f"tag: {tag}")
        return tag


class Tags(models.Model):
    tag_name = models.CharField(max_length=50, blank=False, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # objects = TagsManager()
    __str__ = lambda self: utils.object_to_string(self, 6)

    @classmethod
    def create_tags(cls, tags, post):
        tag = cls(tag_name=tags, post=post)
        print(f"tag: {tag}")
        return tag
