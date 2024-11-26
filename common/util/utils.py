def object_to_string(obj, max_length=15):
    """
    将对象转换为字符串
    :param obj: 要转换的对象
    :param max_length: 属性值的最大长度，默认为15
    :return: 字符串表示
    """
    attributes = vars(obj)  # 获取对象的所有属性
    result = []

    for key, value in attributes.items():
        # 对敏感信息进行脱敏处理
        if isinstance(value, str):
            masked_value = value[:10] + '*' * (min(len(value), max_length) - 10)
        elif isinstance(value, (int, float)):
            masked_value = str(value)
        elif isinstance(value, object):
            masked_value = "未知"
        else:
            masked_value = value

        # 添加属性到结果列表
        result.append(f"{key}: {masked_value}")

    # 使用逗号和空格连接所有属性
    return ', '.join(result)