import streamlit as st
from utils.data_utils import get_all_users, update_user_role, add_new_user
import time

def show():
    st.title("账号权限设置页")

    # 获取所有用户信息
    # users = get_all_users()

    # if users:
    #     # 显示用户表格
    #     st.write("所有用户信息：")
    #     # e_ID, Name, password, d_ID, Position
    #     headers = ["ID", "姓名", "密码", "部门 ID", "Position"]
    #     st.table([dict(zip(headers, user)) for user in users])

    #     # 编辑角色功能
    #     st.write("编辑用户角色：")
    #     user_id = st.number_input("请输入要编辑的用户 ID", min_value=1, step=1, value=None)
    #     new_role = st.selectbox("Please choose new postion for the employee", ["non admin", "department admin", "super admin"], key="update_position_select")
    #     # 将角色转换为对应的数字
    #     new_role_num = convertRoleToNumber(new_role)

    #     contact = None
    #     if new_role_num == 1:
    #         contact = st.text_input("请输入联系方式")

    #     if st.button("更新角色"):
    #         if user_id and new_role_num is not None:
    #             if new_role_num == 1 and not contact:
    #                 st.error("请输入联系方式")
    #             else:
    #                 if update_user_role(user_id, new_role_num, contact):
    #                     st.success("角色更新成功！")
    #                     # 实现倒计时
    #                     countdown_placeholder = st.empty()
    #                     for remaining in range(2, 0, -1):
    #                         countdown_placeholder.text(f'页面将在 {remaining} 秒后刷新...')
    #                         time.sleep(1)
    #                     countdown_placeholder.empty()
    #                     st.rerun()
    #                     # st.rerun()
    #                 else:
    #                     st.error("角色更新失败，请检查用户 ID 是否正确。")
    #         else:
    #             st.error("请输入有效的用户 ID 并选择角色。")

        # 获取所有用户信息

    st.sidebar.title("选择操作")
    selected_operation = st.sidebar.radio("选择一个操作", ["查看用户信息", "编辑用户角色", "新增用户"])

    users = get_all_users()

    if users:
        if selected_operation == "查看用户信息":
            # 分页设置
            items_per_page = 10
            num_pages = len(users) // items_per_page + (1 if len(users) % items_per_page != 0 else 0)
            page_options = [f"第 {i + 1} 页" for i in range(num_pages)]
            selected_page = st.selectbox("选择页码", page_options)
            current_page = page_options.index(selected_page)

            start_index = current_page * items_per_page
            end_index = start_index + items_per_page
            current_users = users[start_index:end_index]

            converted_users = []
            for user in current_users:
                user = list(user)
                user[3] = convert_role(user[3])
                converted_users.append(user)
            # 显示用户表格
            st.write("所有用户信息：")
            # e_ID, Name, d_ID, Position
            headers = ["ID", "姓名", "部门 ID", "Position"]
            st.table([dict(zip(headers, user)) for user in converted_users])

        elif selected_operation == "编辑用户角色":
            # 编辑角色功能
            st.write("编辑用户角色：")
            user_id = st.number_input("请输入要编辑的用户 ID", min_value=1, step=1, value=None)
            new_role = st.selectbox("Please choose new postion for the employee", ["non admin", "department admin", "super admin"],
                                    key="update_position_select")
            # 将角色转换为对应的数字
            new_role_num = convert_role(new_role)

            contact = None
            if new_role_num == 1:
                contact = st.text_input("请输入联系方式")

            if st.button("更新角色"):
                if user_id and new_role_num is not None:
                    if new_role_num == 1 and not contact:
                        st.error("请输入联系方式")
                    else:
                        if update_user_role(user_id, new_role_num, contact):
                            st.success("角色更新成功！")
                            # 实现倒计时
                            countdown_placeholder = st.empty()
                            for remaining in range(2, 0, -1):
                                countdown_placeholder.text(f'页面将在 {remaining} 秒后刷新...')
                                time.sleep(1)
                            countdown_placeholder.empty()
                            st.rerun()
                        else:
                            st.error("角色更新失败，请检查用户 ID 是否正确。")
                else:
                    st.error("请输入有效的用户 ID 并选择角色。")

        elif selected_operation == "新增用户":
            # 新增用户功能
            st.write("新增用户：")
            E_name = st.text_input("请输入员工姓名")
            password = st.text_input("请输入密码", type="password")
            department_id = st.number_input("请输入部门 ID", min_value=1, step=1, value=None)
            position = st.selectbox("Please choose new postion for the employee", ["non admin", "department admin", "super admin"], key="add_user_position_select")
            position_num = convert_role(position)

            new_contact = None
            if position_num == 1:
                new_contact = st.text_input("请为新用户输入联系方式")

            if st.button("新增用户"):
                if E_name and password and department_id and position_num is not None:
                    if position_num == 1 and not new_contact:
                        st.error("请为新用户输入联系方式")
                    else:
                        if add_new_user(E_name, password, department_id, position_num, new_contact):
                            st.success("用户新增成功！")
                            countdown_placeholder = st.empty()
                            for remaining in range(2, 0, -1):
                                countdown_placeholder.text(f'页面将在 {remaining} 秒后刷新...')
                                time.sleep(1)
                            countdown_placeholder.empty()
                            st.rerun()
                        else:
                            st.error("用户新增失败，请检查输入信息。")
                else:
                    st.error("请完整输入员工姓名、密码、部门 ID 并选择角色。")

def convert_role(role):
    role_mapping = {
        "non admin": 0,
        "department admin": 1,
        "super admin": 2
    }
    inverse_mapping = {v: k for k, v in role_mapping.items()}

    if isinstance(role, str):
        if role in role_mapping:
            return role_mapping[role]
        else:
            st.error("无效的角色名称。")
            return None
    elif isinstance(role, int):
        if role in inverse_mapping:
            return inverse_mapping[role]
        else:
            st.error("无效的角色数字。")
            return None
    else:
        st.error("输入类型必须是字符串或整数。")
        return None