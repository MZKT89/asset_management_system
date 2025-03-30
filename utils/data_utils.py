import sqlite3


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
                Position INT CHECK (Position IN (0, 1)),
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
        # 创建 ADMINISTRATOR 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ADMINISTRATOR (
                a_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name VARCHAR(100) NOT NULL,
                e_ID VARCHAR(50) UNIQUE NOT NULL,
                Contact_Info VARCHAR(255),
                FOREIGN KEY (e_ID) REFERENCES EMPLOYEE(e_ID)
            )
        ''')
        conn.commit()
        conn.close()
        
# 插入数据函数示例
def insert_department(department_name, a_id):
    """
    向 DEPARTMENT 表插入数据
    :param department_name: 部门名称
    :param a_id: 管理员 ID
    :return: 插入结果
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO DEPARTMENT (Department_Name, a_ID)
                VALUES (?,?)
            ''', (department_name, a_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    return False


# 查询数据函数示例
def get_department(d_id):
    """
    根据部门 ID 查询 DEPARTMENT 表中的数据
    :param d_id: 部门 ID
    :return: 查询结果
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM DEPARTMENT WHERE d_ID =?
        ''', (d_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    return None


# 更新数据函数示例
def update_department(d_id, department_name, a_id):
    """
    更新 DEPARTMENT 表中的数据
    :param d_id: 部门 ID
    :param department_name: 部门名称
    :param a_id: 管理员 ID
    :return: 更新结果
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE DEPARTMENT
                SET Department_Name =?, a_ID =?
                WHERE d_ID =?
            ''', (department_name, a_id, d_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    return False


# 删除数据函数示例
def delete_department(d_id):
    """
    根据部门 ID 删除 DEPARTMENT 表中的数据
    :param d_id: 部门 ID
    :return: 删除结果
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM DEPARTMENT WHERE d_ID =?
            ''', (d_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    return False


# 你可以按照上述示例为其他表添加插入、查询、更新和删除函数    