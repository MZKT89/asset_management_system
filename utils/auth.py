from utils.data_utils import *
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


def login(e_id, password):
    """
    用户登录验证函数
    :param e_id: 输入的员工 ID（作为用户名）
    :param password: 输入的密码
    :return: 如果验证通过，返回用户信息字典；否则返回 None
    """
    result = query_user_by_credentials(e_id, password)
    if result is None:
        return None  # 如果 result 为 None，直接返回 None
    departmentResult = query_department_Name(result[2])
    if result:
        user_info = {
            "e_id": result[0],
            "role": "super-admin" if result[1] == 2 else ("dep-admin" if result[1] == 1 else "non-admin"),
            "d_id": result[2],
            "Name": result[3],
            "DepartmentName": departmentResult 
        }
        return user_info    
    else:
        return None


def login_as_guest():
    """
    以访客身份登录
    :return: 访客用户信息字典
    """
    return {
        "e_id": None,
        "role": "guest",
        "d_id": None
    }
