import streamlit as st
from datetime import datetime
from utils.data_utils import (
    get_department_list,
    add_new_item,
    validate_item_data
)

def add_asset_page():
    st.title("Add New Asset")

    # Display a message indicating whether the asset was added successfully
    if "asset_add_success" in st.session_state:
        st.success(st.session_state["asset_add_success"])
        del st.session_state["asset_add_success"]

    # Get the department list
    departments = get_department_list()
    if not departments:
        st.error("Unable to get the department list")
        return

    # Initialize default values for form fields (automatically initialize all except the 'Department' option on first visit and after submission)
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

    # Form
    with st.form("add_asset_form"):
        # Asset ID (automatically generated)
        item_id = st.text_input("Asset ID", value="Automatically generated", disabled=True)

        # Asset name
        item_name = st.text_input("Asset Name*", key="item_name")

        # Affiliated department
        department = st.selectbox(
            "Affiliated Department*",
            options=list(dict.fromkeys(departments)),  # Remove duplicates
            format_func=lambda x: x[1]
        )

        col1, col2 = st.columns(2)
        with col1:
            # Purchase amount
            asset_cost = st.number_input(
                "Purchase Amount*",
                min_value=0.01,
                format="%.2f",
                key="asset_cost"
            )

        with col2:
            # Purchase year
            current_year = datetime.now().year
            purchase_year = st.number_input(
                "Purchase Year*",
                min_value=2005,
                max_value=2025,
                key="purchase_year"
            )

        # Storage location
        placement_location = st.text_input("Storage Location*", key="placement_location")

        col3, col4 = st.columns(2)
        with col3:
            # Service life
            usable_life = st.number_input(
                "Service Life (Years)",
                min_value=1,
                key="usable_life"
            )

        # Submit button
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Validate required fields
            if not item_name:
                st.error("Please enter the asset name")
                return

            if not placement_location:
                st.error("Please enter the storage location")
                return

            # Prepare data for submission
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

            # Use the validation function to validate the data
            is_valid, error_msg = validate_item_data(asset_data)

            if not is_valid:
                st.error(f"Data validation failed: {error_msg}")
                return

            # Add the asset
            new_item_id = add_new_item(asset_data)

            if new_item_id:
                st.session_state["asset_add_success"] = f"Asset added successfully! Asset ID: {new_item_id}"
                # Clear form fields after successful submission
                for key in ["item_name", "placement_location", "asset_cost", "purchase_year", "usable_life"]:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("Failed to add. Please try again later")

    # Back button
    if st.button("Back to Query Page"):
        st.session_state["selected_page"] = "Asset Query"
        st.rerun()

def show():
    add_asset_page()

if __name__ == "__main__":
    show()
    