import streamlit as st
from utils.data_utils import get_all_department_items, get_department_items, get_item_details, query_department_Name

def show():
    st.title("Asset Query")

    if "user" not in st.session_state or st.session_state.user is None:
        st.error("Please log in first")
        return

    user = st.session_state.get("user", {})
    role = user.get("role", "guest")
    d_id = user.get("d_id", None)

    # ---------------------- Search Bar ----------------------
    col1, col2, col3 = st.columns([3, 2, 2])
    search_term = ""
    with col1:
        if role == "guest":
            search_term = st.text_input("Search for assets (only supports asset ID)", placeholder="Enter asset ID")
        else:
            search_term = st.text_input("Search for assets (asset ID or asset name)", placeholder="Enter asset ID or asset name")
    with col2:
        if role != "guest":
            status_filter = st.selectbox("Filter by status", options=["All", "In use", "Scrapped"])
        else:
            status_filter = "All"  # Default filter for guest
    with col3:
        if role != "guest":
            if st.button("Annual Procurement 📊"):
                st.session_state["selected_page"] = "Annual Dept Procurement Expenditure 📈"
                st.rerun()

    # Show the button to add a new asset for administrators
    if role == "dep-admin" or role == "super-admin":
        # Trigger page jump
        if st.button("Add new asset"):
            st.session_state["selected_page"] = "Add New Asset"
            st.rerun()

    # ---------------------- Data Query Logic ----------------------
    assets = []
    if role == "guest":
        # Guests can only search by ID
        if search_term != "":
            if search_term.isdigit():
                asset = get_item_details(int(search_term))
                if asset:
                    assets = [asset]
                else:
                    st.warning("No corresponding asset found")
            else:
                st.info("Guests can only search by asset ID")

    else:
        all_items = (get_all_department_items() if role == "super-admin" else get_department_items(d_id))
        for item in all_items:
            if search_term:
                # Fuzzy search by asset ID or asset name
                if (str(item["ID"]).startswith(search_term) or search_term in item["Item_Name"]):
                    assets.append(item)
            else:
                assets.append(item)

        # Status filter
        if status_filter == "In use":
            assets = [item for item in assets if item["Status"] == 1]
        elif status_filter == "Scrapped":
            assets = [item for item in assets if item["Status"] == 0]

        # Sort by current value
        if st.checkbox("Sort by current value in descending order"):
            assets.sort(key=lambda x: x["Current_Value"], reverse=True)

    # ---------------------- Table Display ----------------------
    if (search_term != "") and (not assets):
        st.info("No assets meet the criteria for now")
        return

    if len(assets) > 0:
        st.subheader("Asset List")
    for idx, item in enumerate(assets):
        with st.container():
            cols = st.columns(4)  # 四列

            # 第一列，两行内容
            with cols[0]:
                st.markdown(f"**Asset ID**")
                st.markdown(f"{item['ID']}")
                st.markdown(f"**Asset Name**")
                st.markdown(f"{item['Item_Name']}")

            # 第二列，两行内容
            with cols[1]:
                st.markdown(f"**Status**")
                st.markdown("🟢 In use" if item["Status"] == 1 else "🔴 Scrapped")
                st.markdown(f"**Storage Location**")
                st.markdown(f"{item['Placement_Location']}")

            # 第三列，两行内容（根据角色显示部门信息）
            with cols[2]:
                d_ID = item["d_ID"]
                d_name = query_department_Name(d_ID) or "Unknown"
                if role != "guest":
                    st.markdown(f"**Managing Department**")
                    st.markdown(f"{d_name}")
                    st.markdown(f"**Current Value**")
                    st.markdown(f"￥{item['Current_Value']}")
                else:
                    st.markdown(f"**Managing Department**")
                    st.markdown(f"{d_name}")
                    st.markdown("")  # 空行保持对齐
                    st.markdown("")

            # 第四列，两行按钮
            with cols[3]:
                st.markdown("**Operations**")
                if st.button(f"View Details", key=f"view_{item['ID']}"):
                    st.session_state["selected_asset_id"] = item["ID"]
                    st.session_state["selected_page"] = "Asset Details"
                    st.rerun()
                if role in ("dep-admin", "super-admin"):
                    if st.button("Edit Status", key=f"edit_{item['ID']}"):
                        st.session_state["edit_target_id"] = item["ID"]
                        st.session_state["selected_page"] = "Edit Asset Status"
                        st.rerun()

        st.markdown("---")