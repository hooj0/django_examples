import datetime

from django.contrib.auth.models import User
from django.db import reset_queries
from django.db.models import Avg, Max, Sum, Count, Min, FloatField, Q, StdDev, Variance, Aggregate, OuterRef, Subquery, Exists, CharField
from django.db.models.expressions import RawSQL
from django.db.models.functions import Length
from django.utils import timezone

from apps.blog.models import Tags, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager


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
        reset_queries()

    def test_aggregate_functions(self):
        """
        https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#aggregate-expressions
        https://docs.djangoproject.com/zh-hans/5.1/topics/db/aggregation/#top
        示例参考：
        https://lxblog.com/qianwen/share?shareId=a57834b8-dff7-4b8b-bfa6-a2c9cb31bb4c
        """
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

        class MySum(Aggregate):
            # Supports SUM(ALL field).
            function = "SUM"
            template = "%(function)s(%(all_values)s%(expressions)s)"
            allow_distinct = False

            def __init__(self, expression, all_values=False, **extra):
                super().__init__(expression, all_values="ALL " if all_values else "", **extra)

        # SELECT COALESCE(SUM("blog_tags"."id"), 0) AS "total" FROM "blog_tags" WHERE NOT ("blog_tags"."tag_name" LIKE '%test%' ESCAPE '\')
        output_sql(Tags.objects.exclude(tag_name__contains='test').aggregate(total=MySum("id", default=0)))

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

    def test_subquery(self):
        """
        Subquery(queryset, output_field=None)
        使用 Subquery 表达式向 QuerySet 添加一个显式子查询

        OuterRef(field)
        当 Subquery 中的查询集需要引用外部查询或其转换的字段时，请使用 OuterRef
        """
        # SELECT "blog_post"."id", "blog_post"."title", "blog_post"."content", "blog_post"."created_date", "blog_post"."published_date", "blog_post"."image", "blog_post"."author_id", "blog_post"."status",
        # (SELECT U0."tag_name" FROM "blog_tags" U0 WHERE U0."post_id" = ("blog_post"."id") ORDER BY U0."tag_name" DESC LIMIT 1) AS "newest_tagname"
        # FROM "blog_post" LIMIT 21
        newest = Tags.objects.filter(post=OuterRef("pk")).order_by("-tag_name")
        output_sql(Post.objects.annotate(newest_tagname=Subquery(newest.values("tag_name")[:1])))

        # output_sql(Tags.objects.filter(post=OuterRef("pk")))

        # SELECT "blog_tags"."id", "blog_tags"."tag_name", "blog_tags"."post_id" FROM "blog_tags"
        # WHERE "blog_tags"."post_id" IN (SELECT U0."id" FROM "blog_post" U0 WHERE U0."published_date" >= '2024-12-23 02:50:52.020441')
        posts = Post.objects.filter(published_date__gte=(timezone.now() - datetime.timedelta(days=1)))
        output_sql(Tags.objects.filter(post__in=Subquery(posts.values("pk"))))

    def test_exists(self):
        """
        Exists 是一个 Subquery 子类，它使用 SQL EXISTS 语句。
        """

        # SELECT "blog_post"."id", "blog_post"."title", "blog_post"."content", "blog_post"."created_date", "blog_post"."published_date", "blog_post"."image", "blog_post"."author_id", "blog_post"."status",
        # EXISTS(SELECT 1 AS "a" FROM "blog_tags" U0 WHERE (U0."post_id" = ("blog_post"."id") AND U0."tag_name" LIKE '%test%' ESCAPE '\') LIMIT 1) AS "tag_exists"
        # FROM "blog_post"
        tags = Tags.objects.filter(post=OuterRef("pk"), tag_name__contains="test")
        output_sql(Post.objects.annotate(tag_exists=Exists(tags)))

        # 取反
        output_sql(Post.objects.annotate(tag_exists=~Exists(tags)))

        tags = Tags.objects.filter(post=OuterRef("pk")).order_by().values("post")
        total_comments = tags.annotate(total=Sum(Length("tag_name"))).values("total")

        CharField.register_lookup(Length)
        # SELECT "blog_post"."id", "blog_post"."title", "blog_post"."content", "blog_post"."created_date", "blog_post"."published_date", "blog_post"."image", "blog_post"."author_id", "blog_post"."status" FROM "blog_post"
        # WHERE LENGTH("blog_post"."title") > (SELECT SUM(LENGTH(U0."tag_name")) AS "total" FROM "blog_tags" U0 WHERE U0."post_id" = ("blog_post"."id") GROUP BY U0."post_id")
        output_sql(Post.objects.filter(title__length__gt=Subquery(total_comments)))

    def test_rawsql(self):
        """
        RawSQL(sql, params, output_field=None)
        在表达式无法满足情况，可以使用sql
        """
        # SELECT "blog_tags"."id", "blog_tags"."tag_name", "blog_tags"."post_id",
        # (select id from blog_post where title like '%s%') AS "custom_id" FROM "blog_tags"
        output_sql(Tags.objects.annotate(custom_id=RawSQL("select id from blog_post where title like %s", ("%s%",))))

        # SELECT "blog_tags"."id", "blog_tags"."tag_name", "blog_tags"."post_id" FROM "blog_tags"
        # WHERE "blog_tags"."post_id" IN (select id from blog_post where title like '%s%')
        output_sql(Tags.objects.filter(post_id__in=RawSQL("select id from blog_post where title like %s", ("%s%",))))

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
