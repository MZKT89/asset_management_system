import streamlit as st
from utils.auth import login, login_as_guest

def show():
    st.title("Login👇")
    username = st.text_input("Your EID")
    password = st.text_input("Password", type="password")

    # 登录按钮
    if st.button("Login"):
        # auth.py - login 函数进行登录验证
        user = login(username, password)
        print(user)
        if user:
            # 登录成功，将用户信息存入会话状态
            st.session_state.user = user
            st.session_state["selected_page"] = "Asset Query"  # 登录成功后默认跳转到查询页面
            print('Login through USER! Change default page to asset query!')
            # 清除之前遗留的资产ID等状态
            st.session_state.pop("selected_asset_id", None)
            st.session_state.pop("edit_target_id", None)            
            # 重新运行应用，跳转到主页面
            st.rerun()
        else:
            # 登录失败，显示错误信息
            st.error("The account or password is incorrect.")
        

    # 以访客身份登录按钮
    if st.button("Log in as a guest"):
        # 调用 auth.py - login_as_guest 函数以访客身份登录
        st.session_state.user = login_as_guest()
        st.session_state["selected_page"] = "Asset Query"  # 登录成功后默认跳转到查询页面
        print('Login through GUEST! Change default page to asset query!')
        # 清除之前遗留的资产ID等状态
        st.session_state.pop("selected_asset_id", None)
        st.session_state.pop("edit_target_id", None)            
        # 重新运行应用，跳转到主页面
        st.rerun()
        print("以访客身份登录成功")