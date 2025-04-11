import streamlit as st
from utils.data_utils import get_department_items, get_item_details

def show():
    st.title("资产查询")

    if "user" not in st.session_state or st.session_state.user is None:
        st.error("请先登录")
        return

    user = st.session_state.get("user", {})
    role = user.get("role", "guest")
    d_id = user.get("d_id", None)

    # ---------------------- 搜索栏 ----------------------
    col1, col2, col3 = st.columns([3, 2, 2])
    search_term = ""
    with col1:
        if role == "guest":
            search_term = st.text_input("搜索资产（支持资产ID）", placeholder="输入资产ID")
        else:
            search_term = st.text_input("搜索资产（支持资产ID或资产名称）", placeholder="输入资产ID或资产名称")
    with col2:
        status_filter = st.selectbox("筛选状态", options=["全部", "使用中", "报废"])
    with col3:
        if role != "guest":
            if st.button("查看年度采购总支出"):
                st.session_state["selected_page"] = "部门采购总支出"
                st.rerun()

    # 管理员显示新增资产按钮
    if role == "dep-admin" or role == "super-admin":
        # 触发跳转
        if st.button("新增资产"):
            st.session_state["selected_page"] = "新增物品录入信息"
            st.rerun()

    # ---------------------- 数据查询逻辑 ----------------------
    assets = []
    if role == "guest":
        # 访客仅支持按ID查询
        if search_term != "":
            if search_term.isdigit():
                asset = get_item_details(int(search_term))
                if asset:
                    assets = [asset]
                else:
                    st.warning("未找到对应资产")
            else:
                st.info("访客只能通过资产ID进行搜索")
    else:
        all_items = get_department_items(d_id)
        for item in all_items:
            if search_term:
                # 按资产ID或资产名模糊搜索
                if (str(item["ID"]).startswith(search_term) or search_term in item["Item_Name"]):
                    assets.append(item)
            else:
                assets.append(item)

        # 状态过滤
        if status_filter == "使用中":
            assets = [item for item in assets if item["Status"] == 1]
        elif status_filter == "报废":
            assets = [item for item in assets if item["Status"] == 0]

        # 当前价值排序
        if st.checkbox("按当前价值降序排列"):
            assets.sort(key=lambda x: x["Current_Value"], reverse=True)

    # ---------------------- 表格展示 ----------------------
    if (search_term != "") and (not assets):
        st.info("暂无符合条件的资产")
        return

    if len(assets) > 0:
        st.subheader("资产列表")
    for idx, item in enumerate(assets):
        with st.container():
            cols = st.columns([2, 2, 2, 2, 2])

            with cols[0]:
                st.markdown(f"**资产ID**: {item['ID']}")
                st.markdown(f"**资产名称**: {item['Item_Name']}")

            with cols[1]:
                st.markdown(f"**状态**: {'🟢 使用中' if item['Status'] == 1 else '🔴 报废'}")
                st.markdown(f"**存放位置**: {item['Placement_Location']}")

            if role != "guest":
                with cols[2]:
                    st.markdown(f"**管理部门ID**: {item.get('d_ID', '-')}")
                    st.markdown(f"**当前价值**: ￥{item['Current_Value']}")

            # 操作按钮列
            with cols[3]:
                if st.button(f"查看详情", key=f"view_{item['ID']}"):
                    st.session_state["selected_asset_id"] = item["ID"]
                    st.session_state["selected_page"] = "资产详情"
                    st.rerun()

            with cols[4]:
                if role == "dep-admin" or role == "super-admin":
                    if st.button("编辑状态", key=f"edit_{item['ID']}"):
                        st.session_state["edit_target_id"] = item["ID"]
                        st.session_state["selected_page"] = "编辑物品状态"
                        st.rerun()

        st.markdown("---")
