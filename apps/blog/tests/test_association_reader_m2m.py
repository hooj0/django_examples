from unittest import TestCase
from django.contrib.auth.models import User
from django.db import reset_queries

from apps.blog.models import Studio, Author, faker, Book, Publisher, Reader, Club
from apps.blog.tests.tests import BasedTestCase, sql_decorator, output_sql

class PublisherModelTest(BasedTestCase):

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

        reader = Reader.objects.create(reader_name=faker.name())
        reader2 = Reader.objects.create(reader_name=faker.name())
        # 向 club 插入数据，但额外自定义的字段为空
        # INSERT INTO "blog_club" ("reader_id", "book_id", "recommended_id", "borrow_date") VALUES (1, 2, NULL, '2024-11-29'), (1, 3, NULL, '2024-11-29') RETURNING "blog_club"."id"
        # reader.books.add(book2, book3)

        # 关联中间表，填充扩展字段
        Club.objects.create(book=book2, reader=reader, borrow_date=faker.date(), recommended=book1)
        print(reader.books.all())
        print(book2.reader_set.all())

        Club.objects.create(book=book3, reader=reader, borrow_date=faker.date(), recommended=book2)
        Club.objects.create(book=book3, reader=reader2, borrow_date=faker.date(), recommended=book2)
        print(reader.books.all())
        print(book3.reader_set.all())

    @sql_decorator
    def test_m2m_crud(self):
        recommended_book = Book.objects.create(title=faker.sentence(), author=self.author, price=1.11)

        book = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))
        reader = Reader.objects.create(reader_name=faker.name())

        book.club_set.create(reader=reader, borrow_date=faker.date(), recommended=recommended_book)
        reader.club_set.create(book=book, borrow_date=faker.date(), recommended=recommended_book)

        print(reader.club_set.all())
        print(book.club_set.all())

        club = Club.objects.create(book=book, borrow_date=faker.date(), recommended=recommended_book)
        reader.club_set.add(club)
        print(book.club_set)
