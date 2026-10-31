import streamlit as st

import database as db
import styles

user = st.session_state.user
df = db.get_complaints(user_id=user["id"])

styles.page_header(f"Welcome, {user['name'].split()[0]}", f"{user['hostel'] or 'Select your hostel on the Submit Complaint page'}", "Student dashboard")

styles.metric_row(
    [
        ("My complaints", len(df), "#4F46E5"),
        ("Pending", styles.count_status(df, "Pending"), "#F59E0B"),
        ("In progress", styles.count_status(df, "In Progress"), "#3B82F6"),
        ("Solved", styles.count_status(df, "Solved"), "#10B981"),
    ]
)

st.write("")
st.subheader("Recent activity")
if df.empty:
    st.info("You have not submitted any complaint yet. Open Submit Complaint from the menu.")
else:
    for _, c in df.head(3).iterrows():
        st.markdown(styles.complaint_card(c, progress=True), unsafe_allow_html=True)
    st.caption("See every complaint on the My Complaints page.")
