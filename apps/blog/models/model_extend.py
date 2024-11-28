from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()

    def __str__(self):
        return self.name

class Student(Person):
    student_id = models.CharField(max_length=20)
    # 使用 parent_link=True 创建一个 OneToOneField 到父类 Person
    person_ptr = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True  # 设置为主键
    )

    def __str__(self):
        return f"{self.name} - 学生ID: {self.student_id}"