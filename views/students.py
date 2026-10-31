import streamlit as st

import database as db
import styles

scope = st.session_state.get("scope", [])
styles.page_header("Students", "Students registered in the selected hostel(s).", "Directory")

df = db.get_students(hostels=scope)
if df.empty:
    st.info("No students registered yet.")
else:
    st.metric("Total students", len(df))
    table = df.rename(columns={"name": "Name", "email": "Email", "hostel": "Hostel", "created_at": "Joined", "complaints": "Complaints"})[
        ["Name", "Email", "Hostel", "Complaints", "Joined"]
    ]
    st.dataframe(table, hide_index=True)
