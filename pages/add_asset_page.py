import streamlit as st
from datetime import datetime
from utils.data_utils import (
    get_department_list,
    add_new_item,
    validate_item_data
)

def add_asset_page():
    st.title("新增资产")

    # 显示资产是否添加成功的消息
    if "asset_add_success" in st.session_state:
        st.success(st.session_state["asset_add_success"])
        del st.session_state["asset_add_success"]


    # 获取部门列表
    departments = get_department_list()
    if not departments:
        st.error("无法获取部门列表")
        return
    
    # 初始化表单字段默认值（首次访问&提交后除“部门”选项外其他全部自动初始化）
    if "item_name" not in st.session_state:
        st.session_state["item_name"] = ""
    if "placement_location" not in st.session_state:
        st.session_state["placement_location"] = ""
    if "asset_cost" not in st.session_state:
        st.session_state["asset_cost"] = 0.01
    if "purchase_year" not in st.session_state:
        st.session_state["purchase_year"] = datetime.now().year
    if "usable_life" not in st.session_state:
        st.session_state["usable_life"] = 5

    # 表单
    with st.form("add_asset_form"):
        # 资产ID（自动生成）
        item_id = st.text_input("资产ID", value="自动生成", disabled=True)
        
        # 资产名称
        item_name = st.text_input("资产名称*", key="item_name")
        
        # 所属部门
        department = st.selectbox(
            "所属部门*",
            options=list(dict.fromkeys(departments)),  # 去重
            format_func=lambda x: x[1]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            # 采购金额
            asset_cost = st.number_input(
                "采购金额*", 
                min_value=0.01, 
                format="%.2f",
                # value=0.01,
                key="asset_cost"
            )
        
        with col2:
            # 采购年份
            current_year = datetime.now().year
            purchase_year = st.number_input(
                "采购年份*", 
                min_value=2005, 
                max_value=2025, 
                # value=current_year,
                key="purchase_year"
            )
        
        # 存放位置
        placement_location = st.text_input("存放位置*", key="placement_location")
        
        col3, col4 = st.columns(2)
        with col3:
            # 使用年限
            usable_life = st.number_input(
                "使用年限（年）", 
                min_value=1,
                # value=5,
                key="usable_life"
            )
        
        # 提交按钮
        submitted = st.form_submit_button("提交")
        
        if submitted:
            # 验证必填字段
            if not item_name:
                st.error("请输入资产名称")
                return
            
            if not placement_location:
                st.error("请输入存放位置")
                return
            
            # 准备提交数据
            asset_data = {
                "Item_Name": item_name,
                "d_ID": department[0],
                "Placement_Location": placement_location,
                "Status": 1,
                "Current_Value": asset_cost,
                "Asset_Cost": asset_cost,
                "Purchase_Year": int(purchase_year),
                "Usable_Life": usable_life
            }
            
            # 使用验证函数验证数据
            is_valid, error_msg = validate_item_data(asset_data)
            
            if not is_valid:
                st.error(f"数据验证失败：{error_msg}")
                return
            
            # 添加资产
            new_item_id = add_new_item(asset_data)
            
            if new_item_id:
                st.session_state["asset_add_success"] = f"资产添加成功！资产ID：{new_item_id}"
                # 提交成功后清空表单字段
                for key in ["item_name", "placement_location", "asset_cost", "purchase_year", "usable_life"]:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("添加失败，请稍后重试")
    # 返回按钮        
    if st.button("返回查询页面"):
        st.session_state["selected_page"] = "资产查询"
        st.rerun()

def show():
    add_asset_page()

if __name__ == "__main__":
    show()