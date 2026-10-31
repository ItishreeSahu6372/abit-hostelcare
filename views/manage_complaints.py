import streamlit as st

import database as db
import styles

user = st.session_state.user
is_admin = user["role"] == "admin"
scope = st.session_state.get("scope", [])
no_warden = db.hostels_without_warden()

styles.page_header("Complaints", "View, filter and export." if is_admin else "Update status, add remarks and export the data.",
                   "Administrator" if is_admin else "Warden")

f1, f2, f3 = st.columns(3)
status = f1.selectbox("Status", ["All"] + db.STATUSES)
category = f2.selectbox("Category", ["All"] + db.CATEGORIES)
search = f3.text_input("Search", placeholder="Student, room, title or hostel")

df = db.get_complaints(hostels=scope, status=status, category=category, search=search)
st.caption(f"Showing {len(df)} complaint(s)")

if df.empty:
    st.info("No complaints match your filters.")
    st.stop()

st.dataframe(df[["id", "hostel", "room", "student", "title", "category", "priority", "status", "created_at"]], hide_index=True)
st.download_button("Download as CSV", df.to_csv(index=False).encode("utf-8"), "complaints.csv", "text/csv")

st.divider()
st.subheader("Complaint details" if is_admin else "Update a complaint")

options = {int(r["id"]): f"#{r['id']} · {r['title']} ({r['hostel']}, {r['room']})" for _, r in df.iterrows()}
selected_id = st.selectbox("Select complaint", list(options.keys()), format_func=lambda i: options[i])
current = df[df["id"] == selected_id].iloc[0]
st.markdown(styles.complaint_card(current, show_student=True, unassigned=current["hostel"] in no_warden), unsafe_allow_html=True)

if is_admin:
    st.caption("Only the assigned warden can change a complaint's status.")
    st.stop()

with st.form("update_form"):
    u1, u2 = st.columns([1, 2])
    new_status = u1.selectbox("New status", db.STATUSES, index=db.STATUSES.index(current["status"]))
    remarks = u2.text_input("Remarks for student", value=current["remarks"] or "")
    saved = st.form_submit_button("Save changes", type="primary")

if saved:
    db.update_complaint(int(selected_id), new_status, remarks.strip())
    st.toast("Complaint updated", icon=":material/check_circle:")
    st.rerun()

with st.expander("Danger zone"):
    confirm = st.checkbox("I want to delete this complaint permanently")
    if st.button("Delete complaint") and confirm:
        db.delete_complaint(int(selected_id))
        st.rerun()
