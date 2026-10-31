import pandas as pd
import streamlit as st

import auth
import config
import database as db
import styles

styles.page_header("Wardens", "Create accounts, assign buildings and deactivate wardens.", "Administrator")

wardens = db.get_wardens()
no_warden = db.hostels_without_warden()
if no_warden:
    st.warning("Buildings without an active warden: " + ", ".join(no_warden))

st.subheader("All wardens")
if not wardens:
    st.info("No wardens yet. Add one below.")
else:
    st.dataframe(
        pd.DataFrame([{"Name": w["name"], "Email": w["email"], "Status": "Active" if w["active"] else "Inactive",
                       "Buildings": ", ".join(w["hostels"]) or "None"} for w in wardens]),
        hide_index=True,
    )

tab_add, tab_edit = st.tabs(["Add warden", "Edit or deactivate"])

with tab_add:
    with st.form("add_warden", clear_on_submit=True):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Temporary password", type="password")
        hostels = st.multiselect("Assign buildings", config.HOSTELS)
        created = st.form_submit_button("Create warden account", type="primary")
    if created:
        ok, msg = auth.create_warden_account(name, email, hostels, password)
        if ok:
            st.toast(msg, icon=":material/check_circle:")
            st.rerun()
        else:
            st.error(msg)

with tab_edit:
    if not wardens:
        st.info("Nothing to edit yet.")
    else:
        labels = {w["id"]: f"{w['name']} ({w['email']})" for w in wardens}
        wid = st.selectbox("Select warden", list(labels), format_func=lambda i: labels[i])
        w = next(x for x in wardens if x["id"] == wid)
        with st.form("edit_warden"):
            new_hostels = st.multiselect("Assigned buildings", config.HOSTELS, default=[h for h in w["hostels"] if h in config.HOSTELS])
            active = st.checkbox("Account is active", value=w["active"])
            new_pw = st.text_input("Reset password (leave empty to keep the current one)", type="password")
            saved = st.form_submit_button("Save changes", type="primary")
        if saved:
            if new_pw and len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                db.set_warden_hostels(w["id"], new_hostels)
                db.set_user_active(w["id"], active)
                if new_pw:
                    db.set_password(w["id"], auth.hash_password(new_pw))
                st.toast("Warden updated", icon=":material/check_circle:")
                st.rerun()


        with st.expander("Delete this warden permanently"):
            st.caption("This removes the account completely. Complaints are not affected. To only block login, use the Active checkbox instead.")
            confirm = st.checkbox("Yes, delete this warden", key=f"del_{w['id']}")
            if st.button("Delete warden") and confirm:
                db.delete_warden(w["id"])
                st.toast("Warden deleted", icon=":material/check_circle:")
                st.rerun()