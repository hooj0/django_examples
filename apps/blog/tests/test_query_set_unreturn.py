from datetime import date

from django.contrib.auth.models import User
from django.db import reset_queries
from django.db.models import Q

from apps.blog.models import Tags, Post, Book, Author, faker, Publisher, Topping, Pizza, Restaurant
from apps.blog.tests.tests import BasedTestCase, output_sql, sql_decorator


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

    def test_operator(self):
        print("----------------operator--------------------")
        # and
        # WHERE ("blog_post"."id" = 1 AND "blog_post"."title" LIKE '%test%' ESCAPE '\')
        output_sql(Post.objects.filter(id=1) & Post.objects.filter(title__contains='test'))

        # or
        # WHERE ("blog_post"."id" = 1 OR "blog_post"."title" LIKE '%test%' ESCAPE '\')
        output_sql(Post.objects.filter(id=1) | Post.objects.filter(title='test'))

        # xor
        # WHERE (("blog_post"."id" = 1 OR "blog_post"."title" = 'test')
        # AND 1 = (CASE WHEN "blog_post"."id" = 1 THEN 1 ELSE 0 END + CASE WHEN "blog_post"."title" = 'test' THEN 1 ELSE 0 END))
        output_sql(Post.objects.filter(id=1) ^ Post.objects.filter(title='test'))

    def test_query_set_get(self):
        print("----------------get--------------------")
        output_sql(Tags.objects.get(id=2))
        output_sql(Tags.objects.get(pk=2))
        output_sql(Tags.objects.get(tag_name='tag test 1'))

        post = Post.objects.get(id=1)
        # WHERE ("blog_tags"."post_id" = 1 AND "blog_tags"."tag_name" = 'tag test 1')
        output_sql(Tags.objects.get(Q(post=post) & Q(tag_name='tag test 1')))

        output_sql(Tags.objects.filter(tag_name='tag test 1').get())

    @sql_decorator
    def test_get_or_create(self):
        """
        获取或者创建对象
        get_or_create(defaults=None, **kwargs)
        """
        print("----------------get_or_create--------------------")

        try:
            obj = Tags.objects.get(tag_name='test', post=self.post)
        except Tags.DoesNotExist:
            obj = Tags(tag_name='test', post=self.post)
            obj.save()

        # 和上面有同样效果，且带事务处理
        data, created = Tags.objects.get_or_create(tag_name='test2', post=self.post)
        print(data, created)  # id: 13, tag_name: test2, post_id: 1    True

        # created 已经创建
        data, created = Tags.objects.get_or_create(tag_name='test2', post=self.post)
        print(data, created)  # id: 13, tag_name: test2, post_id: 1    False

        # defaults 带默认值，先过滤匹配数据，如果没有就创建
        # WHERE (("blog_tags"."tag_name" = 'test 1' OR "blog_tags"."tag_name" = 'test 2') AND "blog_tags"."post_id" = 1)
        data, created = Tags.objects.filter(
            Q(tag_name="test 1") | Q(tag_name="test 2"),
        ).get_or_create(post=self.post, defaults={"tag_name": "my tag"})
        print(data, created)

    @sql_decorator
    def test_update_or_create(self):
        """
        update_or_create(defaults=None, create_defaults=None, **kwargs)
        更新或者创建对象，
            defaults 用于更新对象，而 create_defaults 用于创建操作。
            如果未提供 create_defaults，则将使用 defaults 进行创建操作。
        """
        print("----------------update_or_create--------------------")

        case = 3
        if case == 1:
            # id: 12, title: test, content: content is****, created_date: 2024-12-18 08:12:38.768229+00:00, published_date: 2024-12-18 08:12:38.768240+00:00, image: , author_id: 1, status: False =====>>>>>> True
            data, created = Post.objects.update_or_create(
                title="test",
                content="content is a b",
                author=self.user,
                defaults={"status": True},
                create_defaults={"status": False, "published_date": date(1940, 10, 9)},
            )
        elif case == 2:
            # create_defaults 或 defaults 会覆盖key arguments数据
            # id: 12, title: test, content: hahahhahah**, created_date: 2024-12-18 08:11:34.034023+00:00, published_date: 2024-12-18 08:11:34.034034+00:00, image: , author_id: 1, status: False =====>>>>>> True
            data, created = Post.objects.update_or_create(
                title="test",
                content="content is a b",
                author=self.user,
                defaults={"status": False, "content": "hahahhahahha"},
            )
        else:
            # id: 12, title: test 111, content: 1111111, created_date: 2024-12-18 08:16:25.987899+00:00, published_date: 2024-12-18 08:16:25.988649+00:00, image: , author_id: 1, status: False =====>>>>>> False
            Post.objects.create(
                title="test 111",
                content="content is a b",
                author=self.user
            )
            # 先根据条件进行查询，没有就创建，有就修改
            # SELECT * FROM "blog_post" WHERE ("blog_post"."author_id" = 1 AND "blog_post"."content" = 'content is a b' AND "blog_post"."title" = 'test 111') LIMIT 21
            # 整条数据更新
            # UPDATE "blog_post" SET "content" = '1111111', "created_date" = '2024-12-18 08:16:25.987899', "published_date" = '2024-12-18 08:16:25.988649', "image" = '', "status" = 0 WHERE "blog_post"."id" = 12
            data, created = Post.objects.update_or_create(
                title="test 111",
                content="content is a b",
                author=self.user,
                defaults={"status": False, "content": "1111111"}
            )
        print(data, "=====>>>>>>", created)

    @sql_decorator
    def test_bulk_create(self):
        """
        bulk_create(objs, batch_size=None, ignore_conflicts=False, update_conflicts=False, update_fields=None, unique_fields=None)
        批量更新，以与提供的顺序相同的顺序返回已创建的对象列表
            batch_size 一次性插入数量
            ignore_conflicts 设置为 True 告诉数据库忽略插入失败的行
            update_conflicts 设置为 True 告诉数据库忽略更新失败的行
            update_fields 发生冲突时应该更新哪些字段
            unique_fields 唯一的字段属性，检测冲突的唯一字段
        显示设置主键的优先插入或更新
        """
        print("----------------bulk_create--------------------")
        data = [
            Tags(tag_name='tag test 1', post=self.post),
            Tags(tag_name='tag test 2', post=self.post),
            Tags(tag_name='tag test 3', post=self.post, id=222),
            Tags(tag_name='tag test 4', post=self.post),
            Tags(tag_name='tag test 5', post=self.post, id=111),
        ]
        # 一次性插入
        # Tags.objects.bulk_create(data)
        # 分批插入
        # Tags.objects.bulk_create(data, batch_size=2)

        data = [
            Tags(tag_name='tag test 1', post=self.post, id=1),
            Tags(tag_name='tag test 2', post=self.post, id=2),
            Tags(tag_name='tag test 3', post=self.post, id=222),
            Tags(tag_name='tag test 4', post=self.post),
            Tags(tag_name='tag test 5', post=self.post, id=111),
        ]
        # 插入时主突会忽略，继续插入
        # rs = Tags.objects.bulk_create(data, ignore_conflicts=True)

        # 插入时冲突会更新
        rs = Tags.objects.bulk_create(data, update_conflicts=True, update_fields=['tag_name', 'post'], unique_fields=['id'])
        print(rs)

    @sql_decorator
    def test_bulk_update(self):
        """
        bulk_update(objs, fields, batch_size=None)
        这个方法高效地更新提供的模型实例上的给定字段，通常只需一个查询，并返回更新的对象数量
        """
        print("----------------bulk_update--------------------")

        data = [
            Tags(tag_name='tag test 1', post=self.post, id=1),
            Tags(tag_name='tag test 2', post=self.post, id=2),
            Tags(tag_name='tag test 3', post=self.post, id=222),
            Tags(tag_name='tag test 4', post=self.post, id=3),
            Tags(tag_name='tag test 5', post=self.post, id=111),
        ]
        # 批量更新必须有主键
        Tags.objects.bulk_update(data, ['tag_name'], batch_size=2)

        # 主键字段不能更新
        # Tags.objects.bulk_update(data, ['tag_name', 'id'], batch_size=2)

    def test_in_bulk(self):
        """
        in_bulk(id_list=None, *, field_name='pk')
        接收一个字段值的列表（id_list）和这些值的 field_name，并返回一个字典，将每个值映射到具有给定字段值的对象实例
        相当于 key-map，key 存主键数据，map 是对应的对象
        field_name 必须是唯一约束字段
        """
        print("----------------in_bulk--------------------")
        # {1: <Tags: _state: unknown, id: 1, tag_name: tag test 1, post_id: 1>, 2: <Tags: _state: unknown, id: 2, tag_name: tag Test 2, post_id: 1>}
        output_sql(Tags.objects.in_bulk([1, 2]))

        # 不传参数查询所有
        output_sql(Tags.objects.in_bulk())
        # field_name 必须是唯一约束字段
        output_sql(Post.objects.in_bulk(["this is post."], field_name='title'))

    def test_iterator(self):
        """
        iterator(chunk_size=None)
        迭代器方式查询，一次性不使用缓存
        """
        print("----------------iterator--------------------")

        case = 3
        if case == 1:
            iter = output_sql(Tags.objects.iterator())
            for element in iter:
                print(element)

        elif case == 2:
            # 处理5条，降低内存消耗
            for element in output_sql(Tags.objects.iterator(chunk_size=5)):
                print(element)

        elif case == 3:
            # 结合过滤器迭代
            for element in output_sql(Tags.objects.filter(tag_name__contains="o").iterator(chunk_size=3)):
                print(element)

    def test_latest(self):
        """
        根据给定的字段，返回表中最新的对象
        按照这个字段倒序后的第一个对象
        """
        print("----------------latest--------------------")
        output_sql(Tags.objects.latest('id'))
        output_sql(Tags.objects.latest('tag_name'))

        # 指定排序方式
        output_sql(Post.objects.latest('title', '-published_date'))

    def test_simple_func(self):
        # ORDER BY "blog_tags"."id" ASC LIMIT 1
        output_sql(Tags.objects.first())
        # ORDER BY "blog_tags"."id" DESC LIMIT 1
        output_sql(Tags.objects.last())
        output_sql(Tags.objects.values('tag_name', 'id').last())

        # COUNT(*)
        output_sql(Tags.objects.count())
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
