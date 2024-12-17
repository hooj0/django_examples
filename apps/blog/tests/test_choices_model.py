import datetime
from enum import Enum

from django.db.models.enums import TextChoices
from django.test import TestCase

from apps.blog.models import Choices
from django.db import models, reset_queries
from apps.blog.tests.tests import BasedTestCase, output, output_sql, sql_decorator


class ChoicesModelTest(BasedTestCase):
    """
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/#choices
    """
    def setUp(self):
        super().setUp()

    def test_level_choices(self):
        print(Choices.Level)    # <enum 'Level'>
        print(Choices.Level.choices) # [('FR', '大一新生'), ('SO', '大二'), ('JR', '初级'), ('SR', '高级'), ('GR', '毕业生')]
        print(Choices.Level.values)  # ['FR', 'SO', 'JR', 'SR', 'GR']
        print(Choices.Level.names)   # ['FRESHMAN', 'SOPHOMORE', 'JUNIOR', 'SENIOR', 'GRADUATE']
        print(Choices.Level.labels)  # ['大一新生', '大二', '初级', '高级', '毕业生']

        print(Choices.Level.FRESHMAN)   # <Choices.Level: FR>
        print(Choices.Level.FRESHMAN.__dict__)   # {'_value_': 'FR', '_name_': 'FRESHMAN', '__objclass__': <enum 'Level'>, '_sort_order_': 0, '_label_': '大一新生'}
        print(Choices.Level.__dict__)
        print(Choices.Level.__members__)   # {'FRESHMAN': Choices.Level.FRESHMAN, 'SOPHOMORE': Choices.Level.SOPHOMORE, 'JUNIOR': Choices.Level.JUNIOR, 'SENIOR': Choices.Level.SENIOR, 'GRADUATE': Choices.Level.GRADUATE}
        print(dict(Choices.Level.choices)) # {'FR': '大一新生', 'SO': '大二', 'JR': '初级', 'SR': '高级', 'GR': '毕业生'}
        print(Choices.Level.FRESHMAN.value) # FR
        print(Choices.Level.FRESHMAN.label) # 大一新生
        print(Choices.Level.FRESHMAN.name)  # FRESHMAN

        print(Choices.Level['FRESHMAN'] == Choices.Level.FRESHMAN)
        print(dict(Choices.Level.choices))

        for value, label in Choices.Level.choices:
            print(value)

    def test_enum(self):
        class Type(Enum):
            RED = (1, "Red", True)
            GREEN = (2, "Green", False)
            BLUE = (3, "Blue", True)

            def __new__(cls, value, desc, bool):
                data = object.__new__(cls)
                data._value_ = value
                data.desc = desc
                data.bool = bool
                return data

            @staticmethod
            def values():
                return [Type.RED, Type.GREEN, Type.BLUE]

            @staticmethod
            def valueOf(value):
                # for type in Type:
                #     if type.name == value:
                #         return type
                # return [x for x in Type.values() if x.name == value][0]
                return next((type for type in Type if type.name == value), None)

        print(Type)
        print(Type.RED)
        print(Type.RED.__dict__) # {'_value_': 1, 'desc': 'Red', 'bool': True, '_name_': 'RED', '__objclass__': <enum 'Type'>, '_sort_order_': 0}
        print(Type.RED.name)
        print(Type.RED.value)
        print(Type.RED.desc)
        print(Type.RED.bool)
        print(Type.valueOf("RED").value)
        print(Type.values())
        print(list(Type))   # [<Type.RED: 1>, <Type.GREEN: 2>, <Type.BLUE: 3>]
        print(Type.__members__.values()) # dict_values([<Type.RED: 1>, <Type.GREEN: 2>, <Type.BLUE: 3>])

    def test_meta_choices(self):
        class MoonLandings(datetime.date, models.Choices):
            APOLLO_11 = 1969, 7, 20, "Apollo 11 (Eagle)"
            APOLLO_12 = 1969, 11, 19, "Apollo 12 (Intrepid)"
            APOLLO_14 = 1971, 2, 5, "Apollo 14 (Antares)"
            APOLLO_15 = 1971, 7, 30, "Apollo 15 (Falcon)"
            APOLLO_16 = 1972, 4, 21, "Apollo 16 (Orion)"
            APOLLO_17 = 1972, 12, 11, "Apollo 17 (Challenger)"

        print(MoonLandings.choices)
        print(MoonLandings.values)
        print(MoonLandings.labels)
        print(MoonLandings.names)
        print(MoonLandings.APOLLO_11.label)

        class OpenMode(int, models.Choices):
            a = 1, "read a b"
            b = 2, "write c d"

        print("-------------------------")
        print(OpenMode.choices)
        print(OpenMode.a)
        print(OpenMode.a.name)
        print(OpenMode.a.label)
        print(OpenMode.a.value)

        class SimpleMeta:
            def __init__(self, param1=None, param2=None):
                self.param1 = param1
                self.param2 = param2

            __str__ = lambda self: f"{self.param1} - {self.param2}"

        class OpenState(SimpleMeta, models.Choices):
            a = SimpleMeta(100, "X"), "read a b"
            b = SimpleMeta(200, "Y"), "write c d"

        print("-------------------------")
        print(OpenState.choices)
        print(OpenState.a.label)
        print(OpenState.a.value)
        print(OpenState.a)
        print(OpenState.a.param1)
        print(OpenState.a.param2)

    def test_simple_choices(self):
        class Priority(models.Choices):
            LOW = 'L', 'Low'
            MEDIUM = 'M', 'Medium'
            HIGH = 'H', 'High'

        print(Priority)
        print(Priority.choices) # [(('L',), 'Low'), (('M',), 'Medium'), (('H',), 'High')
        print(Priority.names)   # ['LOW', 'MEDIUM', 'HIGH']
        print(Priority.values)  # [('L',), ('M',), ('H',)]
        print(Priority.labels)  # ['Low', 'Medium', 'High']
        print(Priority['LOW'])
        print(vars(Priority['LOW']))
        print("------------------------------------")

        class Priority2(models.Choices):
            LOW = 'L', 'Low', 1
            MEDIUM = 'M', 'Medium', 2
            HIGH = 'H', 'High', 3

            def desc(self):
                return self.value[1]

            def value2(self):
                return self.value[0]

            def index(self):
                return self.value[2]

        print(Priority2)
        print(Priority2.choices) # [(('L', 'Low', 1), 'Low'), (('M', 'Medium', 2), 'Medium'), (('H', 'High', 3), 'High')]
        print(Priority2.names)   # ['LOW', 'MEDIUM', 'HIGH']
        print(Priority2.values)  # [('L', 'Low', 1), ('M', 'Medium', 2), ('H', 'High', 3)]
        print(Priority2.labels)  # ['Low', 'Medium', 'High']
        print(Priority2['LOW'].label)
        print(Priority2['LOW'].name)
        print(Priority2['LOW'].value)
        print(Priority2['LOW'].desc())
        print(Priority2['LOW'].index())

    def test_choices_model(self):
        data = Choices.objects.create(place=Choices.Place.FIRST, priority=Choices.Priority.HIGH, region=Choices.Region.HB, suit=Choices.Suit.HEART)
        output_sql(data)
        output(Choices.objects.all())

        data.answer = Choices.Answer.YES
        data.language = Choices.LanguageChoice.EN
        # data.language = Choices.LanguageChoice.EN.name
        data.gender = Choices.GENDER_CHOICES[1]
        data.category_type = Choices.CategoryType.KP
        data.level = Choices.Level.SENIOR
        data.medal_type = Choices.MedalType.SILVER
        output_sql(data.save())

        output(Choices.objects.all())


    @sql_decorator
    def test_choices_query(self):
        self.test_choices_model()

        data = Choices.objects.filter(answer=Choices.Answer.YES).first()

        print(data.answer)   # 1
        print(data.priority) # H
        print(data.language) # LanguageChoice.EN
        print(data.gender)   # ('F', 'Female')
        print(data.get_answer_display()) # Yes
        print(data.get_fruit_display())  # 苹果
        print(data.get_suit_display())      # Heart
        print(data.get_language_display())  # LanguageChoice.EN

        print(data.answer == Choices.Answer.YES)        # True
        print(data.priority == Choices.Priority.HIGH)   # True

        print(Choices.LanguageChoice.EN.name)   # EN
        print(Choices.LanguageChoice.EN.value)  # English
        print(Choices.LanguageChoice.EN.__str__()) # LanguageChoice.EN
        print(data.language == Choices.LanguageChoice.EN) # True
        print(data.language == Choices.LanguageChoice.EN.name) # False
        print(data.language == Choices.LanguageChoice.EN.__str__()) # True
        print(data.gender == Choices.GENDER_CHOICES[1]) # False

    def test_choices_biz(self):

        class BaseTextChoices(models.TextChoices):
            @classmethod
            def value_of(cls, value):
                return next(item for item in cls if item.value == value)

            @classmethod
            def label_of(cls, label):
                return next(item for item in cls if item.label == label)

            @classmethod
            def name_of(cls, name):
                try:
                    return cls[name]
                except:
                    return None

            def get_dict(self):
                return {'name': self.name, 'label': self.label, 'value': self.value}

            @classmethod
            def get_choices(cls):
                return [(item.name, item.label) for item in cls]

            @classmethod
            def get_choices_dict(cls):
                return {item.name: item.label for item in cls}

            @classmethod
            def get_choices_list(cls):
                return list(map(lambda item: item.get_dict(), cls))

            def __str__(self):
                return f'{self.name} {self.value} - {self.label}'

        class Status(BaseTextChoices):
            ACTIVE = 'A', '活动'
            INACTIVE = 'I', '未激活'
            DELETED = 'D', '删除'

        print(Status['ACTIVE'])          # ACTIVE A - 活动
        print(Status.name_of('ACTIVE'))  # ACTIVE A - 活动
        print(Status.name_of('ACTIVE2')) # None
        print(Status.value_of('D'))      # DELETED D - 删除
        print(Status.label_of('未激活'))  # INACTIVE I - 未激活
        print(Status['ACTIVE'].__dict__)    # {'_value_': 'A', '_name_': 'ACTIVE', '__objclass__': <enum 'Status'>, '_sort_order_': 0, '_label_': '活动'}
        print(Status['ACTIVE'].get_dict())  # {'name': 'ACTIVE', 'label': '活动', 'value': 'A'}
        print(Status.get_choices())         # [('ACTIVE', '活动'), ('INACTIVE', '未激活'), ('DELETED', '删除')]
        print(Status['ACTIVE'].get_choices_dict())  # {'ACTIVE': '活动', 'INACTIVE': '未激活', 'DELETED': '删除'}
        print(Status.get_choices_list())            # [{'name': 'ACTIVE', 'label': '活动', 'value': 'A'}, {'name': 'INACTIVE', 'label': '未激活', 'value': 'I'}, {'name': 'DELETED', 'label': '删除', 'value': 'D'}]
        print(Status.choices)                       # [('A', '活动'), ('I', '未激活'), ('D', '删除')]
