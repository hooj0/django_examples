from django.utils import timezone
from faker import Faker
from django.contrib.auth.models import User

from apps.blog.models import Comment, Post
from apps.blog.tests.tests import BasedTestCase, output_sql, sql_decorator


class TestComment(BasedTestCase):
    """
    模型字段和字段属性参考
    https://docs.djangoproject.com/zh-hans/5.1/ref/models/fields/
    """
    def setUp(self):
        super().setUp()
        # 创建User
        self.user = User.objects.create(username='test')
        # 创建Post
        self.post = Post.objects.create(title='this is post.', content='this is content.', author=self.user)
        # 查询所有Post
        print("posts: ", Post.objects.all())

    @sql_decorator
    def test_create(self):
        create = Comment.objects.create(content="test", post=self.post, email="test@qq.com")
        print(create)

        faker = Faker()
        create.user = faker.user_name()
        create.file = faker.file_path()
        create.file_path = faker.file_path()
        create.file_size = faker.pyint()
        create.photo = faker.image_url()
        create.created_date = faker.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
        create.updated_date = faker.date()
        create.interval = faker.time_delta(timezone.now())
        create.pub_time = faker.time()
        create.size = faker.pyint()
        create.stars = faker.pyfloat(max_value=10, min_value=0.1)
        create.status = faker.pybool()
        create.uri = faker.uri()
        create.url_param = faker.slug()
        create.content = faker.text()
        create.uuid = faker.uuid4()
        create.first_name = faker.first_name()
        create.last_name = faker.last_name()
        create.json = faker.json()
        create.ip_address = faker.ipv4()
        create.rate = faker.pyfloat(min_value=0, max_value=9, right_digits=1)

        print(create.save())
        print(Comment.objects.all())
