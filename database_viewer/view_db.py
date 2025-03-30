import sqlite3

def list_tables(conn):
    """
    列出数据库中的所有表名
    :param conn: 数据库连接对象
    :return: 表名列表
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    return table_names

def view_table_data(conn, table_name):
    """
    查看指定表中的数据
    :param conn: 数据库连接对象
    :param table_name: 表名
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    print(f"表名: {table_name}")
    print("列名:", columns)
    for row in rows:
        print(row)
    print()

def main():
    # 连接到 SQLite 数据库文件
    # db_file = '../asset_management.db'
    db_file = '../local_test/assetdb.db'
    try:
        conn = sqlite3.connect(db_file)
        # 列出所有表名
        table_names = list_tables(conn)
        print("数据库中的表:")
        for table_name in table_names:
            print(table_name)
        print()
        # 查看每个表的数据
        for table_name in table_names:
            view_table_data(conn, table_name)
    except sqlite3.Error as e:
        print(f"数据库操作出错: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()