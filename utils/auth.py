# 模拟用户数据库，实际应用中可替换为从数据库中读取
users = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "d_id": 1
    },
    "employee": {
        "password": "employee123",
        "role": "employee",
        "d_id": 1
    },
    "guest": {
        "password": "guest123",
        "role": "guest",
        "d_id": None
    }
}

def login(username, password):
    """
    用户登录验证函数
    :param username: 输入的用户名
    :param password: 输入的密码
    :return: 如果验证通过，返回用户信息字典；否则返回 None
    """
    if username in users and users[username]["password"] == password:
        return {
            "username": username,
            "role": users[username]["role"],
            "d_id": users[username]["d_id"]
        }
    return None


def login_as_guest():
    """
    以访客身份登录
    :return: 访客用户信息字典
    """
    return {
        "username": "guest",
        "role": "guest",
        "d_id": None
    }


def is_super_admin(user):
    """
    判断用户是否为超级管理员
    :param user: 用户信息字典
    :return: 如果是超级管理员返回 True，否则返回 False
    """
    return user["role"] == "admin"


def is_department_admin(user):
    """
    判断用户是否为部门管理员
    :param user: 用户信息字典
    :return: 如果是部门管理员返回 True，否则返回 False
    """
    return user["role"] == "admin"


def has_permission(user, required_role):
    """
    检查用户是否具有指定角色的权限
    :param user: 用户信息字典
    :param required_role: 所需角色
    :return: 如果用户具有该角色权限返回 True，否则返回 False
    """
    return user["role"] == required_role