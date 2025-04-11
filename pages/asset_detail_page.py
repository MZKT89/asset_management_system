import streamlit as st
from utils.data_utils import get_department_items, get_item_details, check_department_admin
import sqlite3
from utils.data_utils import create_connection

def get_purchase_records(item_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT p.ID, p.Asset_Cost, d.Department_Name
                FROM PURCHASE_INFO p
                JOIN DEPARTMENT d ON p.d_ID = d.d_ID
                WHERE p.ID = ?
            ''', (item_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"查询采购记录失败: {e}")
        finally:
            conn.close()
    return []

def show():
    st.title("资产详情页")

    user = st.session_state.get("user", {})
    role = user.get("role", "guest")
    e_id = user.get("e_id", None)
    d_id = user.get("d_id", None)
    passed_id = st.session_state.get("selected_asset_id", None)

    # 如果是 guest，只使用传入的 asset_id
    if role == "guest":
        if not passed_id:
            st.warning("访客请先从查询页面选择要查看的资产。")
            return
        asset = get_item_details(passed_id)
        if not asset:
            st.error("未找到该资产信息")
            return
    else:
        all_items = get_department_items(d_id)
        if not all_items:
            st.warning("没有可查看的资产")
            return

    # 构建访客的资产详情列表
    if role == "guest":
        item_options = {f"{asset['ID']} - {asset['Item_Name']}": asset['ID']}
    else:
        # 非访客
        item_options = {f"{item['ID']} - {item['Item_Name']}": item['ID'] for item in all_items}
    option_keys = list(item_options.keys())

    # 计算默认选项 key
    default_key = None
    if passed_id:
        for label, val in item_options.items():
            if val == passed_id:
                default_key = label
                break

    selected_item_key = st.selectbox(
        "选择资产",
        options=option_keys,
        index=option_keys.index(default_key) if default_key else 0,
        format_func=lambda x: x
    )

    selected_item_id = item_options[selected_item_key]
    asset = get_item_details(selected_item_id)
    st.session_state["selected_asset_id"] = selected_item_id  # 保持一致

    if not asset:
        st.error("未找到该资产信息")
        return

    purchase_records = get_purchase_records(asset["ID"])

    # ---------------------- 基本信息卡片 ----------------------
    st.subheader("基本信息")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**资产 ID**: {asset['ID']}")
        st.markdown(f"**资产名称**: {asset['Item_Name']}")
        st.markdown(f"**管理部门**: {asset['Department_Name']}")
        st.markdown(f"**存放位置**: {asset['Placement_Location']}")
        st.markdown(f"**状态**: {'🟢 使用中' if asset['Status'] == 1 else '🔴 报废'}")

    with cols[1]:
        # 获取采购信息（可能无记录）
        year = "-"
        life = "-"
        contact = "-"
        admin = "-"
        if purchase_records:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Purchase_Year, Usable_Life FROM PURCHASE_INFO WHERE ID = ?", (asset["ID"],))
            purchase = cursor.fetchone()
            if purchase:
                year = purchase[0]
                life = purchase[1]
            conn.close()
        st.markdown(f"**采购年份**: {year}")
        st.markdown(f"**使用寿命**: {life} 年")

        if role != "guest":
            st.markdown(f"**当前价值**: ￥{asset['Current_Value']:.2f}")

        # 获取管理员信息
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Name, Contact_Info FROM ADMINISTRATOR
            WHERE d_ID = ? LIMIT 1
        ''', (asset["d_ID"],))
        admin_info = cursor.fetchone()
        if admin_info:
            admin, contact = admin_info
        st.markdown(f"**部门管理员**: {admin}")
        st.markdown(f"**联系方式**: {contact}")

    # ---------------------- 采购记录（访客隐藏） ----------------------
    if role != "guest":
        st.subheader("采购记录")
        if purchase_records:
            st.table([
                {"采购单号": r[0], "采购金额": f"￥{r[1]:.2f}", "采购部门": r[2]}
                for r in purchase_records
            ])
        else:
            st.info("暂无采购记录")

    # ---------------------- 操作按钮（仅部门管理员） ----------------------
    if role == "dep-admin" and check_department_admin(e_id, asset["d_ID"]):
        if st.button("编辑物品状态", key="edit_status_from_detail"):
            st.session_state["edit_target_id"] = asset["ID"]
            st.session_state["selected_page"] = "编辑物品状态"
            st.rerun()

    # ---------------------- 返回按钮 ----------------------
    if st.button("返回查询页面"):
        st.session_state["selected_page"] = "资产查询"
        st.session_state.pop("selected_asset_id", None)
        st.rerun()
