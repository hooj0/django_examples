import copy
import enum
import inspect
from enum import IntEnum
from operator import attrgetter, itemgetter
from typing import List

from django.db import models
from django.db.models.enums import Choices

from common.util import utils


class BeanUtils:
    """
    BeanUtils 仿照Java中的BeanUtils，可进行Bean Object对象（或属性值）复制
    """
    pass

    @staticmethod
    def kget(target: list, key: str) -> list:
        """
        get the value of the key in the target object list
        :param target: target object list
        :param key: the key of the target object
        :return: the value of the key in the target object
        """
        return list(map(attrgetter(key), target))

    @staticmethod
    def iget(target: list[tuple], index: int) -> list:
        """
        get the value of the key in the target object list
        :param target: target object list
        :param index: the key of the target object
        :return: the value of the key in the target object
        """
        return list(map(itemgetter(index), target))

    @staticmethod
    def copy_properties(source: dict | object | List[object] | List[dict], target: object | type, mapping: dict = None, skip_null: bool = False) -> object | List[object]:
        """
        copy properties from source to target
        :param source: source is custom bean object or dict type
        :param target: target object is custom bean object
        :param mapping: mapping of source object properties to target object properties
        :param skip_null: skip null value
        :return: target object
        """
        if not (isinstance(source, object) or isinstance(source, dict)):
            raise TypeError("source must be an instance of custom object or dict")

        if isinstance(target, type):
            target = BeanUtils.__create_instance(target)
        elif not BeanUtils.__is_custom_object(target):
            raise TypeError("target must be an instance of custom object")
        if source is None or target is None:
            raise ValueError("source or target must be not null value")
        if mapping is None:
            mapping = {}

        if not hasattr(target, '__dict__'):
            raise ValueError("target must be valid objects with __dict__ attribute")
        if isinstance(source, dict):
            source_dict = source
        elif not hasattr(source, '__dict__'):
            raise ValueError("source must be valid objects with __dict__ attribute")
        else:
            source_dict = source.__dict__

        for key in source_dict:
            target_key = mapping.get(key, key)

            # 检查 target 是否有 target_key 属性
            if hasattr(target, target_key):
                try:
                    if isinstance(source, dict):
                        value = source[key]
                    else:
                        value = getattr(source, key)

                    if skip_null and value is None:
                        continue
                    if BeanUtils.__is_custom_object(value) and not BeanUtils.__is_enum(value):
                        continue
                    setattr(target, target_key, value)
                except AttributeError as e:
                    # 处理 getattr 或 setattr 抛出的异常
                    print(f"Error: copying property {key} to {target_key}: {e}")
            else:
                # 如果 target 没有 target_key 属性，记录警告
                print(f"Warning: target object does not have property {target_key}")

        return target

    @staticmethod
    def copy(source: dict | object | List[object] | List[dict], target: object | type) -> object | List[object]:
        """
        copy properties from source to target
        :param source: source object
        :param target: destination object class type
        :return: target object
        """
        if isinstance(source, list):
            return list(map(lambda src: BeanUtils.copy_properties(src, target), source))
        elif isinstance(target, type) and type(source) is target:
            print("source and target are same type")
            return copy.copy(source)
        else:
            return BeanUtils.copy_properties(source, target)

    @staticmethod
    def __create_instance(target):
        if isinstance(target, type):
            try:
                return target()
            except TypeError as e:
                raise TypeError(f"Failed to create {target} instance, __init__(self) function needs to be provided: {e}")
        elif not isinstance(target, object) or not BeanUtils.__is_custom_object(target):
            raise TypeError("target must be an instance of custom object")
        return target

    @staticmethod
    def __is_custom_object(target):
        return target.__class__.__module__ != 'builtins'


    @staticmethod
    def __is_enum(target):
        # 如果传入的是类型本身
        if isinstance(target, type):
            return issubclass(target, enum.Enum)
        else:
            # 如果传入的是对象
            return isinstance(target, enum.Enum)

    @staticmethod
    def test(value):
        print(BeanUtils.__is_enum(value), type(value))


if __name__ == '__main__':
    class Item:
        def __init__(self, name, value):
            self.name = name
            self.value = value
            self.a = 1

    class Record:
        def __init__(self, name, value):
            self.name2 = name
            self.value = value
            self.b = 2

    class Record2:
        def __init__(self):
            self.name = None
            self.value = None
            self.c = 3

    class User:
        def __init__(self, name, age, item, choice):
            self.name = name
            self.age = age
            self.item = item
            self.choice = choice

    item = Item('apple', 1)
    items = [item, Item('banana', 2)]

    # 获取对象的属性值列表
    print("--------------获取对象的属性值列表--------------")
    print(BeanUtils.kget(items, 'name'))
    print(BeanUtils.kget(items, 'value'))
    print(BeanUtils.iget([("aa", 1), ("bb", 2)], 1))

    # 复制对象属性
    print("--------------复制对象属性--------------")
    print(item.__dict__)
    item2 = Item(None, None)
    print(BeanUtils.copy_properties(item, item2).__dict__)
    print(item2.__dict__)
    print(BeanUtils.copy_properties(item, item2).__dict__)

    # 复制dict对象
    print("--------------复制dict对象--------------")
    print(BeanUtils.copy_properties({'name': 'apple', 'value': 1, 'a': 1, 'd': 4}, item2).__dict__)

    # 复制对象，设置mapping映射关系
    print("--------------复制对象，设置mapping映射关系--------------")
    item2 = Item(None, 2)
    record = Record('apple', None)
    print(BeanUtils.copy_properties(record, item2, {'name2': 'name'}).__dict__)

    item2 = Item(None, 2)
    record = Record('apple', None)
    print(BeanUtils.copy_properties(item2, record, {'name': 'name2'}).__dict__)

    # 复制对象，创建目标类型对象
    print("--------------复制对象，创建目标类型对象--------------")
    print(BeanUtils.copy(item, Record2).__dict__)
    print(BeanUtils.copy({'name': 'apple2', 'value': 11, 'a': 1, 'd': 4}, Record2).__dict__)

    # 复制对象列表
    print("--------------复制对象列表--------------")
    print(list(map(vars, BeanUtils.copy(items, Record2))))
    print([vars(x) for x in BeanUtils.copy([{'name': 'apple2', 'value': 11}, {'name': 'xiaomi', 'value': 2}], Record2)])

    # 同类型对象复制
    print("--------------同类型对象复制--------------")
    print(vars(BeanUtils.copy(item, item2)))

    record2 = Record2()
    record2.name = 'xiaomi'
    record2.value = 2
    print(vars(BeanUtils.copy(record2, Record2)))

    # 复杂对象复制
    print("--------------复杂对象复制--------------")
    user = User('xiaomi', 18, item, enum.Enum('choice', {'a': 3, 'b': 4}))
    # print(vars(user))
    # print(BeanUtils.copy(user, User).__dict__)

    choice = enum.Enum('choice', {'a': 3333, 'b': 4444})
    # 获取对象的类型
    obj_type = type(item)

    user2 = User(None, None, None, None)
    print(BeanUtils.copy(user, user2).__dict__)
    user2.choice = enum.Enum('choice', {'a': 3333, 'b': 4444})
    print(user.choice)
    print(vars(user.item))
    print(user2.choice)

    # 测试枚举类型
    print("--------------测试枚举类型--------------")
    class Color(enum.Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class Number(IntEnum):
        ONE = 1
        TWO = 2
        THREE = 3

    Place = models.IntegerChoices("Place", "FIRST SECOND THIRD")

    BeanUtils.test(item)
    BeanUtils.test({'name': 'apple', 'value': 1})
    BeanUtils.test(choice)
    BeanUtils.test(choice.a)
    BeanUtils.test(Color.RED)      # True, 因为 Color.RED 是枚举类型的实例
    BeanUtils.test(Color)         # True, 因为 Color 是枚举类
    BeanUtils.test(Number.ONE)     # True, 因为 Number.ONE 是枚举类型的实例
    BeanUtils.test(Number)
    BeanUtils.test(Place)
    BeanUtils.test(Place.THIRD)
