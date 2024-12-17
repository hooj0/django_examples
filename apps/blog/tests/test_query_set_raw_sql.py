from collections import namedtuple

from django.contrib.auth.models import User
from django.db import connection, connections
from django.db import reset_queries

from apps.blog.models import Tags, Post, Book, Author, faker, Publisher, Topping, Pizza, Restaurant
from apps.blog.tests.tests import BasedTestCase, output_sql, sql_decorator


class QuerySetRawSQLTest(BasedTestCase):
    """
    https://docs.djangoproject.com/zh-hans/5.1/topics/db/sql/#top
    管理器方法 raw() 能用于执行原生 SQL 查询，就会返回模型实例：
        Manager.raw(raw_query, params=(), translations=None)
    """

    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)
        # 查询所有Post
        print("posts: ", Post.objects.all())

        self.query_set_prepare_data()
        self.prefetch_related_prepare_data()

    def test_query(self):
        qs = output_sql(Tags.objects.raw("SELECT * FROM blog_tags"))
        print(qs)  # <RawQuerySet: SELECT * FROM blog_tags>
        print(type(qs))

        for tag in qs:
            print(tag)

        # 获取表名
        print(Tags._meta.db_table) # blog_tags
        output_sql(Tags.objects.raw(f"SELECT * FROM {Tags._meta.db_table}").columns)

    def test_query_column(self):
        output_sql(Post.objects.raw("SELECT title, created_date, status FROM blog_post").columns)

        # 取别名，对应模型属性
        output_sql(Post.objects.raw("SELECT title AS name, created_date AS date, status FROM blog_post").columns)
        # 名称映射转换
        output_sql(Post.objects.raw("SELECT title, created_date, status FROM blog_post", translations={'title': 'name', 'created_date': 'date', 'status': 'is_published'}).columns)

    def test_query_index(self):
        # 索引是在数据全部返回后再进行索引，所以索引从0开始
        # 并没有改变SQL语句
        output_sql(Tags.objects.raw("SELECT * FROM blog_post")[0])

        # 推荐写法
        output_sql(Tags.objects.raw("SELECT * FROM blog_post limit 1")[0])

    @sql_decorator
    def test_query_lazy_column(self):
        """
        没有主键数据，所以会报错
        FieldDoesNotExist: Raw query must include the primary key
        按需加载，延迟查询：对于查询的字段会进行原始SQL查询，对于未查询到的字段，会自动发出SQL进行查询
        """
        # qs = Post.objects.raw("SELECT title, created_date, status FROM blog_post")
        qs = Post.objects.raw("SELECT id, title, created_date FROM blog_post limit 1")
        for post in qs:
            # SELECT id, title, created_date FROM blog_post limit 1
            print(post.title)   # 对于查询到的字段，会直接从缓存中读取，不会再次查询
            print(post.created_date)

            # 对于未查询到的字段，会发出SQL进行查询
            # SELECT "blog_post"."id", "blog_post"."status" FROM "blog_post" WHERE "blog_post"."id" = 1 LIMIT 21
            # SELECT "blog_post"."id", "blog_post"."content" FROM "blog_post" WHERE "blog_post"."id" = 1 LIMIT 21
            print(post.status)
            print(post.content)

    @sql_decorator
    def test_query_with_func(self):
        # 函数查询
        qs = Post.objects.raw("select count(1) as count, max(published_date) as max_date, id from blog_post")
        for item in qs:
            print(item)
            print(item.count)
            print(item.max_date)

    @sql_decorator
    def test_query_with_params(self):
        # 占位符传参
        print(Tags.objects.raw("SELECT * FROM blog_tags WHERE post_id = %s", [1])[0])
        # 传like参数
        print(Tags.objects.raw("SELECT * FROM blog_tags WHERE post_id >= %s OR tag_name like %s", [1, "%tag%"])[0])

    @sql_decorator
    def test_cursor_sql(self):
        # 游标使用
        with connection.cursor() as cursor:
            cursor.execute("UPDATE blog_post SET created_date = datetime() WHERE id = %s", [1])
            cursor.execute("SELECT created_date FROM blog_post WHERE id = %s", [1])
            row = cursor.fetchone()

        # 返回查询结果
        print(row)  # (datetime.datetime(2024, 12, 17, 7, 12, 37),)

        # 针对多个数据库连接，使用别名
        with connections["my_db_alias"].cursor() as cursor:
            pass

    def test_cursor_row(self):
        """
        封装返回结果
        """
        def dict_fetchall(cursor):
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        def namedtuple_fetchall(cursor):
            desc = cursor.description
            nt_result = namedtuple("Result", [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM blog_post limit 2")
            print(cursor.fetchall())
            print(cursor.description)
            print("")

            cursor.execute("SELECT * FROM blog_post limit 2")
            print(dict_fetchall(cursor))
            print("")

            cursor.execute("SELECT * FROM blog_post limit 2")
            print(namedtuple_fetchall(cursor))
            print("")

    def test_cursor(self):
        # 和 with 方式一致
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM blog_post")
            print(cursor.fetchall())
        finally:
            cursor.close()

    def test_proc(self):
        # 调用存储过程
        with connection.cursor() as cursor:
            cursor.callproc("test_procedure", [1, "test"])

    def query_set_prepare_data(self):
        Tags.objects.create(tag_name='tag test 1', post=self.post)
        Tags.objects.create(tag_name='tag Test 2', post=self.post)
        Tags.objects.create(tag_name='tag test 3', post=self.post)
        Tags.objects.create(tag_name='tag test 4', post=self.post)
        Tags.objects.create(tag_name='tag test 4', post=self.post)

        Tags.objects.create(tag_name='Of Returning HTTP', post=self.post)
        Tags.objects.create(tag_name='error codes', post=self.post)
        Tags.objects.create(tag_name='in Django is easy', post=self.post)
        Tags.objects.create(tag_name='There are subclasses', post=self.post)
        Tags.objects.create(tag_name='of HttpResponse', post=self.post)
        Tags.objects.create(tag_name='OF', post=self.post)
        print("prepare data: ", Tags.objects.all())

        author = Author.mock_data()
        author.user = self.user
        author.save()

        for i in range(10):
            book = Book.mock_data()
            book.author = author
            book.save()

            Post.objects.create(title=faker.name(), content=faker.text(), author=self.user)
        print("prepare data: ", Book.objects.all())

        publisher = Publisher.objects.create(publisher_name=faker.company())
        publisher.books.add(1, 2, 3, 7)

        publisher = Publisher.objects.create(publisher_name=faker.company())
        publisher.books.add(4, 5, 6, 8, 9)
        reset_queries()

    def prefetch_related_prepare_data(self):
        topping1 = Topping.objects.create(name="咸蛋黄")
        topping2 = Topping.objects.create(name="芝士")
        topping3 = Topping.objects.create(name="火腿")
        topping4 = Topping.objects.create(name="鸡肉")
        topping5 = Topping.objects.create(name="榴莲")
        topping6 = Topping.objects.create(name="菠萝")

        p1 = Pizza.objects.create(name="辣肠披萨")
        p1.toppings.add(topping1, topping2, topping3)

        p2 = Pizza.objects.create(name="榴莲披萨")
        p2.toppings.add(topping4, topping5, topping6)

        p3 = Pizza.objects.create(name="水果披萨")
        p3.toppings.add(topping1, topping4, topping5, topping6)

        p4 = Pizza.objects.create(name="暗黑披萨")
        p4.toppings.add(topping1, topping6)

        r1 = Restaurant.objects.create(name="高级披萨餐厅", best_pizza=p1)
        r1.pizzas.add(p1, p2, p3, p4)

        r2 = Restaurant.objects.create(name="水果萨餐厅", best_pizza=p2)
        r2.pizzas.add(p2, p3)

        r3 = Restaurant.objects.create(name="素食披萨餐厅", best_pizza=p3)
        r3.pizzas.add(p1, p3)

        r4 = Restaurant.objects.create(name="暗黑萨餐厅", best_pizza=p4)
        r4.pizzas.add(p1, p2)
        reset_queries()
