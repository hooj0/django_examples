from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db import reset_queries
from django.db.models import F, ExpressionWrapper, DecimalField, Prefetch
from django.db.models.aggregates import Count, Avg, Sum
from django.db.models.functions import Lower
from django.db.models.query import EmptyQuerySet
from django.utils import timezone

from apps.blog.models import Tags, Post, Book, Author, faker, Publisher, Topping, Pizza, Restaurant
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output
from common.util.utils import object_to_string


class QuerySetTest(BasedTestCase):
    """
    返回QuerySet部分：
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/querysets/#methods-that-return-new-querysets
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

    def test_query_introduce(self):
        print("----------------iterator-----------------")
        # 第一次迭代进行查询，后续查询使用缓存
        for item in output_sql(Tags.objects.all()):
            print(item)

        # 切片会返回新的 QuerySet
        # repr、len、list 会执行QuerySet
        print(repr(Tags.objects.all()))
        print(len(Tags.objects.all()))
        print(list(Tags.objects.all()))

        # if 会执行 QuerySet
        if Tags.objects.filter(tag_name='tag test 1'):
            print("There is at least one Tag with the name 'tag test 1'")

        if Tags.objects.filter(tag_name='tag test 1222'):
            print("There is at least one Tag with the name 'tag test 1'")

    def test_query_set_basic(self):
        print("----------------base--------------------")
        queryset = output_sql(Tags.objects.all())
        output_sql(Tags.objects) # blog.Tags.objects
        print(Tags.objects == queryset) # False

        print(type(Tags.objects)) # <class 'django.db.models.manager.Manager'>
        print(type(queryset))     # <class 'django.db.models.query.QuerySet'>

        print(queryset.ordered)     # False
        print(queryset.db)          # default
        print(object_to_string(queryset))

    def test_query_set_all(self):
        print("----------------all--------------------")
        output_sql(Tags.objects.all())
        # ORDER BY "blog_tags"."id" ASC LIMIT 1
        output_sql(Tags.objects.all().first())
        # ORDER BY "blog_tags"."id" DESC LIMIT 1
        output_sql(Tags.objects.all().last())
        output_sql(Tags.objects.all().get(id=2))
        # COUNT(*)
        output_sql(Tags.objects.all().count())

    def test_query_set_filter(self):
        print("----------------filter--------------------")
        output_sql(Tags.objects.filter(tag_name='tag test 1'))
        output_sql(Tags.objects.filter(tag_name='tag test 1').first())
        output_sql(Tags.objects.filter(tag_name='tag test 1').count())

        output_sql(Tags.objects.filter(tag_name__startswith='tag test'))
        # -id 倒序， ORDER BY "blog_tags"."id" DESC
        output_sql(Tags.objects.filter(tag_name__contains='test').order_by('-id'))
        output_sql(Tags.objects.filter(tag_name__in=['tag test 1', 'tag test 2']))

    def test_query_set_exclude(self):
        print("----------------exclude--------------------")
        # 排除 NOT ("blog_tags"."tag_name" = 'tag test 1')
        output_sql(Tags.objects.exclude(tag_name='tag test 1'))
        # NOT ("blog_tags"."id" > 2 AND "blog_tags"."tag_name" = 'tag test 1')
        output_sql(Tags.objects.exclude(tag_name='tag test 1', id__gt=2))
        # (NOT ("blog_tags"."tag_name" = 'tag test 1') AND NOT ("blog_tags"."id" > 2))
        output_sql(Tags.objects.exclude(tag_name='tag test 1').exclude(id__gt=2))

    def test_query_set_alias(self):
        """
        允许你为表达式创建别名，这些别名可以在后续的查询中重复使用。这可以简化复杂的查询，并提高可读性。
        """
        print("----------------alais--------------------")
        discounted_price_exp = ExpressionWrapper(
            F('price') * (1 - F('price')), output_field=DecimalField()
        )
        # (CAST((CAST(("blog_book"."price" * (CAST((1 - "blog_book"."price") AS NUMERIC))) AS NUMERIC)) AS NUMERIC)) < '10'
        books = Book.objects.alias(discounted_price=discounted_price_exp).filter(discounted_price__lt=10.00)
        output_sql(books)

        # 首先为每个作者的书籍平均价格创建别名
        author_avg_price = Avg('book__price')
        # 然后使用这个别名来过滤和分组
        top_authors = Author.objects.alias(avg_price=author_avg_price).filter(avg_price__gt=4.5)
        output_sql(top_authors)

    def test_query_set_orderby(self):
        """
        默认情况下，QuerySet 返回的结果是按照模型 Meta 中的 ordering 选项给出的排序元组排序的
        """
        print("----------------order by--------------------")
        # ORDER BY "blog_book"."id" DESC
        output_sql(Book.objects.order_by('-id'))
        # ORDER BY "blog_book"."id" DESC, "blog_book"."price" ASC
        output_sql(Book.objects.order_by('-id', 'price'))
        # 随机排序，可能有性能损耗
        output_sql(Book.objects.order_by('?')) # ORDER BY RAND() ASC
        # ORDER BY "blog_author"."name" ASC, "blog_book"."price" ASC
        output_sql(Book.objects.order_by('author__name', 'price'))

        # 按照关联模型排序
        output_sql(Book.objects.order_by('author'))
        output_sql(Book.objects.order_by('author__id')) # 和上面同样效果，取决于 Book 的 Meta 排序ordering设置

        # 用查询表达式排序，asc() 和 esc() 有参数（nulls_first 和 nulls_last）来控制如何对空值进行排序
        # output_sql(Book.objects.order_by(Coalesce('summary', 'price').desc()))
        # 对空值排序，控制排在后面
        output_sql(Book.objects.order_by(F('price').desc(nulls_last=True)))
        # ORDER BY LOWER("blog_book"."title") DESC
        output_sql(Book.objects.order_by(Lower('title').desc()))

        # 不想在查询中应用任何排序，甚至是默认的排序
        output_sql(Book.objects.order_by())

        # order_by('price') 会覆盖 order_by('id')
        output_sql(Book.objects.order_by('id').order_by('price'))

    def test_query_set_reverse(self):
        """
        反转已经排序好的查询集，不会修改原始的排序条件
        使用 reverse() 方法来反向返回查询集元素的顺序；第二次调用 reverse() 会将顺序恢复到正常方向
        需要建立在有序集合上
        """
        print("----------------reverse--------------------")
        # 查询结果集中的“最后”五个项目
        output_sql(Book.objects.order_by('-id').reverse()[:5]) # ORDER BY "blog_book"."id" ASC LIMIT 5
        # 从 ASC 顺序变为 DESC
        output_sql(Book.objects.order_by('price').reverse())
        output_sql(Book.objects.order_by('author', 'price').reverse())

    def test_query_set_distinct(self):
        """
        返回一个新的 QuerySet，在其 SQL 查询中使用 SELECT DISTINCT
        """
        print("----------------distinct--------------------")
        # SELECT DISTINCT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book"
        output_sql(Book.objects.distinct())
        output_sql(Book.objects.filter(price__gt=10).distinct())

        # SELECT DISTINCT "blog_book"."title", "blog_book"."price" FROM "blog_book"
        output_sql(Book.objects.values("title", "price").distinct())

        # 以下代码只能在PostgreSQL执行
        # Book.objects.order_by('price').distinct('price')
        # Book.objects.order_by("author").distinct("author")
        # Book.objects.order_by("author", "pub_date").distinct("author", "pub_date")
        # Book.objects.order_by("blog__name", "mod_date").distinct("blog__name", "mod_date")
        # Book.objects.order_by("author", "pub_date").distinct("author")

    def test_query_set_values(self):
        """
        返回一个 QuerySet，当用作可迭代对象时，返回字典，而不是模型实例。
        其中每一个字典都代表一个对象，键与模型对象的属性名相对应。
        """
        print("----------------values--------------------")
        # 关联的model对象
        # <QuerySet [{'id': 1, 'title': 'Mock Book Lisa Smith', 'price': Decimal('459.01'), 'author_id': 1}
        output_sql(Book.objects.values())
        # 返回字典数据 {}
        # <QuerySet [{'title': 'Mock Book Daniel Peters', 'price': Decimal('677.54')} ...>
        output_sql(Book.objects.values('title', 'price'))

        # 关联查询
        # <QuerySet [{'title': 'Mock Book Amanda Ibarra MD', 'price': Decimal('-403.21'), 'author__name': 'tom'}...>
        output_sql(Book.objects.values('title', 'price', 'author__name'))

        # 设置key 为自定义 别名
        # SELECT LOWER("blog_book"."title") AS "name", (CAST(SUM("blog_book"."price") AS NUMERIC)) AS "book_price" FROM "blog_book" GROUP BY "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id", 1 LIMIT 21
        # <QuerySet [{'name': 'mock book mary nichols', 'book_price': Decimal('-259.170000000000')} ...
        output_sql(Book.objects.values(name=Lower('title'), book_price=Sum('price')))

        # 关联并分组
        # SELECT "blog_author"."user_id", COUNT("blog_book"."author_id") AS "entries" FROM "blog_book"
        # <QuerySet [{'author__user': 1, 'entries': 10}]>
        output_sql(Book.objects.values("author__user", entries=Count("author")))
        output_sql(Book.objects.values("author__user").annotate(entries=Count("author")))

        # 两者效果一样
        output_sql(Book.objects.values("author"))
        output_sql(Book.objects.values("author_id"))

        output_sql(Book.objects.values().order_by("id"))
        output_sql(Book.objects.order_by("id").values())

    def test_query_set_values_list(self):
        """
        与 values() 类似，不同之处在于在迭代时，它返回元组而不是字典
        """
        print("----------------values_list--------------------")
        # 按照声明的顺序返回模型中的所有字段，以元组形式
        # <QuerySet [(1, 'Mock Book Michael Gutierrez', Decimal('507.00'), 1)...
        output_sql(Book.objects.values_list())
        # <QuerySet [(1, 'Mock Book Michael Gutierrez', 'Mock Author johnsonchristopher')
        output_sql(Book.objects.values_list("id", "title", "author__name"))

        # 返回一个值的元组
        # <QuerySet [(1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,), (10,)]>
        output_sql(Book.objects.values_list("id").order_by("id"))

        # 返回集合，flat 参数（不支持多个字段）
        # <QuerySet [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]>
        output_sql(Book.objects.values_list("id", flat=True).order_by("id"))

        # 返回多行Row -> namedtuple() ，named 参数 底层对象转换有性能损耗，相较于元组
        # <QuerySet [Row(id=1, price=Decimal('754.64')), Row(id=2, price=Decimal('-914.63')),
        output_sql(Book.objects.values_list("id", "price", named=True).order_by("id"))

        # 取特定值
        id, price = output_sql(Book.objects.values_list("id", "price").get(id=1))
        print(id, "----", price)
        title = output_sql(Book.objects.values_list("title", flat=True).get(id=1))
        print(title)

        # 多对一，会存在重复name
        output_sql(Author.objects.values_list("name", "book__title"))

        # <QuerySet [(1,), (1,), (1,), (1,)
        output_sql(Book.objects.values_list("author"))

    def test_query_set_date(self):
        print("----------------date--------------------")
        """
        date() 返回一个 QuerySet，其中包含所有日期字段，并且只包含日期部分，而不是时间部分。
        值是一个 datetime.date 对象的列表，代表 QuerySet 内容中所有可用的特定日期
        """
        # <QuerySet [datetime.date(2024, 12, 14)]>
        output_sql(Post.objects.dates("created_date", "day"))

        # <QuerySet [datetime.date(2024, 1, 1)]>
        output_sql(Post.objects.dates("created_date", "year"))

        # <QuerySet [datetime.date(2024, 12, 1)]>
        output_sql(Post.objects.dates("created_date", "month"))

        # <QuerySet [datetime.date(2024, 12, 9)]>
        output_sql(Post.objects.dates("created_date", "week"))

        # 排序
        output_sql(Post.objects.dates("created_date", "day", order="DESC"))

        output_sql(Post.objects.filter(published_date__year=2024).dates("created_date", "day", order="DESC"))

        print("----------------datetimes--------------------")
        """
        值是一个 datetime.datetime 对象的列表
        kind 应该是 "year"、"month"、"week"、"day"、"hour"、"minute" 或 "second"
        """
        output_sql(Post.objects.datetimes("created_date", "day"))
        # <QuerySet [datetime.datetime(2024, 12, 14, 16, 40, 17, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai'))]>
        output_sql(Post.objects.datetimes("created_date", "second"))
        # <QuerySet [datetime.datetime(2024, 12, 14, 16, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai'))]>
        output_sql(Post.objects.datetimes("created_date", "hour", order="DESC", tzinfo=timezone.get_current_timezone()))

    def test_query_set_none(self):
        """
        返回 空对象
        """
        print("----------------none--------------------")
        # <QuerySet []>
        output_sql(Book.objects.none())
        output_sql(isinstance(Book.objects.none(), EmptyQuerySet)) # True

    @sql_decorator
    def test_query_chain(self):
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
        print("----------------test_query_collection--------------------")
        foo = Tags.objects.filter(tag_name__endswith='test 1')
        bar = Tags.objects.filter(tag_name__contains='test').exclude(tag_name='tag test 3').exclude(tag_name='tag test 2')
        bar2 = Tags.objects.filter(tag_name__contains='t')
        print("foo: ", foo)
        print("bar: ", bar)
        print("bar: ", bar2)

        # 交集 UNION
        # UNION 操作符默认只选择不同的值。要允许重复的值，使用 all=True 参数
        print("----------------------union---------------------")
        output(foo.union(bar))
        output(foo.union(bar, bar2))
        # 允许重复值
        output(foo.union(bar, bar2, all=True))

        # 支持不同model的相同列数量和类型进行交集
        books = Book.objects.values("title")
        authors = Author.objects.values("name")
        # SELECT "blog_book"."title" AS "col1" FROM "blog_book" UNION SELECT "blog_author"."name" AS "col1" FROM "blog_author"
        output(books.union(authors))

        # 只有 LIMIT、OFFSET、COUNT(*)、ORDER BY 和指定列（即切片、count()、exists()、order_by() 与 values() ／ values_list() ）允许在结果 QuerySet 中使用
        # ORDER BY "col1" ASC
        output(books.union(authors).order_by("title"))
        # 对合并结果进行取值
        output(books.union(authors).values("title"))
        # output(books.union(authors).count("title"))
        # output(books.union(authors).exists())

        # 差集 INTERSECT
        print("----------------------intersection---------------------")
        output(foo.intersection(bar))
        output(foo.intersection(bar, bar2))

        # 并集 EXCEPT
        print("----------------------difference---------------------")
        output(bar.difference(foo))
        output(foo.difference(bar, bar2))

    def test_query_set_select_related(self):
        """
        将“跟随”外键关系，在执行查询时选择额外的相关对象数据。这是一个性能提升器，它导致一个更复杂的单一查询，但意味着以后使用外键关系将不需要数据库查询。
        任何 ForeignKey 或 OneToOneField 关系
        """
        print("----------------select_related--------------------")
        # 跨表查询2次
        book = output_sql(Book.objects.get(id=1))
        # 触发SQL：SELECT "blog_author"."id", "blog_author"."name", "blog_author"."age", "blog_author"."user_id", "blog_author"."studio_id" FROM "blog_author" WHERE "blog_author"."id" = 1
        output_sql(book.author.name)

        print("-------")
        # 联表查询1次
        book = output_sql(Book.objects.select_related("author").get(id=1))
        # 不触发SQL
        output_sql(book.author.name)

        # 联合查询并过滤，顺序不重要
        output_sql(Book.objects.filter(title__contains="Book", id__gt=5).select_related("author"))
        output_sql(Book.objects.select_related("author").filter(title__contains="Book", id__gt=5))

        # 将跨3个表查询，进行数据缓存
        book = output_sql(Book.objects.select_related("author__studio").get(id=1))
        # 不触发新SQL
        print(book.author.name)
        print(book.author.user)

        # 查询多个关联表数据
        output_sql(Book.objects.select_related("author", "author__studio", "author__user"))
        # 和以上效果一致
        all = output_sql(Book.objects.select_related("author").select_related("author__studio").select_related("author__user"))

        # 清除在过去的 select_related 调用中添加的相关字段列表，可以将 None 作为参数传递
        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book"
        output_sql(all.select_related(None))

        output_sql(Book.objects.select_related())

        # ERROR, 仅支持 ForeignKey 或 OneToOneField 关系
        # output_sql(Publisher.objects.select_related("books").get(publisher_name="Packt"))

    def test_query_set_prefetch_related(self):
        """
        在一个批次中自动检索每个指定查询的相关对象
            与 select_related 有类似的目的，二者都是为了阻止因访问相关对象而引起的数据库查询潮，但策略却完全不同
            select_related 的工作方式是创建一个 SQL 连接，并在 SELECT 语句中包含相关对象的字段。
            出于这个原因，select_related 在同一个数据库查询中得到相关对象。
            然而，为了避免因跨越“many”关系进行连接而产生更大的结果集，select_related 仅限于 o2o和 m2o
        prefetch_related 支持多对多、对一和 GenericRelation 对象，外键和一对一关系，
        还支持 GenericForeignKey 的预取，但是必须在 GenericPrefetch 的 querysets 参数中提供每个 ContentType 的查询集
        prefetch_related 使用 IN SQL语句进行关联查询
        """
        print("----------------prefetch_related--------------------")
        # 多对一：触发2条SQL
        # SELECT "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book" LIMIT 21
        # SELECT "blog_author"."id", "blog_author"."name", "blog_author"."age", "blog_author"."user_id", "blog_author"."studio_id" FROM "blog_author" WHERE "blog_author"."id" IN (1)
        output_sql(Book.objects.prefetch_related("author"))

        # 触发3条SQL
        # self.books.all() 将使用数据库查询
        output_sql(Publisher.objects.all())
        # 多对多：触发2条SQL
        # self.books.all() 将使用 prefetch_related 缓存数据
        output_sql(Publisher.objects.prefetch_related("books"))

        # 可以多表关联查询
        output_sql(Publisher.objects.prefetch_related("books__reader_set"))
        output_sql(Publisher.objects.prefetch_related("books__author"))

        # 查询配料，触发3条SQL
        output_sql(Restaurant.objects.prefetch_related("pizzas__toppings"))
        # 查询最佳披萨，触发3条SQL
        output_sql(Restaurant.objects.prefetch_related("best_pizza__toppings"))

        # 触发2条SQL
        # output_sql(Publisher.objects.select_related("外键属性").prefetch_related("外键对象关联的多对多对象"))
        output_sql(Restaurant.objects.select_related("best_pizza").prefetch_related("best_pizza__toppings"))

        # 清空
        qs = Publisher.objects.prefetch_related("books__author")
        qs.prefetch_related(None)

        # 自定义结果集
        output_sql(Restaurant.objects.prefetch_related(Prefetch("pizzas__toppings")))
        # 排序
        output_sql(Restaurant.objects.prefetch_related(Prefetch("pizzas__toppings", queryset=Topping.objects.order_by("name"))))
        # 通过披萨查询餐厅，并查询最好的披萨（通过多对多一端查询另一个多的一段，并查询子集数据）
        output_sql(Pizza.objects.prefetch_related(Prefetch("restaurants", queryset=Restaurant.objects.select_related("best_pizza"))))

        # 将查出的结果集用 直接存储在一个列表
        vegetarian_pizzas = Pizza.objects.filter(name="水果披萨")
        qs = output_sql(Restaurant.objects.prefetch_related(Prefetch("pizzas", to_attr="a"), Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="b")))
        print(qs[0].a)  # [<Pizza: 辣肠披萨 (咸蛋黄, 芝士, 火腿)>, <Pizza: 榴莲披萨 (鸡肉, 榴莲, 菠萝)>, <Pizza: 水果披萨 (咸蛋黄, 鸡肉, 榴莲, 菠萝)>, <Pizza: 暗黑披萨 (咸蛋黄, 菠萝)>]
        print(qs[0].b) # [<Pizza: 水果披萨 (咸蛋黄, 鸡肉, 榴莲, 菠萝)>]

        # 对查询结果集进行二次查询
        qs = output_sql(Restaurant.objects.prefetch_related(Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="b"), "b__toppings"))
        print(qs[0].b)  # [<Pizza: 水果披萨 (咸蛋黄, 鸡肉, 榴莲, 菠萝)>]
        print(qs[0])    # 高级披萨餐厅

        # 预取
        only_name = Pizza.objects.only("name")
        restaurants = Restaurant.objects.prefetch_related(Prefetch("best_pizza", queryset=only_name))
        print(restaurants) # <QuerySet [<Restaurant: 高级披萨餐厅>, <Restaurant: 水果萨餐厅>, <Restaurant: 素食披萨餐厅>, <Restaurant: 暗黑萨餐厅>]>

        output_sql(Restaurant.objects.prefetch_related("pizzas__toppings", "pizzas"))

        # 数据库
        # output_sql(Restaurant.objects.prefetch_related("pizzas__toppings").using("replica"))
        #
        # # Inner将使用“副本”数据库；外部将使用“默认”数据库
        # Restaurant.objects.prefetch_related(
        #     Prefetch("pizzas__toppings", queryset=Topping.objects.using("replica")),
        # )
        # # 内部将使用“副本”数据库；外层将使用“冷藏”数据库
        # Restaurant.objects.prefetch_related(
        #     Prefetch("pizzas__toppings", queryset=Topping.objects.using("replica")),
        # ).using("cold-storage")

    def test_query_set_extra(self):
        """
        用于将特定的子句注入到由 QuerySet 生成的 SQL 中
        """
        print("----------------extra--------------------")
        output_sql(Book.objects.extra(select={"price_cents": "price * 100"}, order_by=["price_cents"]))
        # SELECT (select 4) AS "val", "blog_book"."id", "blog_book"."title", "blog_book"."price", "blog_book"."author_id" FROM "blog_book"
        output_sql(Book.objects.extra(select={"val": "select 4"}))
        # SELECT (created_date > '2006-01-01') AS "is_recent", "blog_post"."id", ...
        output_sql(Post.objects.extra(select={"is_recent": "created_date > '2006-01-01'"}))
        # 列子句查询
        # SELECT (SELECT COUNT(*) FROM blog_tags WHERE blog_tags.post_id = blog_post.id) AS "tag_count",
        output_sql(Post.objects.extra(select={"tag_count": "SELECT COUNT(*) FROM blog_tags WHERE blog_tags.post_id = blog_post.id"}))

        # 设置参数
        # SELECT ('one') AS "a", ('two') AS "b",
        output_sql(Post.objects.extra(select={"a": "%s", "b": "%s"}, select_params=("one", "two")))

        # WHERE (title='a' OR title='b') AND (status = False)
        output_sql(Post.objects.extra(where=["title='a' OR title='b'", "status = False"]))

        # 设置表名
        output_sql(Post.objects.extra(where=["title='a' OR title='b'", "status = False"], tables=["blog_post"]))

        # 排序
        qs = output_sql(Book.objects.extra(select={"price_cents": "price * 100"}))
        # FROM "blog_book" ORDER BY 1 DESC
        output_sql(qs.extra(order_by=["-price_cents"]))

        # where 条件传参
        # WHERE (title='a')
        output_sql(Book.objects.extra(where=["title=%s"], params=["a"]))

    def test_query_set_defer(self):
        """
        不要从数据库中检索字段
        """
        print("----------------defer--------------------")
        output_sql(Post.objects.defer("content", "published_date", "image"))
        output_sql(Post.objects.defer("content", "published_date", "image").filter(id=1))
        # 支持链式
        output_sql(Post.objects.defer("content", "published_date", "image").filter(id=1).defer("author", "created_date"))
        # 支持跨表
        output_sql(Post.objects.defer("content", "published_date", "image").filter(id=1).defer("author__email", "author__last_name"))

        # 清除
        output_sql(Post.objects.defer("content", "published_date", "image").filter(id=1).defer("author__email", "author__last_name").defer(None))

    def test_query_set_only(self):
        """
        only() 方法实际上是 defer() 的相反，只查询相应的字段
        """
        print("----------------only--------------------")
        # SELECT "blog_post"."id", "blog_post"."content", "blog_post"."published_date", "blog_post"."image" FROM "blog_post"
        output_sql(Post.objects.only("content", "published_date", "image"))
        output_sql(Post.objects.only("content", "published_date", "image").filter(id=1))
        # 支持链式
        output_sql(Post.objects.only("content", "published_date", "image").filter(id=1).only("author", "created_date"))
        # 支持跨表
        output_sql(Post.objects.only("content", "published_date", "image").filter(id=1).only("author__email", "author__last_name"))

    def test_query_set_using(self):
        """
        使用指定的数据库
        """
        print("----------------using--------------------")
        # default
        output_sql(Book.objects.db)

        # 设置数据库
        # output_sql(Book.objects.using("replica"))
        # output_sql(Book.objects.using("replica").filter("title='book'"))

    @sql_decorator
    def test_query_set_select_for_update(self):
        """
        SELECT FOR UPDATE
        select_for_update(nowait=False, skip_locked=False, of=(), no_key=False)
        返回一个查询集，该查询集将锁定行直到事务结束，生成 SELECT ... FOR UPDATE SQL 语句
        默认情况下，select_for_update() 锁定所有被查询选择的行
        nowait=True 不等待/不阻塞
        skip_locked=True 来忽略锁定的记录
        nowait 和 skip_locked 是相互排斥的，在启用这两个选项的情况下调用 select_for_update() 会导致一个 ValueError
        of=(...) 中使用与 select_related() 相同的字段语法指定你要锁定的相关对象。使用 'self' 来表示查询集的模型
        no_key=True 来获得一个较弱的锁（外键有插入实际值而不是None）

        为了正确测试 select_for_update() 应该使用 TransactionTestCase
        """
        print("----------------select_for_update--------------------")
        books = Book.objects.select_for_update().filter(id__lt=3)
        with transaction.atomic():
            # for book in books，所有匹配的条目将被锁定，直到事务块结束
            # 如果另一个事务已经获得了所选行的锁，那么查询将被阻塞，直到锁被释放
            # 不想阻塞 select_for_update(nowait=True)
            # select_for_update(skip_locked=True) 来忽略锁定的记录
            for book in books:
                print(book)

        # 锁定自引用模型和父模型：在使用 多表继承 时要锁定父模型，必须在 of 参数中指定父链接字段
        Restaurant.objects.select_for_update(of=("self", "place_ptr"))

        # 锁定指定列
        qs = Restaurant.objects.values("name").select_for_update(of=("name"))
        with transaction.atomic():
            for restaurant in qs:
                print(restaurant)

        Restaurant.objects.select_related("best_pizza").select_for_update().exclude(best_pizza=None)

    def test_query_range(self):
        print("----------------test_query_range--------------------")
        # LIMIT 3
        output_sql(Tags.objects.all()[:3])
        print(type(Tags.objects.all()[:3])) # <class 'django.db.models.query.QuerySet'>
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

    def test_query_set_cache(self):
        # https://docs.djangoproject.com/zh-hans/5.1/topics/db/queries/#caching-and-querysets
        output_sql(Tags.objects.all())

        # 使用缓存
        # <generator object QuerySetTest.test_query_set_cache.<locals>.<genexpr> at 0x0000024435E15E40>
        print(item.tag_name for item in Tags.objects.all())
        print(item.post_id for item in Tags.objects.all())

        qs = Tags.objects.all()
        print(item.tag_name for item in qs)
        print(item.post_id for item in qs)

        print(qs[2])
        print(qs[2])

        # 不使用缓存操作
        # [entry for entry in queryset]
        # bool(queryset)
        # entry in queryset
        # list(queryset)

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
