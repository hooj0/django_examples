from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db import reset_queries
from django.db.models import F, ExpressionWrapper, DecimalField, Prefetch
from django.db.models.aggregates import Count, Avg, Sum
from django.db.models.functions import Coalesce, Lower
from django.db.models.query import EmptyQuerySet
from django.utils import timezone

from apps.blog.models import Tags, Post, Book, Author, faker, Publisher, Topping, Pizza, Restaurant
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output
from common.util.utils import object_to_string


class QuerySetUnReturnTest(BasedTestCase):
    """
    不返回QuerySet部分：
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/querysets/#methods-that-do-not-return-querysets
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

    def test_query_set_object(self):
        print("----------------objects--------------------")
        output_sql(Tags.objects.get(id=2))
        output_sql(Tags.objects.get(pk=2))
        output_sql(Tags.objects.get(tag_name='tag test 1'))
        # ORDER BY "blog_tags"."id" ASC LIMIT 1
        output_sql(Tags.objects.first())
        # ORDER BY "blog_tags"."id" DESC LIMIT 1
        output_sql(Tags.objects.last())
        # COUNT(*)
        output_sql(Tags.objects.count())
        output_sql(Tags.objects.values('tag_name', 'id').last())
        # SELECT COUNT(*) FROM (SELECT DISTINCT "blog_tags"."tag_name" AS "col1" FROM "blog_tags") subquery
        output_sql(Tags.objects.values('tag_name').distinct().count())
        output_sql(len(Tags.objects.values('tag_name').distinct()))

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
