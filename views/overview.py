import pandas as pd
import streamlit as st

import database as db
import styles

user = st.session_state.user
role = user["role"]
scope = st.session_state.get("scope", [])
label = scope[0] if len(scope) == 1 else f"{len(scope)} hostels"

styles.page_header("Overview", f"Complaints for {label}" if scope else "No hostel assigned yet",
                   "Administrator" if role == "admin" else "Warden")

df = db.get_complaints(hostels=scope)
no_warden = db.hostels_without_warden()

if role == "admin" and no_warden:
    st.warning("No active warden is assigned to: " + ", ".join(no_warden) + ". Complaints there are saved but flagged as unassigned.")

if df.empty:
    st.info("No complaints yet.")
    st.stop()

total = len(df)
solved = styles.count_status(df, "Solved")
styles.metric_row(
    [
        ("Total", total, "#4F46E5"),
        ("Pending", styles.count_status(df, "Pending"), "#F59E0B"),
        ("In progress", styles.count_status(df, "In Progress"), "#3B82F6"),
        ("Solved", solved, "#10B981"),
    ]
)
st.write("")
st.progress(solved / total, text=f"Resolution rate: {solved / total * 100:.0f}%")

if role == "admin":
    st.subheader("Buildings and wardens")
    wardens = db.get_hostel_wardens()
    rows = []
    for hostel in scope:
        h = df[df["hostel"] == hostel]
        rows.append({
            "Hostel": hostel,
            "Active warden(s)": ", ".join(wardens.get(hostel, [])) or "Unassigned",
            "Total": len(h),
            "Open": int((h["status"] != "Solved").sum()),
            "Solved": int((h["status"] == "Solved").sum()),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True)

st.subheader("Needs attention")
urgent = df[(df["priority"] == "High") & (df["status"] != "Solved")]
if urgent.empty:
    st.success("No high-priority complaint is waiting.")
else:
    for _, c in urgent.head(5).iterrows():
        st.markdown(styles.complaint_card(c, show_student=True, unassigned=c["hostel"] in no_warden), unsafe_allow_html=True)
