from django.contrib.auth.models import User
from django.db import reset_queries

from apps.blog.models import Author, Book, Post, faker, Tags, Studio
from apps.blog.tests.tests import BasedTestCase, sql_decorator, output_sql


class BookModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)

        self.tags = Tags.objects.create(post=self.post, tag_name=faker.name())
        self.studio = Studio.objects.create(name='user studio', address='广水市')
        reset_queries()

    @sql_decorator
    def test_create_book(self):
        author = Author.mock_data()
        author.save()

        book = Book.objects.create(title=faker.name(), price=faker.pydecimal(left_digits=3, right_digits=2), author=author)
        print(book)
        print(book.author)
        # Author 默认 外键字段名是 author_id
        print(book.author_id)
        # books 名称 和 Book.author字段上的外键 related_name="books" 关联
        print(book.author.books)    # blog.Book.None 表明有多个book

        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book" WHERE "blog_book"."author_id" = 1
        print(book.author.books.all())

    @sql_decorator
    def test_create_author_books(self):
        author = Author.mock_data()
        author.user = self.user
        # INSERT INTO "blog_author" ("name", "age", "user_id") VALUES ('Mock Author alexanderjohnson', 35, 1) RETURNING "blog_author"."id"
        author.save()

        print(author)

        book = Book.mock_data()
        book.author = author
        # INSERT INTO "blog_book" ("title", "price", "author_id") VALUES ('Mock Book Brenda Taylor', '-906.95', 1) RETURNING "blog_book"."id"
        book.save()

        book2 = Book.mock_data()
        book2.author = author
        # INSERT INTO "blog_book" ("title", "price", "author_id") VALUES ('Mock Book Caroline Sutton', '-625.35', 1) RETURNING "blog_book"."id"
        book2.save()

        print(author)
        # books 名称 和 Book.author字段上的外键 related_name="books" 关联
        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book" WHERE "blog_book"."author_id" = 1 LIMIT 21
        print(author.books.all())

    @sql_decorator
    def test_create_book_with_author(self):
        author = Author.mock_data()
        author.user = self.user
        # INSERT INTO "blog_author" ("name", "age", "user_id") VALUES ('Mock Author alexanderjohnson', 35, 1) RETURNING "blog_author"."id"
        author.save()

        print(author)

        book = Book.mock_data()
        # INSERT INTO "blog_book" ("title", "price", "author_id") VALUES ('Mock Book Jacob Cooper', '-665.35', NULL) RETURNING "blog_book"."id"
        book.save()

        book2 = Book.mock_data()
        # INSERT INTO "blog_book" ("title", "price", "author_id") VALUES ('Mock Book Larry Rivera', '-292.87', NULL) RETURNING "blog_book"."id"
        book2.save()

        # 反向添加，触发update操作
        # UPDATE "blog_book" SET "author_id" = 1 WHERE "blog_book"."id" IN (1, 2)
        author.books.add(book, book2)

        print(author)
        # book_set 名称 和 book的外键 related_name="books" 关联
        # 触发SQL
        print(author.books.all())

    def test_delete_cascade(self):
        author = Author.mock_data()
        author.save()
        print(Author.objects.all())

        book = Book.mock_data()
        book.save()

        author.books.add(book)
        print(Book.objects.all())

        # on_delete=models.CASCADE：删除 author，级联删除 book
        author.delete()
        print(Book.objects.all())   # empty
        print(Author.objects.all()) # empty

        if True:
            return

        # on_delete=models.PROTECT：删除 author，ProtectedError 防止删除被引用对象
        author.delete() # django.db.models.deletion.ProtectedError: ("Cannot delete some instances of model 'Author' because they are referenced through protected foreign keys: 'Book.author'.", {<Book: _state: unknown, id: 1>})

        # on_delete=models.RESTRICT：删除 author，RestrictedError 来防止删除被引用的对象
        author.delete() # django.db.models.deletion.RestrictedError: ("Cannot delete some instances of model 'Author' because they are referenced through restricted foreign keys: 'Book.author'.", {<Book: _state: unknown, id: 1>})

        # on_delete=models.SET_NULL：删除 author，级联的数据关系被设置Null
        author.delete()
        print(Book.objects.all())   # <QuerySet [<Book: _state: unknown, id: 1, title: Mock Book *****, price: -589.29, author_id: None>]>
        print(Author.objects.all()) # <QuerySet []>

        # on_delete=models.DO_NOTHING：删除 author，IntegrityError 未做任何操作，引用完整性不在
        author.delete()
        print(Book.objects.all())   # <QuerySet [<Book: _state: unknown, id: 1, title: Mock Book *****, price: 364.15, author_id: 1>]>
        print(Author.objects.all()) # empty

        # on_delete=models.SET(get_user_id)：删除 author，修改重置关联的数据
        author.delete()

    def test_m2o_query(self):
        author, book = self.prepare_data()
        reset_queries()

        print("-------------------正向查询--------------------")
        print(author)
        print(book)

        output_sql(book.author)

        author2 = Author.mock_data()
        author2.save()
        book.author = author2
        print(book)
        output_sql(book.author)

        output_sql(Book.objects.select_related().all())
        output_sql(Book.objects.select_related().get(pk=1))
        output_sql(Book.objects.select_related("author"))

    def test_m2o_query_reverse(self):
        author, book = self.prepare_data()
        reset_queries()

        print("-------------------反向查询--------------------")
        print(Author.objects.filter(book__title__contains='Mock Book'))
        print(author.books.all())

    def test_m2o_crud(self):
        # 创建
        author, book = self.prepare_data()

        print(book)
        print(author)
        print(author.books.all())

        # 取消关联
        book.author = None # author_id: None
        book.save()
        # author.books.remove(book)
        print(book)
        print(author.books.all())   # <QuerySet []>

        # 清空关联
        author.books.set([])
        author.books.clear()
        print(author.books.all())

    def prepare_data(self):
        author = Author.mock_data()
        author.save()

        book = Book.mock_data()
        book.save()

        author.books.add(book)
        return author, book