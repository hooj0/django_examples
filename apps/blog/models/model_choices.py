from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _

from common.util import utils


class Choices(models.Model):
    """
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/#choices
    """
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

    class Fruit(models.IntegerChoices):
        APPLE = 1, "苹果"
        PEACH = 2, "桃子"
        ORANGE = 3, "橘子"

    class CategoryType(models.TextChoices):
        """
        分类类型
        """
        KP = 'K', '科普'
        SW = 'S', '散文'
        XS = 'X', '小说'
        YX = 'Y', '游戏'

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

        # def __str__(self):
        #     return self.name

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
    fruit = models.IntegerField(choices=Fruit, default=Fruit.APPLE)
    medal_type = models.CharField(max_length=10, choices=MedalType.choices, verbose_name='MedalType', default=MedalType.BRONZE)
    place = models.IntegerField(choices=Place.choices, verbose_name='Place', default=Place.THIRD)

    __str__ = lambda self: utils.object_to_string(self)
