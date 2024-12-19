from datetime import date

from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries


from apps.blog.models import Tags, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, SqlContextManager, sql_decorator, output


class TagsModelTest(BasedTestCase):
    """
    https://docs.djangoproject.com/zh-hans/5.1/topics/db/models/
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/instances/
    """
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

        # 强制保存或更新
        tags_foo = Tags(tag_name='tag test foo', post=self.post)
        tags_foo.save(force_insert=True)
        tags_foo.save(force_update=True)

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

        # 所有数据 更新部分字段
        # UPDATE "blog_tags" SET "tag_name" = 'barxxxxxxxx'
        row = Tags.objects.update(tag_name='barxxxxxxxx')
        print("tags_bar: ", row)
        tags_bar = Tags.objects.get(id=1)
        print("tags_bar: ", tags_bar)

        # 部分数据更新部分字段
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

    @sql_decorator
    def test_get_or_create(self):
        """
        获取或者创建对象
        get_or_create(defaults=None, **kwargs)
        """
        data, created = Tags.objects.get_or_create(tag_name='test2', post=self.post)
        print(data, created)  # id: 13, tag_name: test2, post_id: 1    True

    @sql_decorator
    def test_update_or_create(self):
        """
        update_or_create(defaults=None, create_defaults=None, **kwargs)
        更新或者创建对象，
            defaults 用于更新对象，而 create_defaults 用于创建操作。
            如果未提供 create_defaults，则将使用 defaults 进行创建操作。
        """
        # id: 12, title: test, content: content is****, created_date: 2024-12-18 08:12:38.768229+00:00, published_date: 2024-12-18 08:12:38.768240+00:00, image: , author_id: 1, status: False =====>>>>>> True
        data, created = Post.objects.update_or_create(
            title="test",
            content="content is a b",
            author=self.user,
            defaults={"status": True},
            create_defaults={"status": False, "published_date": date(1940, 10, 9)},
        )
        print(data, created)

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
        Tags.objects.bulk_create(data, batch_size=2)

    @sql_decorator
    def test_bulk_update(self):
        """
        bulk_update(objs, fields, batch_size=None)
        这个方法高效地更新提供的模型实例上的给定字段，通常只需一个查询，并返回更新的对象数量
        """
        data = [
            Tags(tag_name='tag test 1', post=self.post, id=1),
            Tags(tag_name='tag test 2', post=self.post, id=2),
            Tags(tag_name='tag test 3', post=self.post, id=222),
            Tags(tag_name='tag test 4', post=self.post, id=3),
            Tags(tag_name='tag test 5', post=self.post, id=111),
        ]
        # 批量更新必须有主键
        Tags.objects.bulk_update(data, ['tag_name'], batch_size=2)