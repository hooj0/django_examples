from apps.blog.models import Employee, faker
from apps.blog.tests.tests import BasedTestCase, output_sql


class EmployeeModelTest(BasedTestCase):

    def test_create(self):
        # 创建员工
        e1 = Employee.objects.create(name='ai')
        e2 = Employee.objects.create(name=faker.name())
        e3 = Employee.objects.create(name=faker.name())

        # 加入团队
        e1.teams.add(e2, e3)
        output_sql(e1.teams.all())

        # 要获取底层数据库表中的实际 ID，你需要查询中间表
        # 你可以通过 <model>_set 来反向查询或者使用 related_name 参数来指定名称
        for team_employee in Employee.teams.through.objects.filter(from_employee=e1):
            print(f"Employee teams with {team_employee.to_employee} - {team_employee.id}")

        print("------------")
        for team_employee in Employee.teams.through.objects.all():
            print(team_employee.id)
            print(f"团队成员 {team_employee.to_employee}")
            print(f"已加入团队 {team_employee.from_employee}")

        # 注意: 默认情况下, 中间表的名字是 'appname_employee_teams'
        # (这里 'appname' 是你的应用名, 'employee' 是模型的小写名字, 'teams' 是 ManyToManyField 的名字),
        # 并且包含两个字段: 'from_employee_id' 和 'to_employee_id'.