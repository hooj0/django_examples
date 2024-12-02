import datetime

from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries
from django.db.models import Avg, Max, Sum, Count, Min, FloatField, Q, StdDev, Variance

from apps.blog.models import Tags, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output


class TagsModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)
        # 查询所有Post
        print("posts: ", Post.objects.all())

    def test_create_tags(self):
        reset_queries()
        tags = Tags.objects.create(tag_name='tag test', post=self.post)
        output_sql("tags: ", tags)

        tags_foo = Tags(tag_name='tag test foo', post=self.post)
        tags_foo.save()
        output_sql("tags_foo: ", tags_foo)

        with SqlContextManager():
            tmp = Tags.create_tags('tag b', self.post)
            print("tmp: ", tmp)

        # tmp = Tags.objects.create_tag('tag bb', 1)
        print("tmp: ", tmp)

    @sql_decorator
    def test_update_tags(self):
        tags = Tags.objects.create(tag_name='tag test', post=self.post)
        print("tags: ", tags)
        tags.tag_name = 'foo'
        tags.save()
        print("tags: ", tags)

        tags_foo = Tags.objects.get(tag_name='foo')
        print("tags_foo: ", tags_foo)
        tags_foo.tag_name = 'xyz'
        tags_foo.save()
        print("tags_foo: ", tags_foo)

        # UPDATE "blog_tags" SET "tag_name" = 'barxxxxxxxx'
        row = Tags.objects.update(tag_name='barxxxxxxxx')
        print("tags_bar: ", row)
        tags_bar = Tags.objects.get(id=1)
        print("tags_bar: ", tags_bar)

        # UPDATE "blog_tags" SET "tag_name" = 'bar' WHERE "blog_tags"."tag_name" = 'barxxxxxxxx'
        row = Tags.objects.filter(tag_name='barxxxxxxxx').update(tag_name='bar')
        print(row)

    @sql_decorator
    def test_delete_tags(self):
        tags = Tags.objects.create(tag_name='tag test', post=self.post)
        print("tags: ", tags)

        # 级联删除
        # DELETE FROM "blog_author_tags" WHERE "blog_author_tags"."tags_id" IN (1)
        # DELETE FROM "blog_tags" WHERE "blog_tags"."id" IN (1)
        row = tags.delete()
        print(f"tags: {tags}, row: {row}")

        tags = Tags.objects.create(tag_name='tag delete', post=self.post)
        print(tags)
        # 先查询，再删除
        # SELECT "blog_tags"."id", "blog_tags"."tag_name", "blog_tags"."post_id" FROM "blog_tags" WHERE "blog_tags"."id" = 2 LIMIT 21
        # DELETE FROM "blog_author_tags" WHERE "blog_author_tags"."tags_id" IN (2)
        row = Tags.objects.get(id=2).delete()
        print(f"tags: {tags}, row: {row}")

        Tags.objects.create(tag_name='tag remove 1', post=self.post)
        Tags.objects.create(tag_name='tag remove 2', post=self.post)

        # DELETE FROM "blog_author_tags" WHERE "blog_author_tags"."tags_id" IN (3, 4)
        # DELETE FROM "blog_tags" WHERE "blog_tags"."id" IN (4, 3)
        tmp = Tags.objects.all().delete()
        print(f"tmp tags: {tmp}")

        Tags.objects.create(tag_name='tag remove 2', post=self.post)
        # 会先进行查询，再执行删除
        # DELETE FROM "blog_author_tags" WHERE "blog_author_tags"."tags_id" IN (5)
        # DELETE FROM "blog_tags" WHERE "blog_tags"."id" IN (5)
        tmp = Tags.objects.filter(tag_name__icontains='remove').delete()
        print("tmp tags: ", tmp)

        Tags.objects.create(tag_name='remove', post=self.post)
        # 使用原始SQL删除
        cursor = connection.cursor()
        row = cursor.execute("DELETE FROM blog_tags WHERE tag_name = 'remove'")
        print("row: ", row)
        print(cursor.rowcount)
        cursor.close()

        print("tags: ", Tags.objects.all())

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

    def test_query_fields(self):
        self.query_set_prepare_data()

        print("----------------test_query_fields--------------------")
        output(Tags.objects.filter(tag_name='tag test 1'))
        # like %查询%
        output(Tags.objects.filter(tag_name__contains='test'))
        # 忽略大小写 like
        output(Tags.objects.filter(tag_name__icontains='Test'))
        # like str%
        output(Tags.objects.filter(tag_name__startswith='tag'))
        # like %str
        output(Tags.objects.filter(tag_name__endswith='test 1'))
        # in
        output(Tags.objects.filter(tag_name__in=['tag test 1', 'tag test 2']))
        # and not
        output(Tags.objects.filter(tag_name__contains='test').exclude(tag_name='tag test 3').exclude(tag_name='tag test 2'))
        # =
        output(Tags.objects.filter(tag_name__exact='Of'))
        # like str 忽略大小写
        output(Tags.objects.filter(tag_name__iexact='Of'))
        # in
        output(Tags.objects.filter(id__in=[2, 3]))
        # >
        output(Tags.objects.filter(id__gt=2))
        # >=
        output(Tags.objects.filter(id__gte=2))
        # <
        output(Tags.objects.filter(id__lt=2))
        # <=
        output(Tags.objects.filter(id__lte=2))
        # is null
        output(Tags.objects.filter(tag_name__isnull=True))
        # is not null
        output(Tags.objects.filter(tag_name__isnull=False))
        output(Tags.objects.filter(tag_name__regex=r'^of$'))
        # output(Tags.objects.filter(tag_name__search=))

        # BETWEEN 1 AND 2
        output(Tags.objects.filter(id__range=[1, 2]))

        # django_datetime_cast_date("blog_post"."created_date", Asia/Shanghai, UTC) = 2015-01-01
        output(Tags.objects.filter(post__created_date__date=datetime.date(2024, 11, 26)))
        # django_datetime_cast_date("blog_post"."created_date", Asia/Shanghai, UTC) > 2015-01-01
        output(Tags.objects.filter(post__created_date__date__gt=datetime.date(2015, 1, 1)))

        # BETWEEN 2023-12-31 16:00:00 AND 2024-12-31 15:59:59.999999
        output(Post.objects.filter(created_date__year=2024))
        # > 2024-12-31 15:59:59.999999
        output(Post.objects.filter(created_date__year__gt=2024))
        # BETWEEN 2023-12-31 16:00:00 AND 2024-12-29 15:59:59.999999
        output(Post.objects.filter(created_date__iso_year=2024))

        # 月
        output(Post.objects.filter(created_date__month=11))
        # 月的天
        output(Post.objects.filter(created_date__day=26))
        # 周几
        output(Post.objects.filter(created_date__week_day=2))\
        # 周
        output(Post.objects.filter(created_date__week=2))
        # 季度
        output(Post.objects.filter(created_date__quarter=4))

        output(Post.objects.filter(created_date__time=datetime.time(16, 0)))
        output(Post.objects.filter(created_date__time__range=[datetime.time(16, 0), datetime.time(17, 0)]))
        # 取 0 到 23 之间的整数
        output(Post.objects.filter(created_date__hour=23))
        # 分 0-59
        output(Post.objects.filter(created_date__minute=19))
        # 取 0 到 59 之间的整数
        output(Post.objects.filter(created_date__second=19))

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

    def test_sql_raw(self):
        print("----------------test_sql_raw--------------------")
        # 执行一些操作
        instance = Tags.objects.create(tag_name='example', post=self.post)
        print(instance)

        # 获取并打印所有已执行的 SQL 查询
        for query in connection.queries:
            print(query['time'] + " -> " + query['sql'])

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