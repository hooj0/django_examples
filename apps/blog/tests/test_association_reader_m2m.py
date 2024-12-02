from django.contrib.auth.models import User
from django.db import reset_queries

from apps.blog.models import Studio, Author, faker, Book, Reader, Club
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
        # 通过属性访问
        print(reader.books.all())
        # 通过集合访问
        print(reader.club_set.all())
        print(book2.club_set.all())
        print(book2.reader_set.all())

        Club.objects.create(book=book3, reader=reader, borrow_date=faker.date(), recommended=book2)
        print(reader.books.all())

        club = Club(book=book3, reader=reader2, borrow_date=faker.date(), recommended=book2)
        club.save()
        print(book3.reader_set.all())

        print(club.book_id)
        print(club.reader_id)
        print(club.recommended_id)

    def test_m2m_create(self):
        recommended_book = output_sql(Book.objects.create(title=faker.sentence(), author=self.author, price=1.11))

        book = output_sql(Book.objects.create(title=faker.sentence() + " Eat", author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2)))
        reader = output_sql(Reader.objects.create(reader_name=faker.name() + " Tom"))

        # 创建关联关系，正向设置
        output_sql(book.club_set.create(reader=reader, borrow_date=faker.date(), recommended=recommended_book))
        output_sql(reader.club_set.create(book=book, borrow_date=faker.date(), recommended=recommended_book))

        output_sql(reader.club_set.all())
        output_sql(book.club_set.all())

        # 创建关联关系，反向设置，基于中间表关联
        club = Club(reader=reader, book=book, borrow_date=faker.date(), recommended=recommended_book)
        club.save()
        output_sql(club)

        output_sql(reader.books.all())
        output_sql(book.reader_set.all())

        Club.objects.create(reader=reader, book=book, borrow_date=faker.date(), recommended=recommended_book)
        output_sql(reader.books.all())

    def test_m2m_crud(self):
        recommended_book = Book.objects.create(title=faker.sentence(), author=self.author, price=1.11)
        book = Book.objects.create(title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2))
        new_book = Book.objects.create(title=faker.sentence(), author=self.author, price=1.11)
        reader = Reader.objects.create(reader_name=faker.name())
        reset_queries()

        print("-------------------create---------------------")
        # create
        # 向属性集合添加数据，发出2条SQL，先查询集合，再添加中间表关联数据
        # reader.books ====>>> SELECT "blog_club"."book_id" FROM "blog_club" WHERE ("blog_club"."book_id" IN (2) AND "blog_club"."reader_id" = 1)
        # club.add ======>>>>> INSERT INTO "blog_club" ("reader_id", "book_id", "recommended_id", "borrow_date") VALUES (1, 2, 1, '1970-03-09') RETURNING "blog_club"."id"
        output_sql(reader.books.add(book, through_defaults={'borrow_date': faker.date(), 'recommended': recommended_book}))
        output_sql(reader.books.all())

        print("-------------------add---------------------")
        # add
        # 利用属性集合添加数据，发出3条SQL，创建book，查询books，添加club中间表关联数据
        # book.create =====>>> INSERT INTO "blog_book" ("title", "price", "author_id") VALUES ('Eat certainly contain realize offer behind.', '-84166068.14', 1) RETURNING "blog_book"."id"
        # reader.books ====>>> SELECT "blog_club"."book_id" FROM "blog_club" WHERE ("blog_club"."book_id" IN (3) AND "blog_club"."reader_id" = 1)
        # club.add ======>>>>> INSERT INTO "blog_club" ("reader_id", "book_id", "recommended_id", "borrow_date") VALUES (1, 3, 1, '2003-04-25') RETURNING "blog_club"."id"
        output_sql(reader.books.create(
            title=faker.sentence(), author=self.author, price=faker.pydecimal(left_digits=8, right_digits=2),
            through_defaults={'borrow_date': faker.date(), 'recommended': recommended_book})
        )
        output_sql(reader.books.all())

        print("-------------------set---------------------")
        # set
        # 相当于更新操作，触发4条SQL，先删除关联中间表数据，再进行插入关联中间表数据
        # reader-club.books ====>>> SELECT "blog_book"."id" FROM "blog_book" INNER JOIN "blog_club" ON ("blog_book"."id" = "blog_club"."book_id") WHERE "blog_club"."reader_id" = 1
        # club.delete ====>>> DELETE FROM "blog_club" WHERE ("blog_club"."reader_id" = 1 AND "blog_club"."book_id" IN (2, 3))
        # reader.books ====>>> SELECT "blog_club"."book_id" FROM "blog_club" WHERE ("blog_club"."book_id" IN (4) AND "blog_club"."reader_id" = 1)
        # club.add ======>>>>> INSERT INTO "blog_club" ("reader_id", "book_id", "recommended_id", "borrow_date") VALUES (1, 4, 1, '1975-05-20') RETURNING "blog_club"."id"
        output_sql(reader.books.set(
            [new_book, book],
            through_defaults={'borrow_date': faker.date(), 'recommended': recommended_book})
        )
        output_sql(reader.books.all())

        print("-------------------remove---------------------")
        output_sql(reader.books.remove(new_book))
        output_sql(reader.books.all())

        print("-------------------clear---------------------")
        output_sql(reader.books.clear())

    def test_m2m_filter(self):
        self.test_m2m_create()
        reset_queries()

        print("--------------------正向查询------------------------")
        # 正向查询
        output_sql(Reader.objects.filter(books__title__contains='Eat'))
        output_sql(Reader.objects.filter(books__title__contains='Eat').filter(books__price__gt=1))
        output_sql(Reader.objects.filter(books__in=[1, 2]))

        reader = Reader.objects.filter(books__title__contains='Eat').first()
        book = Book.objects.filter(title__contains='Eat').first()
        club = output_sql(reader.club_set.filter(book=book).last())
        print(club.borrow_date)

        book = Book.objects.filter(title__contains='Eat').first()
        club = output_sql(book.club_set.filter(reader=reader).last())
        print(club.borrow_date)

        output_sql(Reader.objects.filter(books__title__contains='Eat').count()) # 4
        output_sql(Reader.objects.filter(books__title__contains='Eat').distinct().count()) # 1

        output_sql(Reader.objects.filter(books__id__in=[1, 2]))
        output_sql(Reader.objects.filter(books__id=2))
        output_sql(Reader.objects.filter(books__pk=2))
        output_sql(Reader.objects.filter(books=2))
        output_sql(Reader.objects.filter(books=book))

        output_sql(Reader.objects.exclude(books=book))

    def test_m2m_filter_reverse(self):
        self.test_m2m_create()
        r1 = Reader.objects.first()
        r2 = Reader.objects.last()

        reset_queries()

        print("--------------------反向查询------------------------")
        # 反向查询，Reader 和 Club 关联，通过 book_id
        output_sql(Book.objects.filter(reader__reader_name__contains='Tom', club__borrow_date__gt='1970-01-01'))
        output_sql(Book.objects.filter(club__reader__reader_name__contains='Tom', club__borrow_date__gt='1970-01-01'))

        output_sql(Book.objects.filter(id__in=[1, 2]))
        output_sql(Book.objects.filter(pk=1))

        output_sql(Book.objects.filter(reader=r1))
        output_sql(Book.objects.filter(reader=1))
        output_sql(Book.objects.filter(reader__id=1))
        output_sql(Book.objects.filter(reader__pk=1))
        output_sql(Book.objects.filter(reader__in=[1, 2]).distinct())
        output_sql(Book.objects.filter(reader__in=[r1, r2]).distinct())

        output_sql(Book.objects.exclude(reader=r1))

    def test_m2m_filter_through(self):
        self.test_m2m_create()
        reset_queries()

        print("--------------------从中间表查询------------------------")
        # 从中间表查询
        club = output_sql(Club.objects.filter(book__title__contains='Eat').first())
        print(club.book)
        print(club.reader)
        print(club.borrow_date)

        club = output_sql(Club.objects.filter(book=club.book, reader=club.reader).last())
        print(club.borrow_date)



