import logging

from django.contrib.auth.models import User
from django.test import TestCase

from apps.blog.models import Tags, Post


class TagsModelTest(TestCase):

    def setUp(self):
        super().setUp()

        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)
        # 查询所有Post
        print("posts: ", Post.objects.all())

    def test_create_tags(self):
        tags = Tags.objects.create(tag_name='tag test', post=self.post)
        print("tags: ", tags)

        tags_foo = Tags(tag_name='tag test foo', post=self.post)
        tags_foo.save()
        print("tags_foo: ", tags_foo)

        tmp = Tags.create_tags('tag b', self.post)
        print("tmp: ", tmp)

        tmp = Tags.objects.create_tag('tag bb', 1)
        print("tmp: ", tmp)

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

        row = Tags.objects.update(tag_name='barxxxxxxxx')
        print("tags_bar: ", row)
        tags_bar = Tags.objects.get(id=1)
        print("tags_bar: ", tags_bar)

    def test_delete_tags(self):
        tags = Tags.objects.create(tag_name='tag test', post=self.post)
        print("tags: ", tags)
        row = tags.delete()
        print(f"tags: {tags}, row: {row}")

        tags = Tags.objects.create(tag_name='tag delete', post=self.post)
        print(tags)
        row = Tags.objects.get(id=2).delete()
        print(f"tags: {tags}, row: {row}")

        Tags.objects.create(tag_name='tag remove 1', post=self.post)
        Tags.objects.create(tag_name='tag remove 2', post=self.post)

        tmp = Tags.objects.filter(tag_name='tag remove')
        # tmp = Tags.objects.all()
        print(f"tmp tags: {tmp}")
        row = tmp.delete()
        print(f"tags: {tmp.count()}, row: {row}")

        tmp = Tags.objects.all()
        print(f"tmp tags: {tmp}")

    def test_query_set(self):
        self.query_set_prepare_data()

        print("----------------objects--------------------")
        print(Tags.objects.get(id=2))
        print(Tags.objects.get(pk=2))
        print(Tags.objects.get(tag_name='tag test 1'))
        print(Tags.objects.first())
        print(Tags.objects.count())
        print(Tags.objects.values('tag_name', 'id').last())

        print("----------------all--------------------")
        print(Tags.objects.all())
        print(Tags.objects.all().first())
        print(Tags.objects.all().last())
        print(Tags.objects.all().get(id=2))
        print(Tags.objects.all().count())

        print("----------------filter--------------------")
        print(Tags.objects.filter(tag_name='tag test 1'))
        print(Tags.objects.filter(tag_name='tag test 1').first())
        print(Tags.objects.filter(tag_name='tag test 1').count())

        print(Tags.objects.filter(tag_name__startswith='tag test'))
        print(Tags.objects.filter(tag_name__contains='test').order_by('-id'))
        print(Tags.objects.filter(tag_name__in=['tag test 1', 'tag test 2']))

        print("----------------exclude--------------------")
        # 排除
        print(Tags.objects.exclude(tag_name='tag test 1'))

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
        print(foo.query)
        print("bar: ", bar)
        print(bar.query)

        # 交集
        print(foo.union(bar))
        # 差集
        print(foo.intersection(bar))
        # 并集
        print(bar.difference(foo))

        # print(foo.symmetric_difference(bar))
        print(foo.count())

    def test_query_func(self):
        self.query_set_prepare_data()

        print("----------------test_query_func--------------------")
        foo = Tags.objects.all()

        print(foo.distinct())
        print(foo.reverse())
        print(foo.count())

    def test_query_range(self):
        self.query_set_prepare_data()

        print("----------------test_query_range--------------------")
        print(Tags.objects.all()[:3])
        print(Tags.objects.all()[1:3])

        # 步长取值
        print(Tags.objects.all()[:3:2])
        print(Tags.objects.all()[:5:2])
        # print(Tags.objects.all()[-2]) # ERROR

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
        print(Tags.objects.filter(tag_name='tag test 1'))
        print(Tags.objects.filter(tag_name__contains='test'))

    def query_set_prepare_data(self):
        Tags.objects.create(tag_name='tag test 1', post=self.post)
        Tags.objects.create(tag_name='tag test 2', post=self.post)
        Tags.objects.create(tag_name='tag test 3', post=self.post)
        Tags.objects.create(tag_name='tag test 4', post=self.post)
        Tags.objects.create(tag_name='tag test 4', post=self.post)

        Tags.objects.create(tag_name='Returning HTTP', post=self.post)
        Tags.objects.create(tag_name='error codes', post=self.post)
        Tags.objects.create(tag_name='in Django is easy', post=self.post)
        Tags.objects.create(tag_name='There are subclasses', post=self.post)
        Tags.objects.create(tag_name='of HttpResponse', post=self.post)
        print("prepare data: ", Tags.objects.all())