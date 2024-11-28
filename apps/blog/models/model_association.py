from django.contrib.auth.models import User
from django.db import models
from faker import Faker

from common.util import utils

faker = Faker()


class Studio(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=False)

    __str__ = lambda self: utils.object_to_string(self)

class Author(models.Model):
    name = models.CharField("作者名称", max_length=50, blank=False, null=False)
    age = models.IntegerField("年龄", default=18)
    # related_name 参数用于指定反向查询时使用的字段名，默认为当前模型类名Author小写
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户基本信息", related_name="author_of", null=True)
    studio = models.OneToOneField(Studio, on_delete=models.CASCADE, verbose_name="工作室", null=True)

    __str__ = lambda self: utils.object_to_string(self)

    @staticmethod
    def mock_data():
        return Author(name=f"Mock Author {faker.user_name()}", age=faker.pyint(min_value=18, max_value=60))


class Book(models.Model):
    title = models.CharField("书名", max_length=50, blank=False, null=False)
    price = models.DecimalField("价格", max_digits=10, decimal_places=2, null=True)
    # related_name 参数用于指定反向查询时使用的字段名，默认为模型类名小写加_set
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="the related book", null=True, related_name="books", related_query_name="book")

    __str__ = lambda self: utils.object_to_string(self)

    @staticmethod
    def mock_data():
        return Book(title=f"Mock Book {faker.name()}", price=faker.pydecimal(left_digits=3, right_digits=2))


