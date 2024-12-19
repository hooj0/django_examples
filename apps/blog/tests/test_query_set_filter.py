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
