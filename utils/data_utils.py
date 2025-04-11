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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DEPARTMENT (
                d_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Department_Name VARCHAR(100) NOT NULL,
                a_ID INTEGER,
                FOREIGN KEY (a_ID) REFERENCES ADMINISTRATOR(a_ID)
            )
        """)
        
        # 创建 ITEM 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ITEM (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Item_Name VARCHAR(100) NOT NULL,
                d_ID INTEGER NOT NULL,
                Placement_Location VARCHAR(100),
                Status INT CHECK (Status IN (0, 1)),
                Current_Value DECIMAL(10,2),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        """)
        
        # 创建 EMPLOYEE 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS EMPLOYEE (
                e_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name VARCHAR(100) NOT NULL,
                d_ID INTEGER NOT NULL,
                password VARCHAR(255),
                Position INT CHECK (Position IN (0, 1, 2)),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        """)
        
        # 创建 PURCHASE_INFO 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PURCHASE_INFO (
                ID INTEGER,
                Asset_Cost DECIMAL(10,2) NOT NULL,
                Purchase_Year INT,
                d_ID INTEGER NOT NULL,
                Usable_Life INT,
                FOREIGN KEY (ID) REFERENCES ITEM(ID),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        """)
        
        # 创建 ADMINISTRATOR 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ADMINISTRATOR (
                e_ID INTEGER,
                d_ID INTEGER,
                Name VARCHAR(100) NOT NULL,
                Contact_Info VARCHAR(255),
                PRIMARY KEY (e_ID, d_ID),
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID),
                FOREIGN KEY (e_ID) REFERENCES EMPLOYEE(e_ID)
            )
        """)
        # 创建位置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LOCATION (
                l_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Location_Name VARCHAR(100) NOT NULL,
                d_ID INTEGER,
                FOREIGN KEY (d_ID) REFERENCES DEPARTMENT(d_ID)
            )
        """)
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
            # 先清空所有表
            cursor.execute("DELETE FROM ADMINISTRATOR")
            cursor.execute("DELETE FROM PURCHASE_INFO")
            cursor.execute("DELETE FROM ITEM")
            cursor.execute("DELETE FROM EMPLOYEE")
            cursor.execute("DELETE FROM DEPARTMENT")
            cursor.execute("DELETE FROM LOCATION")  # 添加清空位置表
            
            # 重置自增ID
            cursor.execute("DELETE FROM sqlite_sequence")
            
            # 插入部门数据
            departments = ["研发部", "市场部"]
            department_ids = []
            for dept_name in departments:
                cursor.execute("INSERT INTO DEPARTMENT (Department_Name) VALUES (?)", (dept_name,))
                department_ids.append(cursor.lastrowid)

            # 添加测试位置数据
            locations = [
                ("办公室A", 1),
                ("办公室B", 1),
                ("实验室", 1),
                ("会议室", 1),
                ("仓库", 2),
                ("展厅", 2)
            ]
            
            for loc_name, dept_id in locations:
                cursor.execute("INSERT INTO LOCATION (Location_Name, d_ID) VALUES (?, ?)", 
                              (loc_name, dept_id))
            
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


def get_department_list():
    """
    获取所有部门列表
    :return: 部门列表 [(d_ID, Department_Name), ...]
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT DISTINCT d_ID, Department_Name FROM DEPARTMENT')  # 添加 DISTINCT
            departments = cursor.fetchall()
            return departments
        except sqlite3.Error as e:
            print(f"获取部门列表出错: {e}")
        finally:
            conn.close()
    return []

def add_new_item(item_data):
    """
    新增资产
    :param item_data: 包含资产信息的字典
    :return: 新增资产的ID，失败返回None
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 插入ITEM表
            cursor.execute('''
                INSERT INTO ITEM (Item_Name, d_ID, Placement_Location, Status, Current_Value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item_data['Item_Name'],
                item_data['d_ID'],
                item_data['Placement_Location'],
                item_data['Status'],
                item_data['Current_Value']
            ))
            item_id = cursor.lastrowid

            # 插入PURCHASE_INFO表
            cursor.execute('''
                INSERT INTO PURCHASE_INFO (ID, Asset_Cost, Purchase_Year, d_ID, Usable_Life)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item_id,
                item_data['Asset_Cost'],
                item_data['Purchase_Year'],
                item_data['d_ID'],
                item_data.get('Usable_Life')  # 可选字段
            ))

            conn.commit()
            return item_id
        except sqlite3.Error as e:
            print(f"新增资产出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    return None

def check_department_exists(d_id):
    """
    检查部门是否存在
    :param d_id: 部门ID
    :return: 布尔值
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM DEPARTMENT WHERE d_ID = ?', (d_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查部门存在出错: {e}")
        finally:
            conn.close()
    return False

def validate_item_data(item_data):
    """
    验证资产数据
    :param item_data: 资产数据字典
    :return: (是否有效, 错误信息)
    """
    if not item_data.get('Item_Name'):
        return False, "资产名称不能为空"
    
    if not check_department_exists(item_data.get('d_ID')):
        return False, "所选部门不存在"
    
    if not item_data.get('Placement_Location'):
        return False, "存放位置不能为空"
    
    if item_data.get('Asset_Cost', 0) <= 0:
        return False, "采购金额必须大于0"
    
    purchase_year = item_data.get('Purchase_Year', 0)
    if not (2005 <= purchase_year <= 2025):
        return False, "采购年份必须在2005-2025之间"
    
    return True, ""


def get_item_details(item_id):
    """
    获取资产详细信息
    :param item_id: 资产ID
    :return: 资产详细信息字典，不存在返回None
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT i.ID, i.Item_Name, i.d_ID, d.Department_Name, 
                       i.Placement_Location, i.Status, i.Current_Value
                FROM ITEM i
                JOIN DEPARTMENT d ON i.d_ID = d.d_ID
                WHERE i.ID = ?
            ''', (item_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "ID": result[0],
                    "Item_Name": result[1],
                    "d_ID": result[2],
                    "Department_Name": result[3],
                    "Placement_Location": result[4],
                    "Status": result[5],
                    "Current_Value": result[6]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取资产详情出错: {e}")
        finally:
            conn.close()
    return None

def check_department_admin(user_id, department_id):
    """
    检查用户是否为指定部门的管理员
    :param user_id: 用户ID
    :param department_id: 部门ID
    :return: 布尔值
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT 1 FROM ADMINISTRATOR 
                WHERE e_ID = ? AND d_ID = ?
            ''', (user_id, department_id))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查部门管理员权限出错: {e}")
        finally:
            conn.close()
    return False

def update_item_status(item_id, new_status, user_id):
    """
    更新资产状态
    :param item_id: 资产ID
    :param new_status: 新状态（0表示报废，1表示使用中）
    :param user_id: 操作用户ID
    :return: (是否成功, 错误信息)
    """
    # 获取资产信息
    item = get_item_details(item_id)
    if not item:
        return False, "资产不存在"
    
    # 检查用户权限
    if not check_department_admin(user_id, item['d_ID']):
        return False, "您没有权限修改此资产状态"
    
    # 验证状态值
    if new_status not in [0, 1]:
        return False, "无效的状态值"
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE ITEM 
                SET Status = ?
                WHERE ID = ?
            ''', (new_status, item_id))
            
            conn.commit()
            return True, "状态更新成功"
        except sqlite3.Error as e:
            print(f"更新资产状态出错: {e}")
            conn.rollback()
            return False, f"数据库错误: {str(e)}"
        finally:
            conn.close()
    return False, "数据库连接失败"

def get_department_items(department_id):
    """
    获取部门所有资产列表
    :param department_id: 部门ID
    :return: 资产列表
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT i.ID, i.Item_Name, i.Placement_Location, 
                       i.Status, i.Current_Value
                FROM ITEM i
                WHERE i.d_ID = ?
            ''', (department_id,))
            items = cursor.fetchall()
            return [{
                "ID": item[0],
                "Item_Name": item[1],
                "Placement_Location": item[2],
                "Status": item[3],
                "Current_Value": item[4]
            } for item in items]
        except sqlite3.Error as e:
            print(f"获取部门资产列表出错: {e}")
        finally:
            conn.close()
    return []

def get_location_list(department_id=None):
    """
    获取存放位置列表
    :param department_id: 部门ID（可选）
    :return: 位置列表 [(l_ID, Location_Name), ...]
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if department_id:
                cursor.execute('SELECT l_ID, Location_Name FROM LOCATION WHERE d_ID = ?', (department_id,))
            else:
                cursor.execute('SELECT l_ID, Location_Name FROM LOCATION')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取位置列表出错: {e}")
        finally:
            conn.close()
    return []

def test_login_add_data():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            # 添加测试位置数据
            locations = [
                ("办公室A", 1),
                ("办公室B", 1),
                ("实验室", 1),
                ("会议室", 1),
                ("仓库", 2),
                ("展厅", 2)
            ]
            
            for loc_name, dept_id in locations:
                cursor.execute("INSERT INTO LOCATION (Location_Name, d_ID) VALUES (?, ?)", 
                              (loc_name, dept_id))
        except sqlite3.Error as e:
            print(f"插入测试数据出错: {e}")
            conn.rollback()
        finally:
            conn.close()
'''
登陆页以及权限设置页部分的处理代码逻辑
'''


def get_department_list():
    """
    获取所有部门列表
    :return: 部门列表 [(d_ID, Department_Name), ...]
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT DISTINCT d_ID, Department_Name FROM DEPARTMENT')  # 添加 DISTINCT
            departments = cursor.fetchall()
            return departments
        except sqlite3.Error as e:
            print(f"获取部门列表出错: {e}")
        finally:
            conn.close()
    return []

def add_new_item(item_data):
    """
    新增资产
    :param item_data: 包含资产信息的字典
    :return: 新增资产的ID，失败返回None
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 插入ITEM表
            cursor.execute('''
                INSERT INTO ITEM (Item_Name, d_ID, Placement_Location, Status, Current_Value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item_data['Item_Name'],
                item_data['d_ID'],
                item_data['Placement_Location'],
                item_data['Status'],
                item_data['Current_Value']
            ))
            item_id = cursor.lastrowid

            # 插入PURCHASE_INFO表
            cursor.execute('''
                INSERT INTO PURCHASE_INFO (ID, Asset_Cost, Purchase_Year, d_ID, Usable_Life)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item_id,
                item_data['Asset_Cost'],
                item_data['Purchase_Year'],
                item_data['d_ID'],
                item_data.get('Usable_Life')  # 可选字段
            ))

            conn.commit()
            return item_id
        except sqlite3.Error as e:
            print(f"新增资产出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    return None

def check_department_exists(d_id):
    """
    检查部门是否存在
    :param d_id: 部门ID
    :return: 布尔值
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM DEPARTMENT WHERE d_ID = ?', (d_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查部门存在出错: {e}")
        finally:
            conn.close()
    return False

def validate_item_data(item_data):
    """
    验证资产数据
    :param item_data: 资产数据字典
    :return: (是否有效, 错误信息)
    """
    if not item_data.get('Item_Name'):
        return False, "资产名称不能为空"
    
    if not check_department_exists(item_data.get('d_ID')):
        return False, "所选部门不存在"
    
    if not item_data.get('Placement_Location'):
        return False, "存放位置不能为空"
    
    if item_data.get('Asset_Cost', 0) <= 0:
        return False, "采购金额必须大于0"
    
    purchase_year = item_data.get('Purchase_Year', 0)
    if not (2005 <= purchase_year <= 2025):
        return False, "采购年份必须在2005-2025之间"
    
    return True, ""


def get_item_details(item_id):
    """
    获取资产详细信息
    :param item_id: 资产ID
    :return: 资产详细信息字典，不存在返回None
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT i.ID, i.Item_Name, i.d_ID, d.Department_Name, 
                       i.Placement_Location, i.Status, i.Current_Value
                FROM ITEM i
                JOIN DEPARTMENT d ON i.d_ID = d.d_ID
                WHERE i.ID = ?
            ''', (item_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "ID": result[0],
                    "Item_Name": result[1],
                    "d_ID": result[2],
                    "Department_Name": result[3],
                    "Placement_Location": result[4],
                    "Status": result[5],
                    "Current_Value": result[6]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取资产详情出错: {e}")
        finally:
            conn.close()
    return None

def check_department_admin(user_id, department_id):
    """
    检查用户是否为指定部门的管理员
    :param user_id: 用户ID
    :param department_id: 部门ID
    :return: 布尔值
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT 1 FROM ADMINISTRATOR 
                WHERE e_ID = ? AND d_ID = ?
            ''', (user_id, department_id))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查部门管理员权限出错: {e}")
        finally:
            conn.close()
    return False

def update_item_status(item_id, new_status, user_id):
    """
    更新资产状态
    :param item_id: 资产ID
    :param new_status: 新状态（0表示报废，1表示使用中）
    :param user_id: 操作用户ID
    :return: (是否成功, 错误信息)
    """
    # 获取资产信息
    item = get_item_details(item_id)
    if not item:
        return False, "资产不存在"
    
    # 检查用户权限
    if not check_department_admin(user_id, item['d_ID']):
        return False, "您没有权限修改此资产状态"
    
    # 验证状态值
    if new_status not in [0, 1]:
        return False, "无效的状态值"
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE ITEM 
                SET Status = ?
                WHERE ID = ?
            ''', (new_status, item_id))
            
            conn.commit()
            return True, "状态更新成功"
        except sqlite3.Error as e:
            print(f"更新资产状态出错: {e}")
            conn.rollback()
            return False, f"数据库错误: {str(e)}"
        finally:
            conn.close()
    return False, "数据库连接失败"

def get_department_items(department_id):
    """
    获取部门所有资产列表
    :param department_id: 部门ID
    :return: 资产列表
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT i.ID, i.Item_Name, i.Placement_Location, 
                       i.Status, i.Current_Value
                FROM ITEM i
                WHERE i.d_ID = ?
            ''', (department_id,))
            items = cursor.fetchall()
            return [{
                "ID": item[0],
                "Item_Name": item[1],
                "Placement_Location": item[2],
                "Status": item[3],
                "Current_Value": item[4]
            } for item in items]
        except sqlite3.Error as e:
            print(f"获取部门资产列表出错: {e}")
        finally:
            conn.close()
    return []

def get_department_expenditure(department_id, year):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 查询当前年的总采购成本
            cursor.execute("""
                SELECT SUM(Asset_Cost)
                FROM PURCHASE_INFO
                WHERE d_ID = ? AND Purchase_Year = ?
            """, (department_id, year))
            result = cursor.fetchone()
            total_cost = result[0] if result[0] is not None else 0

            # 查询上一年的采购成本（用于比较）
            cursor.execute("""
                SELECT SUM(Asset_Cost)
                FROM PURCHASE_INFO
                WHERE d_ID = ? AND Purchase_Year = ?
            """, (department_id, year - 1))
            result_prev = cursor.fetchone()
            previous_cost = result_prev[0] if result_prev[0] is not None else 0

            # 计算同比增减比例
            if previous_cost > 0:
                change_percentage = ((total_cost - previous_cost) / previous_cost) * 100
                comparison = f"{'+' if change_percentage >= 0 else ''}{round(change_percentage)}%"
            else:
                comparison = "N/A"

            return {"total_cost": total_cost, "comparison": comparison}
        except sqlite3.Error as e:
            print(f"计算部门采购总支出出错: {e}")
            return {"total_cost": 0, "comparison": "Error"}
        finally:
            conn.close()
    return {"total_cost": 0, "comparison": "No Connection"}
def get_expenditure_trend(department_id, current_year):
    """
    获取指定部门近 5 年（包括当前年）的采购趋势数据
    :param department_id: 部门ID
    :param current_year: 当前年份（例如 2023）
    :return: 返回一个列表，每项为字典，包含年份和对应的采购总支出，例如：
             [
                {"year": 2019, "total_cost": 45000},
                {"year": 2020, "total_cost": 48000},
                {"year": 2021, "total_cost": 50000},
                {"year": 2022, "total_cost": 52000},
                {"year": 2023, "total_cost": 50000}
             ]
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            start_year = current_year - 4
            # 查询从 start_year 到 current_year 之间各年的采购总成本数据
            cursor.execute("""
                SELECT Purchase_Year, SUM(Asset_Cost) as total_cost
                FROM PURCHASE_INFO
                WHERE d_ID = ? AND Purchase_Year BETWEEN ? AND ?
                GROUP BY Purchase_Year
                ORDER BY Purchase_Year ASC
            """, (department_id, start_year, current_year))
            results = cursor.fetchall()
            # 将查询结果转换为字典形式，便于后续补全数据
            trend_dict = {year: total_cost if total_cost is not None else 0 for (year, total_cost) in results}
            
            # 构造完整的 5 年数据，如果某年无数据，则 total_cost 为 0
            trend_data = []
            for year in range(start_year, current_year + 1):
                trend_data.append({
                    "year": year,
                    "total_cost": trend_dict.get(year, 0)
                })
            return trend_data
        except sqlite3.Error as e:
            print(f"获取采购趋势数据出错: {e}")
        finally:
            conn.close()
    return []
