from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries


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