from django.test import TestCase

from apps.blog.models import Category
from apps.blog.tests.tests import BasedTestCase, output


class CategoryModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()

    def test_category_choices(self):
        choices = Category.CategoryType
        print(choices.KP.label)
        print(choices.KP.value)
        print(choices.KP == choices.SW)
        print(choices.choices)
        print(choices.names)
        print(choices.values)
        print(choices.labels)

    def test_category_model(self):
        category = Category.objects.create(category_name=Category.CategoryType.SW, category_text=Category.get_currencies()[0][0], category_type=Category.CategoryType.KP)
        output(category)
