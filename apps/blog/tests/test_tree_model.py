from unittest import TestCase

from apps.blog.models import Tree
from apps.blog.tests.tests import BasedTestCase, sql_decorator


class TreeModelTest(BasedTestCase):

    def setUp(self):
        super().setUp()

    @sql_decorator
    def test_add_node(self):
        root = Tree.objects.create(node='root')
        node1 = Tree.objects.create(node='java', parent=root)
        node2 = Tree.objects.create(node='python', parent=root)

        node1_1 = Tree.objects.create(node='spring', parent=node1)
        node1_2 = Tree.objects.create(node='struts', parent=node1)

        node2_1 = Tree.objects.create(node='django', parent=node2)
        node2_2 = Tree.objects.create(node='flask', parent=node2)

        node = Tree.objects.filter(node='java').first()
        print(node.children.all())
        print(node.parent)
