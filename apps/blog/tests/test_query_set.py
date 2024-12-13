from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries

from apps.blog.models import Tags, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output


class QuerySetTest(BasedTestCase):
    """
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/querysets/#top
    """

    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)
        # 查询所有Post
        print("posts: ", Post.objects.all())

    def test_query_set(self):
        self.query_set_prepare_data()

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

        print("----------------all--------------------")
        output_sql(Tags.objects.all())
        # ORDER BY "blog_tags"."id" ASC LIMIT 1
        output_sql(Tags.objects.all().first())
        # ORDER BY "blog_tags"."id" DESC LIMIT 1
        output_sql(Tags.objects.all().last())
        output_sql(Tags.objects.all().get(id=2))
        # COUNT(*)
        output_sql(Tags.objects.all().count())

        print("----------------filter--------------------")
        output_sql(Tags.objects.filter(tag_name='tag test 1'))
        output_sql(Tags.objects.filter(tag_name='tag test 1').first())
        output_sql(Tags.objects.filter(tag_name='tag test 1').count())

        output_sql(Tags.objects.filter(tag_name__startswith='tag test'))
        # -id 倒序， ORDER BY "blog_tags"."id" DESC
        output_sql(Tags.objects.filter(tag_name__contains='test').order_by('-id'))
        output_sql(Tags.objects.filter(tag_name__in=['tag test 1', 'tag test 2']))

        print("----------------exclude--------------------")
        # 排除 NOT ("blog_tags"."tag_name" = 'tag test 1')
        output_sql(Tags.objects.exclude(tag_name='tag test 1'))

    @sql_decorator
    def test_query_chain(self):
        self.query_set_prepare_data()

        print("----------------query set--------------------")
        # 链式
        list = Tags.objects.filter(tag_name__contains='test').exclude(tag_name='tag test 1').filter(tag_name='tag test 2').values("tag_name")
        print(f"list: {list}")
        print(list.query)

        query1 = list.filter(tag_name__endswith='test 2')
        print(query1)
        print(query1.query)
        print(query1.filter(tag_name__endswith='test 3'))

        query2 = list.exclude(tag_name__endswith='test 2')
        print(query2)
        print(query2.query)

    def test_query_collection(self):
        self.query_set_prepare_data()
        print("----------------test_query_collection--------------------")
        foo = Tags.objects.filter(tag_name__endswith='test 1')
        bar = Tags.objects.filter(tag_name__contains='test').exclude(tag_name='tag test 3').exclude(tag_name='tag test 2')
        print("foo: ", foo)
        print("bar: ", bar)

        # 交集 UNION
        output(foo.union(bar))
        # 差集 INTERSECT
        output(foo.intersection(bar))
        # 并集 EXCEPT
        output(bar.difference(foo))

        # print(foo.symmetric_difference(bar))

    def test_query_func(self):
        self.query_set_prepare_data()

        print("----------------test_query_func--------------------")

        foo = Tags.objects.all()

        # DISTINCT
        output(foo.distinct())
        output(foo.reverse())
        print(foo.count())
        print(list(foo))

        # 执行的数据库
        print(foo.db)
        # 是否排序
        print(foo.ordered)

        for item in Tags.objects.all():
            print(item)

        if not Tags.objects.filter(tag_name="Test"):
            print("There is at least one Entry with the headline Test")

    def test_query_range(self):
        self.query_set_prepare_data()

        print("----------------test_query_range--------------------")
        # LIMIT 3
        output_sql(Tags.objects.all()[:3])
        # LIMIT 2 OFFSET 1
        output_sql(Tags.objects.all()[1:3])

        # 步长取值
        output_sql(Tags.objects.all()[:3:2])
        output_sql(Tags.objects.all()[:5:2])
        # print(Tags.objects.all()[-2]) # ERROR

        with SqlContextManager():
            # 索引取值
            print(Tags.objects.all()[2])
            print(Tags.objects.order_by("id")[2])
            # 大致相当于：
            # >>> Entry.objects.order_by("headline")[0:1].get()

        # 创建一个字符串数组，长度为10，填充字符串到数组
        list = [str(i) for i in range(10)]
        print(list)
        print(list[:])
        print(list[:3])
        print(list[1:3])

        # 步长为2，在0-5区间取值
        print(list[0:5:2])
        # 步长为1，在0-5区间取值
        print(list[2:8:3])

    def test_sql_raw(self):
        print("----------------test_sql_raw--------------------")
        # 执行一些操作
        instance = Tags.objects.create(tag_name='example', post=self.post)
        print(instance)

        # 获取并打印所有已执行的 SQL 查询
        for query in connection.queries:
            print(query['time'] + " -> " + query['sql'])

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
        reset_queries()
