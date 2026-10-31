import streamlit as st

import database as db
import styles

user = st.session_state.user

styles.page_header("My complaints", "Live status and remarks from your warden.", "Student")

status = st.selectbox("Filter by status", ["All"] + db.STATUSES)
df = db.get_complaints(user_id=user["id"], status=status)  # only this student's complaints

if df.empty:
    st.info("No complaints found.")
else:
    st.caption(f"{len(df)} complaint(s)")
    for _, c in df.iterrows():
        st.markdown(styles.complaint_card(c, progress=True), unsafe_allow_html=True)
