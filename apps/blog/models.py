from datetime import datetime
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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


class Choices(models.Model):
    class Level(models.TextChoices):
        FRESHMAN = "FR", _("大一新生")
        SOPHOMORE = "SO", _("大二")
        JUNIOR = "JR", _("初级")
        SENIOR = "SR", _("高级")
        GRADUATE = "GR", _("毕业生")

    class Region(models.TextChoices):
        HB = "华北"
        HN = "华南"
        HD = "华东"
        HZ = "华中"

    class Suit(models.IntegerChoices):
        DIAMOND = 1
        SPADE = 2
        HEART = 3
        CLUB = 4

    class Answer(models.IntegerChoices):
        NO = 0, _("No")
        YES = 1, _("Yes")

        __empty__ = _("(Unknown)")

    class CategoryType(models.TextChoices):
        """
        分类类型
        """
        KP = 'KP', '科普'
        SW = 'SW', '散文'
        XS = 'XS', '小说'
        YX = 'YX', '游戏'

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    class LanguageChoice(Enum):   # 枚举类的子类 实际上Enum是一个元类 继承自所有类的元类 type
        DE = "German"
        EN = "English"
        CN = "Chinese"
        ES = "Spanish"

    class Priority(str, models.Choices):
        LOW = 'L', 'Low'
        MEDIUM = 'M', 'Medium'
        HIGH = 'H', 'High'

    MedalType = models.TextChoices("MedalType", "GOLD SILVER BRONZE")
    Place = models.IntegerChoices("Place", "FIRST SECOND THIRD")

    priority = models.CharField(max_length=5, choices=Priority.choices, default=Priority.LOW)
    language = models.CharField(max_length=2, choices=[(tag.name, tag.value) for tag in LanguageChoice], default=LanguageChoice.CN)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    category_type = models.CharField(max_length=2, choices=CategoryType, default=CategoryType.KP)
    level = models.CharField(max_length=2, choices=Level, db_comment='level', help_text='Level with no default value')
    region = models.CharField(max_length=2, choices=Region, default=Region.HB, help_text='Region with no default value')
    answer = models.IntegerField(choices=Answer, verbose_name='answer', default=Answer.NO)
    suit = models.IntegerField(choices=Suit, default=Suit.CLUB)
    medal_type = models.CharField(max_length=10, choices=MedalType.choices, verbose_name='MedalType', default=MedalType.BRONZE)
    place = models.IntegerField(choices=Place.choices, verbose_name='Place', default=Place.THIRD)

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
    price = models.DecimalField("价格", max_digits=10, decimal_places=2, null=True)

    __str__ = lambda self: utils.object_to_string(self)


class Author(models.Model):
    name = models.CharField("作者名称", max_length=50, blank=False, null=False)
    age = models.IntegerField("年龄", default=18)
    books = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="the related book")
    tags = models.ManyToManyField(Tags, verbose_name="list of sites", related_name="authors")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="user", related_name="user_info", null=True)

    __str__ = lambda self: utils.object_to_string(self)
