from django.contrib.auth.models import User
from django.db import models

from common.util import utils


class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()

    __str__ = lambda self: utils.object_to_string(self)

"""
    多表继承：一对一，显示设置 parent_link=True
"""
class Student(Person):
    student_id = models.CharField(max_length=20)

    # 使用 parent_link=True 创建一个 OneToOneField 到父类 Person
    # 在大多数情况下，你不需要手动定义 parent_link，因为 Django 在检测到多表继承时会自动为你创建这个字段
    person_ptr = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        parent_link=True,
        # 显示设置 person_ptr 属性名称
        # related_name='student_of',
        primary_key=True  # 设置为主键
    )

    def __str__(self):
        return utils.object_to_string(self)

"""
    多表继承 - 一对一，不设置parent_link
"""
class Teacher(Person):
    salary = models.IntegerField()
    # 在大多数情况下，你不需要手动定义 parent_link，因为 Django 在检测到多表继承时会自动为你创建这个字段

    def __str__(self):
        return utils.object_to_string(self)

"""
    多表继承 - 多对多
"""
class Project(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    __str__ = lambda self: utils.object_to_string(self)

class WebProject(Project):
    url = models.URLField()
    administrators = models.ManyToManyField(Person, related_name='web_projects')

    def __str__(self):
        return super().__str__() + "- web project"

class MobileProject(Project):
    device = models.CharField(max_length=20)
    developers = models.ManyToManyField(Person, related_name='mobile_projects')

    def __str__(self):
        return super().__str__() + "- mobile project"

class JavaWebProject(WebProject):
    framework = models.CharField(max_length=20)

    def __str__(self):
        return super().__str__() + "- java web project"