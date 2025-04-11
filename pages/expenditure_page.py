import streamlit as st
import datetime
import pandas as pd
from utils.data_utils import (
    get_department_expenditure,
    get_expenditure_trend,
    get_department_list,
)


def show():
    st.title("Annual Dept Procurement Expenditure 📈")

    # Permission check: Guests have no access to this page
    if st.session_state.user["role"] == "guest":
        st.error("Guests do not have permission to access this page.")
        return

    user_role = st.session_state.user["role"]

    # Handle department selection based on different roles
    if user_role == "super-admin":
        dept_options = get_department_list()  # Returns [(d_ID, Department_Name), ...]
        if not dept_options:
            st.error("Unable to get department data")
            return
        # Create a dropdown selection box: Display department ID and name
        dept_names = [f"{dept[0]} - {dept[1]}" for dept in dept_options]
        selected_index = st.selectbox(
            "Select a department", range(len(dept_options)), format_func=lambda i: dept_names[i]
        )
        selected_department_id = dept_options[selected_index][0]
    else:
        # Non-super administrators default to the current user's department and display detailed information (e.g., "2 - Marketing Department")
        selected_department_id = st.session_state.user["d_id"]
        department_list = get_department_list()
        department_name = None
        for dept in department_list:
            if int(selected_department_id) == int(dept[0]):
                department_name = dept[1]
                break
        if department_name:
            st.info(f"Current department: {selected_department_id} - {department_name}")
        else:
            st.info(f"Current department: {selected_department_id}")

    # Year selector: Default to the current year, allowing selection from 2005 to 2025
    current_year = datetime.datetime.now().year
    selected_year = st.number_input(
        "Select a year", min_value=2005, max_value=2025, value=current_year, step=1
    )

    # Call the backend function to get data
    expenditure_data = get_department_expenditure(selected_department_id, selected_year)
    trend_data = get_expenditure_trend(selected_department_id, selected_year)

    st.subheader("Total Expenditure Amount")
    # Use st.metric to display the total procurement expenditure and year-on-year percentage
    st.metric(
        label=f"Total procurement expenditure in {selected_year}",
        value=f"¥{expenditure_data['total_cost']}",
        delta=expenditure_data["comparison"],
    )

    st.subheader("Trend of Procurement Amount in the Past 5 Years")
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        df_trend.set_index("year", inplace=True)
        st.line_chart(df_trend["total_cost"])
    else:
        st.write("No data available")

    if st.button("Back to Query Page"):
        st.session_state["selected_page"] = "Asset Query"
        st.session_state.pop("edit_target_id", None)
        st.rerun()
    