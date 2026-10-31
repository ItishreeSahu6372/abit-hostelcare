import streamlit as st

import config
import database as db
import notify
import styles

user = st.session_state.user

styles.page_header("Submit a complaint", "Your hostel warden is notified as soon as you submit.", "Student")

# Students kept from an older version have no hostel saved yet.
if not user["hostel"]:
    st.info("Please select your hostel once. It is saved to your profile.")
    with st.form("hostel_form"):
        chosen = st.selectbox("Your hostel", config.HOSTELS)
        saved = st.form_submit_button("Save hostel", type="primary")
    if saved:
        db.set_student_hostel(user["id"], chosen)
        user["hostel"], user["hostels"] = chosen, [chosen]
        st.session_state.user = user
        st.rerun()
    st.stop()

with st.container(border=True):
    with st.form("complaint_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        c1.text_input("Hostel", value=user["hostel"], disabled=True)
        room_no = c2.text_input("Room number", placeholder="e.g. A-204")
        title = st.text_input("Complaint title", placeholder="e.g. Water leakage in bathroom")
        c3, c4 = st.columns(2)
        category = c3.selectbox("Category", db.CATEGORIES)
        priority = c4.selectbox("Priority", db.PRIORITIES, index=1)
        description = st.text_area("Describe the problem", height=140)
        submitted = st.form_submit_button("Submit complaint", type="primary")

if submitted:
    if not room_no.strip() or not title.strip() or not description.strip():
        st.error("Please enter the room number, a title and a description.")
    else:
        # 1) Save first. The complaint is safe even if the email fails.
        new_id = db.add_complaint(user["id"], user["hostel"], room_no.strip(), title.strip(), category, description.strip(), priority)
        # 2) Then notify only the warden assigned to this hostel.
        assigned = user["hostel"] not in db.hostels_without_warden()
        queued = notify.notify_new_complaint(
            {"id": new_id, "title": title.strip(), "category": category, "priority": priority,
             "description": description.strip(), "hostel": user["hostel"], "room": room_no.strip(),
             "student": user["name"], "student_email": user["username"]}
        )
        if not assigned:
            st.warning(f"Complaint #{new_id} is saved. No warden is currently assigned to {user['hostel']}, so the administration has been flagged.")
        elif queued:
            st.success(f"Complaint #{new_id} submitted. The warden of {user['hostel']} is being notified by email.")
        else:
            st.success(f"Complaint #{new_id} submitted. It is now on the warden's dashboard.")
