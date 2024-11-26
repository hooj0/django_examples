import logging

from django.test import TestCase

from apps.blog.models import Category, Author, Book

logger = logging.getLogger('example')

class BookModelTest(TestCase):

    def test_create_book_with_author(self):
        book = Book.objects.create(title='test')
        author = Author.objects.create(name='test')
        book.author.add(author)
        print(book)

    def test_create_book(self):
        book = Book.objects.create(title='test')
        print(book)


# 创建测试用例
class AuthorModelTest(TestCase):

    def test_create_author(self):
        author = Author.objects.create(name='test')
        print(author)

        logger.debug('This is a debug message')
        logger.info('This is an info message')

    def test_author_name_max_length(self):
        category = Category.objects.get(id=1)
        print(category)