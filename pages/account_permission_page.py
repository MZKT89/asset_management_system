import streamlit as st
from utils.data_utils import get_all_users, update_user_role, add_new_user
import time

def show():
    st.title("Account Permission Settings")
    st.sidebar.title("Select an Operation")
    selected_operation = st.sidebar.radio("Select an operation", ["View User Information", "Edit User Role", "Add New User"])

    users = get_all_users()

    if users:
        if selected_operation == "View User Information":
            # Pagination settings
            items_per_page = 10
            num_pages = len(users) // items_per_page + (1 if len(users) % items_per_page != 0 else 0)
            page_options = [f"Page {i + 1}" for i in range(num_pages)]
            selected_page = st.selectbox("Select a page number", page_options)
            current_page = page_options.index(selected_page)

            start_index = current_page * items_per_page
            end_index = start_index + items_per_page
            current_users = users[start_index:end_index]

            converted_users = []
            for user in current_users:
                user = list(user)
                user[3] = convert_role(user[3])
                converted_users.append(user)
            # Display the user table
            st.write("All user information:")
            # e_ID, Name, d_ID, Position
            headers = ["ID", "Name", "Department ID", "Position"]
            st.table([dict(zip(headers, user)) for user in converted_users])

        elif selected_operation == "Edit User Role":
            # Edit role function
            st.write("Edit user role:")
            user_id = st.number_input("Please enter the user ID to edit", min_value=1, step=1, value=None)
            new_role = st.selectbox("Please choose a new position for the employee", ["non admin", "department admin", "super admin"],
                                    key="update_position_select")
            # Convert the role to the corresponding number
            new_role_num = convert_role(new_role)

            contact = None
            if new_role_num == 1:
                contact = st.text_input("Please enter the contact information")
                if contact and not contact.isdigit():
                    st.error("Contact information must be a number.")

            if st.button("Update Role"):
                if user_id == 1:
                    st.error("The original super admin cannot be modified.")

                elif user_id and new_role_num is not None:
                    if new_role_num == 1 and not contact:
                        st.error("Please enter the contact information")
                    elif new_role_num == 1 and len(contact) != 11:  # 检查电话号码位数是否为 11 位
                        st.error("Please enter a valid 11 - digit phone number.")
                    else:
                        if update_user_role(user_id, new_role_num, contact):
                            st.success("Role updated successfully!")
                            # Implement countdown
                            countdown_placeholder = st.empty()
                            for remaining in range(2, 0, -1):
                                countdown_placeholder.text(f'The page will refresh in {remaining} seconds...')
                                time.sleep(1)
                            countdown_placeholder.empty()
                            st.rerun()
                        else:
                            st.error("Role update failed. Please check if the user ID is correct.")
                else:
                    st.error("Please enter a valid user ID and select a role.")

        elif selected_operation == "Add New User":
            # Add new user function
            st.write("Add a new user:")
            E_name = st.text_input("Please enter the employee's name")
            password = st.text_input("Please enter the password", type="password")
            department_id = st.number_input("Please enter the department ID", min_value=1, step=1, value=None)
            position = st.selectbox("Please choose a new position for the employee", ["non admin", "department admin", "super admin"], key="add_user_position_select")
            position_num = convert_role(position)

            new_contact = None
            if position_num == 1:
                new_contact = st.text_input("Please enter the contact information for the new user")
                if new_contact and not new_contact.isdigit():
                    st.error("Contact information must be a number.")
            if st.button("Add User"):
                if E_name and password and department_id and position_num is not None:
                    if position_num == 1 and not new_contact:
                        st.error("Please enter the contact information for the new user")
                    elif position_num == 1 and len(new_contact) != 11:  # 检查电话号码位数是否为 11 位
                        st.error("Please enter a valid 11 - digit phone number.")
                    else:
                        if add_new_user(E_name, password, department_id, position_num, new_contact):
                            st.success("User added successfully!")
                            countdown_placeholder = st.empty()
                            for remaining in range(2, 0, -1):
                                countdown_placeholder.text(f'The page will refresh in {remaining} seconds...')
                                time.sleep(1)
                            countdown_placeholder.empty()
                            st.rerun()
                        else:
                            st.error("Failed to add the user. Please check the input information.")
                else:
                    st.error("Please enter the employee's name, password, department ID, and select a role completely.")

def convert_role(role):
    role_mapping = {
        "non admin": 0,
        "department admin": 1,
        "super admin": 2
    }
    inverse_mapping = {v: k for k, v in role_mapping.items()}

    if isinstance(role, str):
        if role in role_mapping:
            return role_mapping[role]
        else:
            st.error("Invalid role name.")
            return None
    elif isinstance(role, int):
        if role in inverse_mapping:
            return inverse_mapping[role]
        else:
            st.error("Invalid role number.")
            return None
    else:
        st.error("The input type must be a string or an integer.")
        return None
    