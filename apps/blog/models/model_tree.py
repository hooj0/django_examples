from django.db import models

from common.util import utils


class Tree(models.Model):
    """
    递归关系
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/#recursive-relationships
    """
    node = models.CharField(max_length=50, blank=False, null=False)
    # 自引用
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children')

    __str__ = lambda self: utils.object_to_string(self)
