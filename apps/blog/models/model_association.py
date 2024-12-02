from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from faker import Faker

from common.util import utils

faker = Faker()


class Studio(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=False)

    __str__ = lambda self: utils.object_to_string(self)


"""
    一对一关联
"""
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


"""
    多对一关联
"""
class Book(models.Model):
    title = models.CharField("书名", max_length=50, blank=False, null=False)
    """
    max_digits
        数字中允许的最大位数。请注意，这个数字必须大于或等于 decimal_places。
    decimal_places
        与数字一起存储的小数位数。
    例如，要存储最高为 999.99 的数字，精度为小数点后 2 位，你可以使用：
    models.DecimalField(..., max_digits=5, decimal_places=2)
    """
    price = models.DecimalField("价格", max_digits=10, decimal_places=2, null=True)
    # related_name 参数用于指定反向查询时使用的字段名，默认为模型类名小写加_set
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="the related book", null=True, related_name="books", related_query_name="book")

    __str__ = lambda self: utils.object_to_string(self)

    @staticmethod
    def mock_data():
        return Book(title=f"Mock Book {faker.name()}", price=faker.pydecimal(left_digits=3, right_digits=2))


"""
    多对多关联
"""
class Publisher(models.Model):
    publisher_name = models.CharField(max_length=50, blank=False, null=False)
    """
    隐式模式，默认设置
    生成以下字段：
        id ：关系的主键。
        <containing_model>_id ：声明 ManyToManyField 的模型的 id。
        <other_model>_id ：ManyToManyField 指向的模型的 id。
        
    # 多对多只需要在 两个关联模型的一个中设置多对多关系，不需要两个都设置
    # Django 会自动生成一个表来管理多对多关系
    """
    books = models.ManyToManyField(Book)

    __str__ = lambda self: utils.object_to_string(self)

    @staticmethod
    def mock_data():
        return Publisher(publisher_name=f"Mock Publisher {faker.name()}")


class Reader(models.Model):
    reader_name = models.CharField(max_length=50, blank=False, null=False)
    """
    显示模式，中间表模式
    # to = 字符串，指定关联的模型类，也可以指定关联的模型类名（当依赖的模型在当前模型下方，编译不会出错）
    # through 显示设置/自定义中间模型指连接两个多对多关联模型类的中间表
    # through_fields 只有自定义的中间模型时才会使用，当中间模型外键存在相同类型时，需要决定使用中间模型的哪些字段来自动建立多对多的关系
    """
    books = models.ManyToManyField('Book', through='Club', through_fields=('reader', 'book'))

    __str__ = lambda self: utils.object_to_string(self)


class Club(models.Model):
    """
    读书会
        # through_fields=('reader', 'book') 显式地为多对多关系中涉及的中间模型指定外键
        # 存在两个相同 外键 Book，如果不设置会出错
    """
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    recommended = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="推荐一本书", related_name="club_recommended", null=True)

    borrow_date = models.DateField(default=timezone.now)
    __str__ = lambda self: utils.object_to_string(self)


class Employee(models.Model):
    name = models.CharField(max_length=100)
    """
    # 自关联的 ManyToManyField
    # 注意: 默认情况下, 中间表的名字是 'appname_employee_teams'
        # (这里 'appname' 是你的应用名, 'employee' 是模型的小写名字, 'teams' 是 ManyToManyField 的名字),
        # 并且包含两个字段: 'from_employee_id' 和 'to_employee_id'.
        https://lxblog.com/qianwen/share?shareId=637bd1a2-4767-465e-a673-731a0e64a69d
        
    # 生成：
        id ：关系的主键。
        from_<model>_id ：指向模型的实例（即源实例）的 id
        to_<model>_id ：关系所指向的实例（即目标模型实例）的 id
    # symmetrical=False 关系不对称，默认为对称
        将 A 添加为 B 的子集，不会自动将 B 添加为 A 子集
    # db_table 要创建的用于存储多对多数据的中间表的名称，不设置将默认生成
    # db_constraint 控制外键约束，默认 True 需要约束（同时传递 db_constraint 和 through 会引发错误）
    # swappable=False  确保多对多这个字段关联的模型‘settings.AUTH_USER_MODEL’不能被替换
        # settings.py
        AUTH_USER_MODEL = 'myapp.CustomUser'
    """
    teams = models.ManyToManyField('self', db_table='employee_teams')

    __str__ = lambda self: utils.object_to_string(self)
