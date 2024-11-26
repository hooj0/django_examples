from django.db import models
from django.db.models.functions import Concat
from django.utils import timezone

from common.util import utils


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

class Category(models.Model):
    CATEGORY_CHOICES = [
        ("KP", "科普"),
        ("SW", "散文"),
        ("XS", "小说"),
        ("YX", "游戏"),
    ]

    @staticmethod
    def get_currencies():
        return {i: i for i in Category.CATEGORY_CHOICES}

    class CategoryType(models.TextChoices):
        KP = 'KP', '科普'
        SW = 'SW', '散文'
        XS = 'XS', '小说'
        YX = 'YX', '游戏'

    category_name = models.CharField(max_length=50, blank=False, null=False, choices=CATEGORY_CHOICES, db_comment='Category name')
    category_type = models.CharField(max_length=50, blank=False, null=False, choices=get_currencies, default=CategoryType.KP)
    category_text = models.CharField(max_length=50, blank=False, null=False, choices=CATEGORY_CHOICES, verbose_name='Category text')
    created_date = models.DateTimeField(auto_now_add=True, editable=False)

    def is_upperclass(self):
        return self.category_text in {
            self.CategoryType.KP,
            self.CategoryType.SW,
        }

    __str__ = lambda self: utils.object_to_string(self)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True)
    pub_time = models.TimeField(default=timezone.now)

    status = models.BooleanField(default=False, db_comment='Published or not')
    user = models.CharField(max_length=50, blank=False, null=True)
    content = models.TextField(blank=False, null=True)

    rate = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    interval = models.DurationField(help_text='Interval between comments', blank=True, null=True)
    email = models.EmailField("邮箱", help_text="邮箱地址", max_length=50, default=None)
    photo = models.ImageField(upload_to='media/images/', db_comment="头像", blank=True)
    file = models.FileField(upload_to='media/files/', verbose_name="文件", db_comment="文件", blank=True)
    file_size = models.BigIntegerField(db_comment="文件大小", default=0)
    file_path = models.FilePathField(path='media/files/', db_comment="文件路径", blank=True)

    stars = models.FloatField(db_comment="评分", verbose_name="评分星星", help_text="打分", null=True)
    ip_address = models.GenericIPAddressField(db_comment="IP地址", default="127.0.0.1")

    size = models.IntegerField(db_comment="评论长度", db_column="comment_length", null=True)
    json = models.JSONField(verbose_name="JSON数据", default=dict)
    url_param = models.SlugField(verbose_name="URL路径参数", null=True)
    uri = models.URLField(verbose_name="URL地址", blank=True)
    uuid = models.UUIDField(verbose_name="UUID", editable=False, unique=True, null=True)

    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)

    # 使用GeneratedField定义full_name字段
    full_name = models.GeneratedField(
        expression=Concat("first_name", models.Value(" "), "last_name"),
        output_field=models.CharField(max_length=511),
        db_persist=True
    )

    __str__ = lambda self: utils.object_to_string(self)

class Book(models.Model):
    title = models.CharField("书名", max_length=50, blank=False, null=False)

    __str__ = lambda self: utils.object_to_string(self)

class Author(models.Model):
    name = models.CharField("作者名称", max_length=50, blank=False, null=False)
    books = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="the related book")
    tags = models.ManyToManyField(Tags, verbose_name="list of sites", related_name="authors")
    category = models.OneToOneField(Category, on_delete=models.CASCADE, verbose_name="related place", related_name="author")

    __str__ = lambda self: utils.object_to_string(self)
