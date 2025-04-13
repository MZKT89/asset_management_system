import streamlit as st
from pages import login_page, asset_query_page, expenditure_page, asset_detail_page, add_asset_page, edit_status_page, account_permission_page
from utils.auth import *
from utils.data_utils import create_tables

print(f"st.session_state: {st.session_state}")

pages = {
    "Your account": [
        st.Page("pages/login_page.py", title="Login"),
    ],
    # "Resources": [
    #     st.Page("learn.py", title="Learn about us"),
    #     st.Page("trial.py", title="Try it out"),
    # ],
}

pg = st.navigation(pages)

# 初始化会话状态
if 'user' not in st.session_state:
    st.session_state.user = None

# 检查数据库是否已经初始化
if 'database_initialized' not in st.session_state:
    # 数据库未初始化，调用 create_database 函数
    # create_tables()
    # test_login_add_data()
    # 标记数据库已初始化
    st.session_state.database_initialized = True


# 检查用户是否已登录
if st.session_state.user is None:
    # 未登录，显示登录页面
    login_page.show()
else:
    # 已登录，显示侧边栏导航
    if st.session_state.user["role"] == "guest":
        st.sidebar.write("You are currently logged in as a guest.")
    else:
        # 自定义 CSS 样式
        st.markdown("""
        <style>
           .profile-card {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
           .profile-card h3 {
                margin-top: 0;
                color: #333;
            }
           .profile-card p {
                margin: 5px 0;
                color: #666;
            }
        </style>
        """, unsafe_allow_html=True)

        user_info = f"<h3>Welcome, {st.session_state.user['Name']}!</h3>"
        user_info += f"<p>Employee ID: {st.session_state.user['e_id']}</p>"
        user_info += f"<p>Role: {st.session_state.user['role']}</p>"
        user_info += f"<p>Department ID: {st.session_state.user['d_id']}</p>"
        user_info += f"<p>Department Name: {st.session_state.user['DepartmentName']}</p>"

        # 使用 HTML 卡片展示用户信息
        st.sidebar.markdown(f'<div class="profile-card">{user_info}</div>', unsafe_allow_html=True)

    if st.sidebar.button("Log out"):
        st.session_state.user = None
        st.rerun()

    # 根据用户角色显示不同的页面选项
    if st.session_state.user["role"] == "super-admin":
        pages = ["Asset Query", "Asset Details", "Annual Dept Procurement Expenditure 📈", "Add New Asset", "Edit Asset Status", "Account Permission Settings"]
    elif st.session_state.user["role"] == "dep-admin":
        pages = ["Asset Query", "Asset Details", "Annual Dept Procurement Expenditure 📈", "Add New Asset", "Edit Asset Status"]
    elif st.session_state.user["role"] == "non-admin":
        pages = ["Asset Query", "Asset Details", "Annual Dept Procurement Expenditure 📈"]
    else:  # 访客
        pages = ["Asset Query", "Asset Details"]

    # 默认页面
    default_page = st.session_state.get("selected_page", pages[0])

    # 选择页面
    selected_page = st.sidebar.selectbox("Select a page", pages, index=pages.index(default_page))

    # 如果发生改变，更新 session_state 并立即重新运行
    if selected_page != st.session_state.get("selected_page"):
        st.session_state["selected_page"] = selected_page
        st.rerun()

    page = selected_page

    # 清除离开页面的相关状态
    previous_page = st.session_state.get("current_page")
    if previous_page != page:
        if previous_page == "Asset Details":
            st.session_state.pop("selected_asset_id", None)
        elif previous_page == "Edit Asset Status":
            st.session_state.pop("edit_target_id", None)
        elif previous_page == "Add New Asset":
            for key in ["item_name", "placement_location", "asset_cost", "purchase_year", "usable_life"]:
                st.session_state.pop(key, None)
        st.session_state["current_page"] = page

    if page == "Asset Query":
        asset_query_page.show()
    elif page == "Annual Dept Procurement Expenditure 📈":
        expenditure_page.show()
    elif page == "Asset Details":
        asset_detail_page.show()
    elif page == "Add New Asset":
        add_asset_page.show()
    elif page == "Edit Asset Status":
        edit_status_page.show()
    elif page == "Account Permission Settings":
        account_permission_page.show()
    