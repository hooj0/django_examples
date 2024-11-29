from django.conf import settings
from django.db import connection
from django.db import reset_queries
from django.db.models import QuerySet
from django.test import TestCase


def sql_decorator(func):
    def wrapper(*args, **kwargs):
        reset_queries()

        result = func(*args, **kwargs)

        for query in connection.queries:
            # print(query['time'] + " -> " + query['sql'])
            print(query['sql'])

        print("")
        reset_queries()
        return result
    return wrapper


class SqlContextManager:
    def __enter__(self):
        reset_queries()

    def __exit__(self, exc_type, exc_value, traceback):
        for query in connection.queries:
            # print(query['time'] + " -> " + query['sql'])
            print(query['sql'])

        print("")
        reset_queries()

def output_sql(self, *args):
    print(self, *args)

    for query in connection.queries:
        # print(query['time'] + " -> " + query['sql'])
        print(query['sql'])

    if connection.queries:
        print("")
    reset_queries()
    return self

def output(query_set: QuerySet):
    print(query_set)
    print(query_set.query)
    print("")
    return query_set


class BasedTestCase(TestCase):

    def setUp(self):
        super().setUp()

        # 清空
        reset_queries()
        # 显示开启debug模式
        settings.DEBUG = True