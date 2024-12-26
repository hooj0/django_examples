import datetime

from django.contrib.auth.models import User
from django.db import reset_queries
from django.db.models import Q, F, Value, JSONField, Count, CharField, Exists, OuterRef, ExpressionWrapper, DateTimeField, BooleanField, Func
from django.db.models.fields.json import KT
from django.db.models.functions import Upper, Length, Lower
from django.db.models.lookups import GreaterThan

from apps.blog.models import Tags, Post, Book, Comment
from apps.blog.tests.tests import BasedTestCase, output_sql, output


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
        # not !=
        output(Tags.objects.filter(~Q(tag_name__exact='Of')))
        output(Tags.objects.exclude(tag_name__exact='Of'))
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
        output(Post.objects.filter(created_date__week_day=2))
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

    def test_filter_f_func(self):
        """
        F 表达式：
            - 将模型字段值与同一模型中的另一字段做比较
            - 使用加法、减法、乘法、除法、取模和幂算术，既可以与常数一起使用，也可以与其他 F() 对象一起使用
        https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#django.db.models.F
        """
        # 比较两个字段
        # WHERE "blog_tags"."id" > ("blog_tags"."post_id")
        output_sql(Tags.objects.filter(id__gt=F('post__id')))
        # WHERE "blog_post"."created_date" > ("blog_post"."published_date")
        output_sql(Post.objects.filter(created_date__gt=F('published_date')))

        # 加减乘除数值运算
        #  WHERE "blog_book"."price" = (CAST(("blog_book"."price" + 1) AS NUMERIC))
        output_sql(Book.objects.filter(price=F('price') + 1))
        output_sql(Book.objects.filter(price=F('price') + F('price')))

        # 支持跨表字段
        # WHERE "blog_book"."title" = ("blog_author"."name")
        output_sql(Book.objects.filter(title=F('author__name')))

        # 更新，字段进行赋值操作
        output_sql(Post.objects.filter(id=1).update(published_date=F('created_date')))

        # 日期操作
        output_sql(Post.objects.filter(created_date__gt=F('published_date') + datetime.timedelta(days=3)))
        output_sql(Post.objects.filter(created_date__year=F('published_date__year')))

        # 更新操作应用表达式
        post = Post.objects.get(id=1)
        post.published_date = F("published_date") + 1
        output_sql(post.save())

        post.refresh_from_db()
        post.content = F("content")[1:4] + "test"
        output_sql(post.save())

        post.refresh_from_db()
        print(post.content)

        post = Post.objects.filter(id=1)
        output_sql(post.update(created_date=F("published_date")))

        # output_sql(Post.objects.annotate(expires=ExpressionWrapper(F("published_date") - F("created_date"), output_field=DateTimeField())))

        # 空值排序
        # ORDER BY "blog_post"."published_date" DESC NULLS LAST
        output_sql(Post.objects.order_by(F("published_date").desc(nulls_last=True)))

        # 逻辑判断
        # WHERE "blog_post"."status" = (NOT "blog_post"."status")
        output_sql(Post.objects.filter(status=~F('status')))
        output_sql(Post.objects.filter(~Q(status=True)))

        # WHERE "blog_post"."status" = (NOT 1)
        output_sql(Post.objects.filter(status=~Value(False, output_field=BooleanField())))

    def test_filter_q_func(self):
        """
        通过 Q 对象完成复杂查询¶
        Q 对象可以使用 &、| 和 ^ 运算符组合。当在两个 Q 对象上使用运算符时，它会产生一个新的 Q 对象。
        https://docs.djangoproject.com/zh-hans/5.1/topics/db/queries/#complex-lookups-with-q-objects
        """
        output_sql(Q(a__b__startswith='foo')) # (AND: ('a__b__startswith', 'foo'))
        output_sql(Q(a__b__startswith='foo') | Q(a__b__startswith='bar')) # (OR: ('a__b__startswith', 'foo'), ('a__b__startswith', 'bar'))
        output_sql(Q(a__b__startswith='foo') & Q(a__b__startswith='bar')) # (AND: ('a__b__startswith', 'foo'), ('a__b__startswith', 'bar'))
        output_sql(Q(a__b__startswith='foo') ^ Q(a__b__startswith='bar')) # (XOR: ('a__b__startswith', 'foo'), ('a__b__startswith', 'bar'))
        output_sql(Q(a__b__startswith='foo') | ~Q(a__b__startswith='bar')) # (OR: ('a__b__startswith', 'foo'), (NOT (AND: ('a__b__startswith', 'bar'))))
        output_sql(~(Q(a__b__startswith='foo') & Q(a__b__startswith='bar'))) # (NOT (AND: ('a__b__startswith', 'foo'), ('a__b__startswith', 'bar')))

        # 组合
        author_queries = [Q(name__startswith="J"), Q(name__startswith="K")]
        print(Q(*author_queries, _connector=Q.OR))

        # 多条件组合查询
        # WHERE ("blog_post"."title" LIKE 'Who%' ESCAPE '\'
        # AND (django_datetime_cast_date("blog_post"."published_date", 'Asia/Shanghai', 'UTC') = '2024-05-02'
        # OR django_datetime_cast_date("blog_post"."published_date", 'Asia/Shanghai', 'UTC') = '2024-05-06'))
        output_sql(Post.objects.filter(Q(title__startswith="Who"),
                         Q(published_date__date=datetime.date(2024, 5, 2))
                        | Q(published_date__date=datetime.date(2024, 5, 6))))

        output_sql(Post.objects.filter(Q(published_date__date=datetime.date(2024, 5, 2))
                                       | Q(published_date__date=datetime.date(2024, 5, 6)),
                                       title__startswith="Who"))
        # Q 条件查询需排最前面
        # 无法通过
        # output_sql(Post.objects.filter(title__startswith="Who", Q(published_date__date=datetime.date(2024, 5, 2)) | Q(published_date__date=datetime.date(2024, 5, 6)))

        # 动态查询
        case = 10
        query = Q(title="Who")
        if case > 1:
            query &= Q(title__startswith="Who")
        if case > 2:
            query |= Q(published_date__date=datetime.date(2024, 5, 2))
        if case > 3:
            query ^= Q(created_date__date=datetime.date(2024, 5, 6))

        output_sql(Post.objects.filter(query))

    def test_filter_json(self):
        """
        https://docs.djangoproject.com/zh-hans/5.1/topics/db/queries/#querying-jsonfield
        """
        # json 插入字典数据
        output_sql(Comment.objects.create(post=self.post, email="jack@qq.com", json={"name": "test", "age": 18}))

        # 插入空值
        output_sql(Comment.objects.create(post=self.post, email="tom@qq.com", json=None)) # SQL Null
        output_sql(Comment.objects.create(post=self.post, email="k@qq.com", json=Value(None, JSONField()))) # JSON null

        output_sql(Comment.objects.filter(json=None).values_list("email")) # <QuerySet [('k@qq.com',)]>
        output_sql(Comment.objects.filter(json=Value(None, JSONField())).values_list("email")) # <QuerySet [('k@qq.com',)]>
        output_sql(Comment.objects.filter(json__isnull=True).values_list("email")) # <QuerySet [('tom@qq.com',)]>
        output_sql(Comment.objects.filter(json__isnull=False).values_list("email")) # <QuerySet [('jack@qq.com',), ('k@qq.com',)]>

        output_sql(Comment.objects.create(post=self.post, email="jack@qq.com", json={"name": "kki", "age": 18, "owner": {
            "name": "bull",
            "pets": [
                {"name": "dog", "age": 2},
                {"name": "cat", "age": 3}
            ]
        }}))
        # 查找JSON对象
        output_sql(Comment.objects.filter(json__age=18))
        output_sql(Comment.objects.filter(json__owner__name="bull"))
        output_sql(Comment.objects.filter(json__owner__pets__1__name="cat"))
        output_sql(Comment.objects.filter(json__owner__isnull=False))

        output_sql(Comment.objects.create(post=self.post, email="lee@qq.com", json={"name": "kki", "age": 18,
            "owner": {
                "name": "bull"
            },
            "pets": [
                "cat", "dog"
            ]}))
        # KT 表达式
        output_sql(Comment.objects.annotate(a=KT('json__pets__1__name'), b=KT('json__owner__name')).filter(a__startswith='d', b='bull'))

        # contains (Oracle 和 SQLite 不支持 contains )
        # output_sql(Comment.objects.filter(json__contains={"name": "kki"}))

        # contained_by (Oracle 和 SQLite 不支持 contains )
        # output_sql(Comment.objects.filter(json__contained_by={"name": "kki", "age": 18}))

        # 查找JSON对象键
        output_sql(Comment.objects.filter(json__has_key='age'))
        output_sql(Comment.objects.filter(json__has_keys=['name', 'age']))
        output_sql(Comment.objects.filter(json__has_keys=['name', 'b'])) # empty
        output_sql(Comment.objects.filter(json__has_any_keys=['name', 'a', 'b']))

    def test_filter_expression(self):
        """
        查询表达式
        https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#
        表达式API参考
        https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#expression-api
        编写自定义查询表达式
        https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#writing-your-own-query-expressions
        """
        # 创建时使用表达式
        company = output_sql(Post.objects.create(title="Google", content=Upper(Value("goog")), author=self.user))
        # 如果需要访问该字段，请务必刷新它。
        company.refresh_from_db()
        print(company.content) # 在不刷新情况输出 Upper(Value('goog'))

        # 效果一致
        output_sql(Post.objects.annotate(num_tags=Count("tags")))
        output_sql(Post.objects.annotate(num_tags=Count(F("tags"))))

        # 根据字符串长度排序
        # ORDER BY LENGTH("blog_post"."title") ASC
        output_sql(Post.objects.order_by(Length("title").asc()))
        output_sql(Post.objects.order_by(Length("title").desc()))

        # 注册查找api，支持排序/查找
        CharField.register_lookup(Length)
        # ORDER BY LENGTH("blog_post"."title") ASC
        output_sql(Post.objects.order_by("title__length"))
        #  WHERE LENGTH("blog_post"."title") > 2
        output_sql(Post.objects.filter(title__length__gt=2))

        # 子查询
        # WHERE EXISTS(SELECT 1 AS "a" FROM "blog_tags" U0 WHERE U0."post_id" = ("blog_post"."id") LIMIT 1)
        output_sql(Post.objects.filter(Exists(Tags.objects.filter(post=OuterRef("pk")))))
        output_sql(Post.objects.filter(Exists(Tags.objects.filter(post=OuterRef("pk"), tag_name__contains="test"))))

        # 比较
        # WHERE "blog_post"."published_date" > ("blog_post"."created_date")
        output_sql(Post.objects.filter(GreaterThan(F("published_date"), F("created_date"))))

        # 支持列表达式
        # ... "blog_post"."status", "blog_post"."published_date" > ("blog_post"."created_date") AS "need_chairs" FROM "blog_post"
        output_sql(Post.objects.annotate(
            need_chairs=GreaterThan(F("published_date"), F("created_date")),
        ))

    def test_filter_func(self):
        """
        函数表达式
            https://docs.djangoproject.com/zh-hans/5.1/ref/models/expressions/#django.db.models.Func
        示例教程：
            https://lxblog.com/qianwen/share?shareId=c160d16c-c094-4bfc-8d29-a88ad8d54393
        支持数据库函数：
            https://docs.djangoproject.com/zh-hans/5.1/ref/models/database-functions/
        """
        # LOWER("blog_post"."title") AS "field_lower" FROM "blog_post"
        output_sql(Post.objects.annotate(field_lower=Lower("title")))
        output_sql(Post.objects.annotate(field_lower=Lower(F("title"))))

        # OWER("blog_post"."title") AS "field_lower" FROM "blog_post"
        output_sql(Post.objects.annotate(field_lower=Func("title", function="LOWER")))
        output_sql(Post.objects.annotate(field_lower=Func(F("title"), function="LOWER")))

        # 自定义函数表达式
        class MyLower(Func):
            function = "LOWER"

        output_sql(Post.objects.annotate(field_lower=MyLower("title")))
        output_sql(Post.objects.annotate(field_lower=MyLower(F("title"))))

        class MyFunc(Func):
            function = "UPPER"
            template = "%(function)s(%(expressions)s)"
            arg_joiner = " "
            arity = 1
            output_field = CharField()

            def as_sqlite(self, compiler, connection, **extra_context):
                return super().as_sql(
                    compiler,
                    connection,
                    function="UP_WS",
                    template="%(function)s('', %(expressions)s)",
                    **extra_context
                )

        output_sql(Post.objects.annotate(field_func=MyFunc("title")))

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
