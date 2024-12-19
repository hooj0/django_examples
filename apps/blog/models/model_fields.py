from django.db import models
from django.db.models.functions import Concat
from django.utils import timezone

from apps.blog.models.model_crud import Post
from common.util import utils


class Comment(models.Model):
    """
    模型字段和字段属性参考
       https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/
   """
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
    json = models.JSONField(verbose_name="JSON数据", default=dict, null=True)
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
