import streamlit as st

import database as db
import notify
import styles

user = st.session_state.user
scope = st.session_state.get("scope", [])
cfg = notify.smtp_settings()

styles.page_header("Email notifications", "A new complaint is emailed only to the warden assigned to that hostel.", "Settings")

if notify.is_configured(cfg):
    st.success(f"Email is configured. Messages are sent from {cfg['sender']}.")
else:
    st.warning("Email is not configured yet. Add SMTP_USER and SMTP_PASSWORD in the app secrets (see README).")

st.subheader("Who gets notified")
wardens = db.get_hostel_wardens()
for hostel in scope:
    emails = [e for _n, e in db.get_warden_emails(hostel)]
    st.write(f"**{hostel}**: " + (", ".join(emails) if emails else "No active warden assigned (complaints are flagged as unassigned)"))

st.subheader("Test")
if st.button("Send a test email to me"):
    ok, msg = notify.send_test(user["username"])
    (st.success if ok else st.error)(msg)
