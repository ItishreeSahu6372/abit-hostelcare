import streamlit as st

import auth
import config
import database as db
import styles

styles.hide_sidebar()

left, right = st.columns([1.1, 1], gap="large")

with left:
    st.markdown(styles.brand_panel(), unsafe_allow_html=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="login-title">Welcome</div><div class="login-sub">Sign in or create an account to continue.</div>', unsafe_allow_html=True)
        tab_login, tab_student = st.tabs(["Sign in", "Student sign up"])

        with tab_login:
            with st.form("login_form"):
                role = st.radio("Sign in as", ["Student", "Warden", "Admin"], horizontal=True)
                username = st.text_input("Email", placeholder=config.EMAIL_EXAMPLE)
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", type="primary")
            if submitted:
                login_id = username.strip().lower()
                existing = db.get_user(login_id)
                if role == "Student" and not auth.is_college_email(login_id):
                    st.error(f"Students must sign in with their {config.COLLEGE_SHORT} college email (example: {config.EMAIL_EXAMPLE}).")
                elif existing and not existing["active"]:
                    st.error("This account has been deactivated. Please contact the administrator.")
                else:
                    user = auth.authenticate(login_id, password)
                    if not user:
                        st.error("Wrong email or password.")
                    elif user["role"] != role.lower():
                        st.error(f"This is not a {role.lower()} account.")
                    else:
                        st.session_state.user = user
                        st.rerun()
            if config.SEED_DEMO_DATA:
                with st.expander("Demo accounts"):
                    st.write(f"Student: `{config.DEMO_STUDENT_EMAIL}` / `student123`")
                    st.write(f"Warden: `{config.DEMO_WARDEN_EMAIL}` / `warden123`")

        with tab_student:
            with st.form("student_signup", clear_on_submit=True):
                name = st.text_input("Full name")
                email = st.text_input("College email", placeholder=config.EMAIL_EXAMPLE)
                hostel = st.selectbox("Hostel", config.HOSTELS)
                pw = st.text_input("Create password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                created = st.form_submit_button("Create student account", type="primary")
            if created:
                ok, msg = auth.register_student(name, email, hostel, pw, confirm)
                (st.success if ok else st.error)(msg)

