from django.test import TestCase

from apps.blog.models import Category


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods.
        Category.objects.create(category_name=None)

    def test_category_name_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)  # Assuming the name field has a max_length of 100

    def test_category_str_representation(self):
        category = Category.objects.get(id=1)
        self.assertEqual(str(category), 'TestCategory')  # Check if the string representation is correct

    def test_category_choices(self):
        choices = Category.CategoryType
        print(choices.KP.label)
        print(choices.KP.value)
        print(choices.KP == choices.SW)
        print(choices.choices)
        print(choices.names)
        print(choices.values)
        print(choices.labels)
