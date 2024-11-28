from apps.blog.models import Person, Student, Teacher, WebProject, MobileProject, Project, JavaWebProject
from apps.blog.tests.tests import BasedTestCase, sql_decorator


class ExtendModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()

    @sql_decorator
    def test_student_model(self):
        # INSERT INTO "blog_person" ("name", "age") VALUES ('张三', 18) RETURNING "blog_person"."id"
        person = Person.objects.create(age=18, name="张三")
        print(person)
        # print(person.student) # RelatedObjectDoesNotExist: Person has no student.

        # person_ptr_id 依赖父表的id
        # 触发2条SQL，1条SQL插入Person，1条SQL插入Student，并建立依赖关系
        # INSERT INTO "blog_person" ("name", "age") VALUES ('李四', 18) RETURNING "blog_person"."id"
        # INSERT INTO "blog_student" ("student_id", "person_ptr_id") VALUES ('2018010101', 2)
        student = Student.objects.create(age=18, name="李四", student_id="2018010101")
        print(student)
        print(student.age)
        print(student.id)

        # 父表数据
        print(student.person_ptr)
        print(student.person_ptr.age)

        # 通过主键查询
        parent = Person.objects.get(id=student.person_ptr_id)
        print(parent)

        # 查询子表数据
        # SELECT "blog_person"."id", "blog_person"."name", "blog_person"."age", "blog_student"."student_id", "blog_student"."person_ptr_id" FROM "blog_student" INNER JOIN "blog_person" ON ("blog_student"."person_ptr_id" = "blog_person"."id") WHERE "blog_student"."person_ptr_id" = 2 LIMIT 21
        print(parent.student)

    @sql_decorator
    def test_teacher_model(self):
        teacher = Teacher.objects.create(age=18, name="李四", salary=10000)
        print(teacher)
        print(teacher.id)
        print(teacher.age)

        # 父表数据
        print(teacher.person_ptr)
        print(teacher.person_ptr.age)

        # 通过主键查询
        parent = Person.objects.get(id=teacher.id)
        print(parent)

        # 查询子表数据
        # SELECT "blog_person"."id", "blog_person"."name", "blog_person"."age", "blog_teacher"."person_ptr_id", "blog_teacher"."salary" FROM "blog_teacher" INNER JOIN "blog_person" ON ("blog_teacher"."person_ptr_id" = "blog_person"."id") WHERE "blog_teacher"."person_ptr_id" = 1 LIMIT 21
        # print(parent.teacher)

        if hasattr(parent, 'teacher'):
            tear = parent.teacher
            print(tear.salary)  # 输出: 10000
        else:
            print("这不是一个学生")

        # 单表查询
        print(Person.objects.filter(name="李四"))
        # 多表连接查询
        print(Teacher.objects.filter(name="李四"))

    @sql_decorator
    def test_m2m_project(self):
        alice = Person.objects.create(name='Alice-admin', age=44)
        bob = Person.objects.create(name='Bob-developer', age=33)
        charlie = Person.objects.create(name='Charlie-admin', age=22)

        # 创建 父表和子表
        # INSERT INTO "blog_project" ("name", "description") VALUES ('AI Research', 'Web AI algorithms.') RETURNING "blog_project"."id"
        # INSERT INTO "blog_webproject" ("project_ptr_id", "url") VALUES (1, 'http://www.example.com/ai-research')
        web_proj = WebProject.objects.create(name='AI Research', description='Web AI algorithms.', url='http://www.example.com/ai-research')
        # 关联的用户 管理员
        # INSERT OR IGNORE INTO "blog_webproject_administrators" ("webproject_id", "person_id") VALUES (1, 1), (1, 3)
        web_proj.administrators.add(alice, charlie)

        # INSERT INTO "blog_project" ("name", "description") VALUES ('Wechat App', 'Developing a Wechat Mobile application.') RETURNING "blog_project"."id"
        # INSERT INTO "blog_mobileproject" ("project_ptr_id", "device") VALUES (2, 'iPhone')
        mobile_proj = MobileProject.objects.create(name='Wechat App', description='Developing a Wechat Mobile application.', device='iPhone')
        # 关联用户 开发者
        # INSERT OR IGNORE INTO "blog_mobileproject_developers" ("mobileproject_id", "person_id") VALUES (2, 2)
        mobile_proj.developers.add(bob)

        # 查询bob的 mobile 项目
        print(bob.mobile_projects.all())
        # 查询alice的 web 项目
        print(alice.web_projects.all())

        # 利用继承关系，隐式获取子类
        print(Project.objects.get(name='AI Research').webproject)
        print(Project.objects.get(name='Wechat App').mobileproject)

        # 利用继承关系，隐式默认 parent_link=True 获取子类
        # 子类 project 继承 父类 project，就可以关联到 父类的 project_ptr
        print(web_proj.project_ptr)
        if hasattr(mobile_proj, 'project_ptr'):
            print(mobile_proj.project_ptr)

    @sql_decorator
    def test_many_cascade(self):
        alice = Person.objects.create(name='Alice-admin', age=44)
        bob = Person.objects.create(name='Bob-developer', age=33)
        charlie = Person.objects.create(name='Charlie-admin', age=22)

        web_proj = WebProject.objects.create(name='AI Research', description='Web AI algorithms.', url='http://www.example.com/ai-research')
        web_proj.administrators.add(alice, charlie)

        mobile_proj = MobileProject.objects.create(name='Wechat App', description='Developing a Wechat Mobile application.', device='iPhone')
        mobile_proj.developers.add(bob)

        java_proj = JavaWebProject.objects.create(name='Java Web', description='Developing a Java Web application.', url='http://www.example.com/java-web', framework='Spring')
        java_proj.administrators.add(alice)

        print(alice.web_projects)
        print(alice.web_projects.all())

        print(java_proj.administrators)
        # 访问 project_ptr
        print(java_proj.project_ptr)
        # 访问 webproject_ptr
        print(java_proj.webproject_ptr)

        print(Project.objects.get(name='Java Web').webproject)
        print(Project.objects.get(name='Java Web').webproject.javawebproject)
        print(alice.web_projects.get(name='Java Web').javawebproject)
