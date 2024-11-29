from django.contrib.auth.models import User
from django.db import reset_queries

from apps.blog.models import Studio, Author, faker
from apps.blog.tests.tests import BasedTestCase, sql_decorator, output_sql


class AuthorModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='user', email='user@test.com')
        self.studio = Studio.objects.create(name='user studio', address='广水市')

        user = User.objects.create(username='tom', email='tom@test.com')
        studio = Studio.objects.create(name='tom studio', address='广州市')
        Author.objects.create(name=faker.user_name(), age=faker.pyint(), user=user, studio=studio)
        reset_queries()

    @sql_decorator
    def test_create_author(self):
        author = Author.objects.create(name=faker.user_name(), age=faker.pyint(), user=self.user, studio=self.studio)
        print(author)

        # 反向查询，一对多
        # book_set 名称 和 book的外键 related_name="books" 关联
        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book" WHERE "blog_book"."author_id" = 1
        print(author.books.all())

        # 正向查询 一对一
        # 内存数据 user=self.user，不触发SQL
        print(author.user)
        print(author.user.email)
        # Author 和 User 一对一 正方向设置属性，related_name="author_of"
        print(author.user.author_of == author) # True
        # Author 和 User 一对一，related_name="默认 当前模型名称小写" 方向设置属性
        print(author.studio.author == author) # True

    def test_query_user_reverse(self):
        # 反向查询 一对一
        user = output_sql(User.objects.last())

        # Author 和 User 一对一，Author 方向设置属性 related_name="author_of"
        # SELECT "blog_author"."id", "blog_author"."name", "blog_author"."age", "blog_author"."user_id" FROM "blog_author" WHERE "blog_author"."user_id" = 1
        output_sql(user.author_of) # 触发SQL

        # 反向查询 一对一
        studio = output_sql(Studio.objects.get(name='tom studio'))
        # Author 和 Studio 一对一，Author 反向默认设置 related_name="Author默认小写"
        output_sql(studio.author)

    def test_query_author(self):
        author = output_sql(Author.objects.first())

        # book_set 名称 和 book的外键 related_name="books" 关联
        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book" WHERE "blog_book"."author_id" = 1
        output_sql(author.books.all())

        # 触发SQL 查询
        # SELECT "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined" FROM "auth_user" WHERE "auth_user"."id" = 2 LIMIT 21
        output_sql(author.user.email)
        output_sql(author.user.author_of)
        output_sql(author.user)
        output_sql(author.user.author_of == author) # True
