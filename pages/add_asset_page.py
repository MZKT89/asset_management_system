import streamlit as st
from datetime import datetime
from utils.data_utils import (
    get_department_list,
    add_new_item,
    validate_item_data
)

def add_asset_page():
    st.title("新增资产")

    # 获取部门列表
    departments = get_department_list()
    if not departments:
        st.error("无法获取部门列表")
        return
    
    # 表单
    with st.form("add_asset_form"):
        # 资产ID（自动生成）
        item_id = st.text_input("资产ID", value="自动生成", disabled=True)
        
        # 资产名称
        item_name = st.text_input("资产名称*")
        
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
                value=0.01
            )
        
        with col2:
            # 采购年份
            current_year = datetime.now().year
            purchase_year = st.number_input(
                "采购年份*", 
                min_value=2005, 
                max_value=2025, 
                value=current_year
            )
        
        # 存放位置
        placement_location = st.text_input("存放位置*")
        
        col3, col4 = st.columns(2)
        with col3:
            # 使用年限
            usable_life = st.number_input(
                "使用年限（年）", 
                min_value=1,
                value=5
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
                st.success(f"资产添加成功！资产ID：{new_item_id}")
                st.experimental_rerun()
            else:
                st.error("添加失败，请稍后重试")

def show():
    add_asset_page()

if __name__ == "__main__":
    show()