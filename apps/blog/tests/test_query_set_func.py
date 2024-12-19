import datetime

from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries
from django.db.models import Avg, Max, Sum, Count, Min, FloatField, Q, StdDev, Variance

from apps.blog.models import Tags, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output


class QueryFieldFuncTest(BasedTestCase):
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

    def test_aggregate_functions(self):
        self.query_set_prepare_data()
        print("----------------test_aggregate_functions--------------------")
        # SELECT COALESCE(AVG("blog_tags"."id"), 0.0) AS "id__avg" FROM "blog_tags"
        output_sql(Tags.objects.aggregate(Avg("id", default=0)))
        output_sql(Tags.objects.aggregate(Max("id", default=0)))
        output_sql(Tags.objects.aggregate(Min("id", default=0)))
        output_sql(Tags.objects.aggregate(Sum("id", default=0)))
        output_sql(Tags.objects.aggregate(Sum("id", default=0), Min("id", default=0), Max("id", default=0), Avg("id", default=0)))

        # 标准差
        output_sql(Tags.objects.aggregate(StdDev("id", default=0)))
        # 方差
        output_sql(Tags.objects.aggregate(Variance("id", default=0)))

        # 自定义别名
        output_sql(Tags.objects.aggregate(sum_record=Sum("id", default=0)))

        # 统计数量  COUNT("blog_tags"."id")
        output_sql(Tags.objects.aggregate(Count("id")))

        # output_field 确定输出类型，类型转换
        # SELECT (COALESCE(SUM("blog_tags"."id"), 0.0) - COUNT("blog_tags"."id")) AS "diff_count" FROM "blog_tags"
        output_sql(Tags.objects.aggregate(diff_count=Sum("id", default=0, output_field=FloatField()) - Count("id")))

        # COUNT(DISTINCT "blog_tags"."tag_name")
        output_sql(Tags.objects.aggregate(Count("tag_name", distinct=True)))

        # 最早发表的日期，连接查询
        output_sql(Tags.objects.aggregate(Min("post__published_date")))

        # 过滤后再聚和统计
        output_sql(Tags.objects.filter(tag_name__contains='test').aggregate(Sum("id", default=0)))
        output_sql(Tags.objects.exclude(tag_name__contains='test').aggregate(Sum("id", default=0)))

    def test_annotate(self):
        self.query_set_prepare_data()
        print("----------------test_aggregate_functions--------------------")
        # GROUP BY
        foo = Count("tag_name", filter=Q(id__gt=2))
        bar = Count("tag_name", filter=Q(tag_name__contains='test'))
        output_sql(Tags.objects.annotate(foo=foo, bar=bar))
        output_sql(Tags.objects.annotate(tag_num=Count("tag_name")).order_by("-id")[:5])

        # values 在前面 设置分组和查询的字段，且统计
        output_sql(Tags.objects.values("id", "tag_name").annotate(tag_num=Count("tag_name")).order_by("-id")[:5])
        # order by 排序字段，会在 group by 中分组
        output_sql(Tags.objects.values("id", "tag_name").annotate(tag_num=Count("tag_name")).order_by("-post")[:5])
        # XXX 按统计进行排序
        output_sql(Tags.objects.values("id", "tag_name").annotate(tag_xxx=Count("tag_name")).order_by("tag_xxx"))
        # order_by() 清除排序
        output_sql(Tags.objects.values("id", "tag_name").annotate(tag_xxx=Count("tag_name")).order_by())

        # values 1 设置分组字段，values 2 设置查询字段
        # SELECT "blog_tags"."tag_name" FROM "blog_tags" GROUP BY "blog_tags"."id", "blog_tags"."tag_name" ORDER BY "blog_tags"."id" DESC LIMIT 5
        output_sql(Tags.objects.values("id", "tag_name").annotate(tag_num=Count("tag_name")).values("tag_name", "tag_num").order_by("-id")[:5])

        # 分组后 filter 相当于 having
        # SELECT "blog_tags"."tag_name", COUNT("blog_tags"."tag_name") AS "tag_num" FROM "blog_tags" GROUP BY "blog_tags"."tag_name" HAVING COUNT("blog_tags"."tag_name") > 1
        output_sql(Tags.objects.values("tag_name").annotate(tag_num=Count("tag_name")).filter(tag_num__gt=1))

        # filter 先后 和 values 先后 对语句的影响
        # SELECT "blog_tags"."tag_name", COUNT("blog_tags"."tag_name") AS "tag_num" FROM "blog_tags" WHERE "blog_tags"."id" > 1 GROUP BY "blog_tags"."tag_name"
        output_sql(Tags.objects.filter(id__gt=1).values("tag_name").annotate(tag_num=Count("tag_name")))

        # 分组组合
        output_sql(Tags.objects.values("tag_name").annotate(tag_num=Count("tag_name", distinct=True), tag_max=Count("tag_name")))
        # 连接分组
        output_sql(Tags.objects.annotate(status_num=Count("post__status"), max_date=Max("post__published_date")))
        output_sql(Tags.objects.annotate(Count("post")))
        # 每个标签下，最新发表的日期
        output_sql(Tags.objects.annotate(Max("post__published_date")))

        # 分组和子查询
        output_sql(Tags.objects.annotate(tag_num=Count("tag_name"), abc=Q(tag_name__contains='test')))
        # 分组并统计
        output_sql(Tags.objects.annotate(tag_num=Count("tag_name")).aggregate(Sum("tag_num")))

    def test_sql_monitor(self):
        self.query_set_prepare_data()

        reset_queries()
        print("----------------test_sql_monitor--------------------")
        output_sql(Tags.objects.filter(id__gte=2))

        output_sql(Tags.objects.filter(tag_name='tag test 1'))
        output_sql(Tags.objects.create(tag_name='tag test 1', post=self.post))

        with SqlContextManager():
            print(Tags.objects.create(tag_name='XSS', post=self.post))
            print(Tags.objects.filter(tag_name='XSS'))

        output_sql(Tags.objects.all())
        output_sql(Tags.objects.all().count())
        output_sql(Tags.objects.last())

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
