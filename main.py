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
    create_tables()
    test_login_add_data()
    # 标记数据库已初始化
    st.session_state.database_initialized = True


# 检查用户是否已登录
if st.session_state.user is None:
    # 未登录，显示登录页面
    login_page.show()
else:
    # 已登录，显示侧边栏导航
    if st.session_state.user["role"] == "guest":
        st.sidebar.write("您当前以访客身份登录。")
    else:
        st.sidebar.write(f"欢迎，{st.session_state.user['e_id']}！")
    if st.sidebar.button("退出登录"):
        st.session_state.user = None
        st.rerun()

    # 根据用户角色显示不同的页面选项
    if st.session_state.user["role"] == "super-admin":
        pages = ["资产查询", "资产详情", "部门采购总支出", "新增物品录入信息", "编辑物品状态", "账号权限设置"]
    elif st.session_state.user["role"] == "dep-admin":
        pages = ["资产查询", "资产详情", "部门采购总支出", "新增物品录入信息", "编辑物品状态"]
    elif st.session_state.user["role"] == "non-admin":
        pages = ["资产查询", "资产详情", "部门采购总支出"]
    else:  # 访客
        pages = ["资产查询", "资产详情"]

    # page = st.sidebar.selectbox("选择页面", pages)

    # 默认页面
    default_page = st.session_state.get("selected_page", pages[0])

    # 选择页面
    selected_page = st.sidebar.selectbox("选择页面", pages, index=pages.index(default_page))

    # 如果发生改变，更新 session_state 并立即重新运行
    if selected_page != st.session_state.get("selected_page"):
        st.session_state["selected_page"] = selected_page
        st.rerun()

    page = selected_page

    # 清除离开页面的相关状态
    previous_page = st.session_state.get("current_page")
    if previous_page != page:
        if previous_page == "资产详情":
            st.session_state.pop("selected_asset_id", None)
        elif previous_page == "编辑物品状态":
            st.session_state.pop("edit_target_id", None)
        elif previous_page == "新增物品录入信息":
            for key in ["item_name", "placement_location", "asset_cost", "purchase_year", "usable_life"]:
                st.session_state.pop(key, None)
        st.session_state["current_page"] = page

    if page == "资产查询":
        asset_query_page.show()
    elif page == "部门采购总支出":
        expenditure_page.show()
    elif page == "资产详情":
        asset_detail_page.show()
    elif page == "新增物品录入信息":
        add_asset_page.show()
    elif page == "编辑物品状态":
        edit_status_page.show()
    elif page == "账号权限设置":
        account_permission_page.show()