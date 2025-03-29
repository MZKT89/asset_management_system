import streamlit as st
from utils.auth import login, login_as_guest

def show():
    st.title("登录页")
    username = st.text_input("账号")
    password = st.text_input("密码", type="password")

    # 登录按钮
    if st.button("登录"):
        # auth.py - login 函数进行登录验证
        user = login(username, password)
        if user:
            # 登录成功，将用户信息存入会话状态
            st.session_state.user = user
            # 重新运行应用，跳转到主页面
            st.rerun()
        else:
            # 登录失败，显示错误信息
            st.error("账号或密码错误。")
        print("登录成功")
        

    # 以访客身份登录按钮
    if st.button("以访客身份登录"):
        # 调用 auth.py - login_as_guest 函数以访客身份登录
        st.session_state.user = login_as_guest()
        # 重新运行应用，跳转到主页面
        st.rerun()
        print("以访客身份登录成功")