from django.contrib.auth.models import User
from django.db import reset_queries

from apps.blog.models import Studio, Author, faker, Book, Publisher
from apps.blog.tests.tests import BasedTestCase, sql_decorator, output_sql


class PublisherModelTest(BasedTestCase):
    """
    多对多关系：
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/#manytomanyfield
    示例参考：
    https://docs.djangoproject.com/zh-hans/5.1/topics/db/examples/many_to_many/
    """
    def setUp(self):
        super().setUp()

        user = User.objects.create(username='tom', email='tom@test.com')
        studio = Studio.objects.create(name='tom studio', address='广州市')
        self.author = Author.objects.create(name=faker.user_name(), age=faker.pyint(), user=user, studio=studio)
        reset_queries()

    @sql_decorator
    def test_create_book(self):
        book1 = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))
        book2 = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))
        book3 = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))

        publisher = Publisher.objects.create(publisher_name=faker.company())
        publisher.books.add(book1, book2, book3)

        publisher2 = Publisher.mock_data()
        publisher2.save()
        # needs to have a value for field "id" before this many-to-many relationship can be used.
        publisher2.books.add(book1, book2)

    @sql_decorator
    def test_create_book_with_publisher(self):
        publisher1 = Publisher.objects.create(publisher_name=faker.company())
        publisher2 = Publisher.objects.create(publisher_name=faker.company())

        book = Book.mock_data()
        book.author = self.author
        book.save()

        # 向中间表 blog_publisher_books 插入 关联数据
        book.publisher_set.add(publisher1, publisher2)

        book2 = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))
        book2.publisher_set.add(publisher1)
        book2.publisher_set.add(Publisher.objects.create(publisher_name=faker.company()))

    def test_query_publisher_books(self):
        self.test_create_book()
        print("------------------------------------------------")
        output_sql(Publisher.objects.all())
        publisher = output_sql(Publisher.objects.first())

        output_sql(publisher.books)
        output_sql(publisher.books.all())

    def test_query_book_publisher(self):
        self.test_create_book()
        print("------------------------------------------------")
        book = output_sql(Book.objects.last())

        output_sql(book.publisher_set)
        output_sql(book.publisher_set.all())
        output_sql(book.publisher_set.first().books.all())