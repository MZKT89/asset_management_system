import streamlit as st
from utils.data_utils import (
    get_department_items,
    get_item_details,
    update_item_status,
    check_department_admin
)

def show():
    st.title("编辑物品状态")

    # 检查用户是否登录
    if "user" not in st.session_state or st.session_state.user is None:
        st.error("请先登录")
        return

    if "edit_success" in st.session_state:
        st.success(st.session_state["edit_success"])
        st.session_state.pop("edit_success", None)

    user = st.session_state.user
    
    # 获取用户所在部门的资产列表
    items = get_department_items(user["d_id"])
    
    if not items:
        st.warning("当前部门没有可编辑的资产")
        return

    # # 创建资产选择器
    # item_options = {f"{item['ID']} - {item['Item_Name']}": item['ID'] for item in items}
    # selected_item_key = st.selectbox(
    #     "选择资产",
    #     options=list(item_options.keys()),
    #     format_func=lambda x: x
    # )

    # 获取传入的资产ID
    edit_id = st.session_state.get("edit_target_id", None)

    # 构建资产选择项
    item_options = {f"{item['ID']} - {item['Item_Name']}": item['ID'] for item in items}
    option_keys = list(item_options.keys())

    # 根据传入 ID 选中对应选项（如果存在）
    default_key = None
    if edit_id:
        for label, val in item_options.items():
            if val == edit_id:
                default_key = label
                break

    selected_item_key = st.selectbox(
        "选择资产",
        options=option_keys,
        index=option_keys.index(default_key) if default_key else 0,
        format_func=lambda x: x
    )

    if selected_item_key:
        selected_item_id = item_options[selected_item_key]
        item_details = get_item_details(selected_item_id)
        
        if item_details:
            # 检查用户是否为部门管理员
            is_admin = check_department_admin(user["e_id"], item_details["d_ID"])
            
            # 显示资产详情
            with st.form("edit_status_form"):
                st.text_input("资产ID", value=item_details["ID"], disabled=True)
                st.text_input("资产名称", value=item_details["Item_Name"], disabled=True)
                st.text_input("所属部门", value=item_details["Department_Name"], disabled=True)
                st.text_input("存放位置", value=item_details["Placement_Location"], disabled=True)
                st.number_input("当前价值", value=float(item_details["Current_Value"]), disabled=True)
                
                # 状态选择
                current_status = item_details["Status"]
                new_status = st.selectbox(
                    "状态",
                    options=[(1, "使用中"), (0, "报废")],
                    format_func=lambda x: x[1],
                    index=0 if current_status == 1 else 1,
                    disabled=not is_admin
                )
                
                submitted = st.form_submit_button("提交修改")
                
                if submitted:
                    if not is_admin:
                        st.error("您没有权限修改资产状态")
                    elif new_status[0] == current_status:
                        st.warning("状态未发生变化")
                    else:
                        success, message = update_item_status(
                            item_details["ID"],
                            new_status[0],
                            user["e_id"]
                        )
                        
                        if success:
                            st.session_state["edit_success"] = message
                            # st.session_state.pop("edit_target_id", None)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.error("无法获取资产详情")

    if st.button("返回查询页面"):
        st.session_state["selected_page"] = "资产查询"
        st.session_state.pop("edit_target_id", None)
        st.rerun()

if __name__ == "__main__":
    show()