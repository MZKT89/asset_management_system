import streamlit as st
import datetime
import pandas as pd
from utils.data_utils import (
    get_department_expenditure,
    get_expenditure_trend,
    get_department_list,
)


def show():
    st.title("部门年度采购总支出统计")

    # 权限检查：访客无权访问该页面
    if st.session_state.user["role"] == "guest":
        st.error("访客没有权限访问此页面。")
        return

    user_role = st.session_state.user["role"]

    # 根据不同角色处理部门选择
    if user_role == "super-admin":
        dept_options = get_department_list()  # 返回 [(d_ID, Department_Name), ...]
        if not dept_options:
            st.error("无法获取部门数据")
            return
        # 创建下拉选择框：显示部门ID及名称
        dept_names = [f"{dept[0]} - {dept[1]}" for dept in dept_options]
        selected_index = st.selectbox(
            "选择部门", range(len(dept_options)), format_func=lambda i: dept_names[i]
        )
        selected_department_id = dept_options[selected_index][0]
    else:
        # 非超级管理员默认使用当前用户所属部门，并显示详细信息（如“2 - 市场部”）
        selected_department_id = st.session_state.user["d_id"]
        department_list = get_department_list()
        department_name = None
        for dept in department_list:
            if int(selected_department_id) == int(dept[0]):
                department_name = dept[1]
                break
        if department_name:
            st.info(f"当前部门：{selected_department_id} - {department_name}")
        else:
            st.info(f"当前部门：{selected_department_id}")

    # 年份选择器：默认当前年，允许从 2005 年到 2025 年选择
    current_year = datetime.datetime.now().year
    selected_year = st.number_input(
        "选择年份", min_value=2005, max_value=2025, value=current_year, step=1
    )

    # 调用后端函数获取数据
    expenditure_data = get_department_expenditure(selected_department_id, selected_year)
    trend_data = get_expenditure_trend(selected_department_id, selected_year)

    st.subheader("总支出金额")
    # 使用 st.metric 显示采购总支出及同比百分比
    st.metric(
        label=f"{selected_year} 年采购总支出",
        value=f"¥{expenditure_data['total_cost']}",
        delta=expenditure_data["comparison"],
    )

    st.subheader("近5年采购金额趋势")
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        df_trend.set_index("year", inplace=True)
        st.line_chart(df_trend["total_cost"])
    else:
        st.write("暂无数据")

    if st.button("返回查询页面"):
        st.session_state["selected_page"] = "资产查询"
        st.session_state.pop("edit_target_id", None)
        st.rerun()