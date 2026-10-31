"""HostelCare entry point: login gate and role-based navigation."""
import streamlit as st

import auth
import config
import database as db
import styles

st.set_page_config(page_title=f"{config.COLLEGE_SHORT} HostelCare", page_icon=":material/apartment:", layout="wide")
auth.bootstrap()
styles.inject_css()

user = st.session_state.get("user")

# Keep the session honest: account may have been deactivated or re-assigned by the admin.
if user:
    fresh = db.get_user(user["username"])
    if not fresh or not fresh["active"]:
        st.session_state.clear()
        st.rerun()
    if user["role"] == "warden":
        user["hostels"] = db.get_warden_hostels(user["id"])
        st.session_state.user = user

if not user:
    page = st.navigation([st.Page("views/login.py", title="Sign in")], position="hidden")
else:
    role = user["role"]
    if role == "student":
        pages = [
            st.Page("views/student_home.py", title="Dashboard", icon=":material/dashboard:", default=True),
            st.Page("views/raise_complaint.py", title="Submit Complaint", icon=":material/add_circle:"),
            st.Page("views/my_complaints.py", title="My Complaints", icon=":material/assignment:"),
        ]
    else:
        pages = [
            st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
            st.Page("views/manage_complaints.py", title="Complaints", icon=":material/assignment:"),
            st.Page("views/analytics_page.py", title="Analytics", icon=":material/analytics:"),
        ]
        pages.append(st.Page("views/students.py", title="Students", icon=":material/groups:"))
        if role == "admin":
            pages.append(st.Page("views/wardens.py", title="Wardens", icon=":material/badge:"))
            pages.append(st.Page("views/notifications.py", title="Notifications", icon=":material/notifications:"))
    page = st.navigation(pages)

    with st.sidebar:
        st.markdown(styles.user_card(user), unsafe_allow_html=True)

        if role in ("warden", "admin"):
            hostels = user["hostels"]
            if not hostels:
                st.caption("No hostel is assigned to you yet. Please contact the administrator.")
                st.session_state.scope = []
            else:
                all_label = "All hostels" if role == "admin" else "All my hostels"
                options = ([all_label] if len(hostels) > 1 else []) + hostels
                choice = st.selectbox("Viewing hostel", options, key="hostel_choice")
                st.session_state.scope = hostels if choice == all_label else [choice]

        if st.button("Log out", icon=":material/logout:", type="primary"):
            st.session_state.clear()
            st.rerun()

page.run()
