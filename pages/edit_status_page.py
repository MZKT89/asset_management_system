import streamlit as st
from utils.data_utils import (
    get_department_items,
    get_all_department_items,
    get_item_details,
    update_item_status,
    check_department_admin
)

def show():
    st.title("Edit Asset Status")

    # Check if the user is logged in
    if "user" not in st.session_state or st.session_state.user is None:
        st.error("Please log in first")
        return

    if "edit_success" in st.session_state:
        st.success(st.session_state["edit_success"])
        st.session_state.pop("edit_success", None)

    user = st.session_state.user
    role = user.get("role", "guest")
    d_id = user.get("d_id", None)

    # Get the list of assets in the user's department
    items = (get_department_items(d_id) if role == "dep-admin" else get_all_department_items())

    if not items:
        st.warning("There are no editable assets in the current department")
        return

    # Get the passed asset ID
    edit_id = st.session_state.get("edit_target_id", None)

    # Build asset selection options
    item_options = {f"{item['ID']} - {item['Item_Name']}": item['ID'] for item in items}
    option_keys = list(item_options.keys())

    # Select the corresponding option based on the passed ID (if exists)
    default_key = None
    if edit_id:
        for label, val in item_options.items():
            if val == edit_id:
                default_key = label
                break

    selected_item_key = st.selectbox(
        "Select an asset",
        options=option_keys,
        index=option_keys.index(default_key) if default_key else 0,
        format_func=lambda x: x
    )

    if selected_item_key:
        selected_item_id = item_options[selected_item_key]
        item_details = get_item_details(selected_item_id)

        if item_details:
            # Check if the user is a department administrator
            is_admin = check_department_admin(user["e_id"], item_details["d_ID"])

            # Display asset details
            with st.form("edit_status_form"):
                st.text_input("Asset ID", value=item_details["ID"], disabled=True)
                st.text_input("Asset Name", value=item_details["Item_Name"], disabled=True)
                st.text_input("Affiliated Department", value=item_details["Department_Name"], disabled=True)
                st.text_input("Storage Location", value=item_details["Placement_Location"], disabled=True)
                st.number_input("Current Value", value=float(item_details["Current_Value"]), disabled=True)

                # Status selection
                current_status = item_details["Status"]
                new_status = st.selectbox(
                    "Status",
                    options=[(1, "In use"), (0, "Scrapped")],
                    format_func=lambda x: x[1],
                    index=0 if current_status == 1 else 1,
                    disabled=not is_admin
                )

                submitted = st.form_submit_button("Submit Changes")

                if submitted:
                    if not is_admin:
                        st.error("You do not have permission to modify the asset status")
                    elif new_status[0] == current_status:
                        st.warning("The status has not changed")
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
            st.error("Unable to get asset details")

    if st.button("Back to Query Page"):
        st.session_state["selected_page"] = "Asset Query"
        st.session_state.pop("edit_target_id", None)
        st.rerun()

if __name__ == "__main__":
    show()
    