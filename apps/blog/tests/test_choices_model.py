import datetime
from enum import Enum

from django.test import TestCase

from apps.blog.models import Choices
from django.db import models
from apps.blog.tests.tests import BasedTestCase, output, output_sql


class ChoicesModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()

    def test_level_choices(self):
        print(Choices.Level)    # <enum 'Level'>
        print(Choices.Level.choices) # [('FR', '大一新生'), ('SO', '大二'), ('JR', '初级'), ('SR', '高级'), ('GR', '毕业生')]
        print(Choices.Level.values)  # ['FR', 'SO', 'JR', 'SR', 'GR']
        print(Choices.Level.names)   # ['FRESHMAN', 'SOPHOMORE', 'JUNIOR', 'SENIOR', 'GRADUATE']
        print(Choices.Level.labels)  # ['大一新生', '大二', '初级', '高级', '毕业生']

        print(Choices.Level.FRESHMAN)   # <Choices.Level: FR>
        print(Choices.Level.FRESHMAN.value) # FR
        print(Choices.Level.FRESHMAN.label) # 大一新生
        print(Choices.Level.FRESHMAN.name)  # FRESHMAN

        print(Choices.Level['FRESHMAN'] == Choices.Level.FRESHMAN)

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
        data.gender = Choices.GENDER_CHOICES[1]
        data.category_type = Choices.CategoryType.KP
        data.level = Choices.Level.SENIOR
        data.medal_type = Choices.MedalType.SILVER
        output_sql(data.save())


    def test_choices_query(self):
        self.test_choices_model()
        output(Choices.objects.filter(answer=Choices.Answer.YES))
