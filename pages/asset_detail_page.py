import streamlit as st
from utils.data_utils import get_department_items, get_item_details, check_department_admin, get_all_department_items, get_purchase_records
import sqlite3
from utils.data_utils import create_connection

def show():
    st.title("Asset Details")

    user = st.session_state.get("user", {})
    role = user.get("role", "guest")
    e_id = user.get("e_id", None)
    d_id = user.get("d_id", None)
    passed_id = st.session_state.get("selected_asset_id", None)

    # If it's a guest, only use the passed asset_id
    if role == "guest":
        if not passed_id:
            st.warning("Guests please select an asset to view from the query page first.")
            return
        asset = get_item_details(passed_id)
        if not asset:
            st.error("Asset information not found.")
            return
    else:
        all_items = (get_all_department_items() if role == "super-admin" else get_department_items(d_id))
        if not all_items:
            st.warning("There are no assets to view.")
            return

    # Build the asset details list for guests
    if role == "guest":
        item_options = {f"{asset['ID']} - {asset['Item_Name']}": asset['ID']}
    else:
        # Non - guests
        item_options = {f"{item['ID']} - {item['Item_Name']}": item['ID'] for item in all_items}
    option_keys = list(item_options.keys())

    # Calculate the default option key
    default_key = None
    if passed_id:
        for label, val in item_options.items():
            if val == passed_id:
                default_key = label
                break

    selected_item_key = st.selectbox(
        "Select an asset",
        options=option_keys,
        index=option_keys.index(default_key) if default_key else 0,
        format_func=lambda x: x
    )

    selected_item_id = item_options[selected_item_key]
    asset = get_item_details(selected_item_id)

    if not asset:
        st.error("Asset information not found.")
        return

    purchase_records = get_purchase_records(asset["ID"])

    # ---------------------- Basic Information Card ----------------------
    st.subheader("Basic Information")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Asset ID**: {asset['ID']}")
        st.markdown(f"**Asset Name**: {asset['Item_Name']}")
        st.markdown(f"**Managing Department**: {asset['Department_Name']}")
        st.markdown(f"**Storage Location**: {asset['Placement_Location']}")
        st.markdown(f"**Status**: {'🟢 In use' if asset['Status'] == 1 else '🔴 Scrapped'}")

    with cols[1]:
        # Get purchase information (there may be no records)
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
        st.markdown(f"**Purchase Year**: {year}")
        st.markdown(f"**Service Life**: {life} years")

        if role != "guest":
            st.markdown(f"**Current Value**: ￥{asset['Current_Value']:.2f}")

        # Get administrator information
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Name, Contact_Info FROM ADMINISTRATOR
            WHERE d_ID = ? LIMIT 1
        ''', (asset["d_ID"],))
        admin_info = cursor.fetchone()
        if admin_info:
            admin, contact = admin_info
        st.markdown(f"**Department Administrator**: {admin}")
        st.markdown(f"**Contact Information**: {contact}")

    # ---------------------- Purchase Records (Hidden for Guests) ----------------------
    if role != "guest":
        st.subheader("Purchase Records")
        if purchase_records:
            st.table([
                {"Purchase Order Number": r[0], "Purchase Amount": f"￥{r[1]:.2f}", "Purchasing Department": r[2]}
                for r in purchase_records
            ])
        else:
            st.info("No purchase records available.")

    # ---------------------- Operation Buttons (Only for Department Administrators) ----------------------
    if (role == "dep-admin" and check_department_admin(e_id, asset["d_ID"])) or role == "super-admin":
        if st.button("Edit Asset Status", key="edit_status_from_detail"):
            st.session_state["edit_target_id"] = asset["ID"]
            st.session_state["selected_page"] = "Edit Asset Status"
            st.rerun()

    # ---------------------- Back Button ----------------------
    if st.button("Back to Query Page"):
        st.session_state["selected_page"] = "Asset Query"
        st.session_state.pop("selected_asset_id", None)
        st.rerun()
    