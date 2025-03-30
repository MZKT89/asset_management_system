import sqlite3
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)

def create_connection():
    """
    创建数据库连接
    :return: 数据库连接对象
    """
    try:
        conn = sqlite3.connect('asset_management.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return None


def create_tables():
    """
    创建数据库表
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        # 创建 DEPARTMENT 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DEPARTMENT (
                d_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Department_Name VARCHAR(100) NOT NULL,
                a_ID VARCHAR(50) UNIQUE,
                FOREIGN KEY (a_ID) REFERENCES ADMINISTRATOR(a_ID)
            )
        ''')
        # 创建 ITEM 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ITEM (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Item_Name VARCHAR(100) NOT NULL,
                d_ID VARCHAR(50) NOT NULL,
                Placement_Location VARCHAR(100),
                Status INT CHECK (Status IN (0, 1)),
                Current_Value DECIMAL(10,2),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        ''')
        # 创建 EMPLOYEE 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EMPLOYEE (
                e_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name VARCHAR(100) NOT NULL,
                d_ID VARCHAR(50) NOT NULL,
                password VARCHAR(255),
                Position INT CHECK (Position IN (0, 1, 2)),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        ''')
        # 创建 PURCHASE_INFO 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS PURCHASE_INFO (
                ID INTEGER,
                Asset_Cost DECIMAL(10,2) NOT NULL,
                Purchase_Year INT,
                d_ID VARCHAR(50) NOT NULL,
                Usable_Life INT,
                FOREIGN KEY (ID) REFERENCES ITEM(ID),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        ''')
        # # 创建 ADMINISTRATOR 表
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS ADMINISTRATOR (
        #         a_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        #         Name VARCHAR(100) NOT NULL,
        #         e_ID VARCHAR(50) UNIQUE NOT NULL,
        #         Contact_Info VARCHAR(255),
        #         FOREIGN KEY (e_ID) REFERENCES EMPLOYEE(e_ID)
        #     )
        # ''')

                # 创建 ADMINISTRATOR 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ADMINISTRATOR (
                e_ID VARCHAR(50),
                d_ID VARCHAR(50),
                Name VARCHAR(100) NOT NULL,
                Contact_Info VARCHAR(255),
                PRIMARY KEY (e_ID, d_ID),  -- 将 e_ID 和 d_ID 组合设置为主键
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID),
                FOREIGN KEY (e_ID) REFERENCES EMPLOYEE(e_ID)  
            )
        ''')
        conn.commit()
        conn.close()


# 你可以按照上述示例为其他表添加插入、查询、更新和删除函数    


'''
登陆页以及权限设置页部分的处理代码逻辑
'''
'''
负责用户登录验证和权限管理的函数
'''
def query_user_by_credentials(username, password):
    """
    根据用户名和密码查询用户信息
    :param username: 用户名
    :param password: 密码
    :return: 如果查询到用户信息，返回包含用户信息的元组；否则返回 None
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e_ID, Position, d_ID, password
                FROM EMPLOYEE
                WHERE e_ID =?
            ''', (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result[3]
                if verify_password(password, stored_password):
                    return result[:3]  # 返回除密码外的用户信息
            return None
        except sqlite3.Error as e:
            print(f"数据库查询错误: {e}")
        finally:
            conn.close()
    return None


def get_all_users():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT e_ID, Name, d_ID, Position FROM EMPLOYEE')
            users = cursor.fetchall()
            return users
        except sqlite3.Error as e:
            print(f"查询用户信息出错: {e}")
        finally:
            conn.close()
    return []

def update_user_role(user_id, new_role, contact=None):
    """
    更新用户角色
    :param user_id: 用户 ID
    :param new_role: 新角色编号
    :param contact: 联系方式
    :return: 更新是否成功
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 更新 EMPLOYEE 表中的角色
            cursor.execute('UPDATE EMPLOYEE SET Position =? WHERE e_ID =?', (new_role, user_id))

            # 获取员工姓名
            cursor.execute('SELECT Name,d_ID FROM EMPLOYEE WHERE e_ID =?', (user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            name = result[0]
            d_id = result[1]

            if new_role == 1:
                # 如果新角色是部门管理员，插入或更新 ADMINISTRATOR 表
                print(f"即将插入的 contact 值: {contact}")
                cursor.execute('INSERT OR REPLACE INTO ADMINISTRATOR (Name, e_ID, d_ID, Contact_Info) VALUES (?,?,?,?)',
                               (name, user_id, d_id, contact))
            else:
                # 如果新角色不是部门管理员，从 ADMINISTRATOR 表中删除该记录
                cursor.execute('DELETE FROM ADMINISTRATOR WHERE e_ID =?', (user_id,))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新用户角色出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False
def add_new_user(name, password, department_id, position, contact=None):
    """
    新增用户
    :param name: 员工姓名
    :param password: 密码
    :param department_id: 部门 ID
    :param position: 角色编号
    :param contact: 联系方式
    :return: 新增是否成功
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 插入员工信息到 EMPLOYEE 表
            cursor.execute('INSERT INTO EMPLOYEE (Name, password, d_ID, Position) VALUES (?,?,?,?)',
                           (name, hash_password(password), department_id, position))
            employee_id = cursor.lastrowid

            if position == 1:
                # 如果新用户是部门管理员，插入到 ADMINISTRATOR 表
                cursor.execute('INSERT INTO ADMINISTRATOR (Name, e_ID, d_ID, Contact_Info) VALUES (?,?,?,?)',
                               (name, employee_id, department_id, contact))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"新增用户出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False
def test_login_add_data():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            # 插入两个部门
            departments = ["研发部", "市场部"]
            department_ids = []
            for dept_name in departments:
                cursor.execute("INSERT INTO DEPARTMENT (Department_Name) VALUES (?)", (dept_name,))
                department_ids.append(cursor.lastrowid)

            # 插入员工数据
            employees = [
                {"name": "张三", "dept_id": department_ids[0], "password": hash_password("password1"), "position": 1},
                {"name": "李四", "dept_id": department_ids[1], "password": hash_password("password2"), "position": 1},
                {"name": "王五", "dept_id": department_ids[0], "password": hash_password("password3"), "position": 2},
                {"name": "赵六", "dept_id": department_ids[0], "password": hash_password("password4"), "position": 0},
                {"name": "孙七", "dept_id": department_ids[1], "password": hash_password("password5"), "position": 0}
            ]
            employee_ids = []
            
            for emp in employees:
                cursor.execute("INSERT INTO EMPLOYEE (Name, d_ID, password, Position) VALUES (?,?,?,?)",
                               (emp["name"], emp["dept_id"], emp["password"], emp["position"]))
                employee_ids.append(cursor.lastrowid)

            # 插入管理员数据，只插入部门管理员
            admin_ids = []
            for i, emp in enumerate(employees):
                if emp["position"] == 1:
                    cursor.execute("INSERT INTO ADMINISTRATOR (Name, e_ID, d_ID, Contact_Info) VALUES (?,?,?,?)",
                                   (emp["name"], employee_ids[i], emp["dept_id"], "1300000000{}".format(i + 1)))
                    admin_ids.append(cursor.lastrowid)

            # 更新部门表的 a_ID 字段
            for i, dept_id in enumerate(department_ids):
                if i < len(admin_ids):
                    cursor.execute("UPDATE DEPARTMENT SET a_ID =? WHERE d_ID =?", (admin_ids[i], dept_id))

            conn.commit()
            print("测试数据插入成功")
        except sqlite3.Error as e:
            print(f"插入测试数据出错: {e}")
            conn.rollback()
        finally:
            conn.close()
'''
登陆页以及权限设置页部分的处理代码逻辑
'''

