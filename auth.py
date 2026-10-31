"""Login, sign up, admin/warden account creation, password hashing, first-run setup."""
import hashlib
import hmac
import os
import re

import streamlit as st

import config
import database as db

STUDENT_EMAIL_PATTERN = re.compile(r"^\d{2}[a-z]{2,6}\d{1,4}@" + re.escape(config.COLLEGE_DOMAIN) + "$")
GENERIC_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    salt, digest = stored.split("$")
    return hmac.compare_digest(hash_password(password, salt).split("$")[1], digest)


def is_college_email(email):
    return bool(STUDENT_EMAIL_PATTERN.match(email.strip().lower()))


def _secret(name, default):
    try:
        return str(st.secrets[name])
    except Exception:
        return default


def admin_password():
# Optional: password of the demo warden account.
    return _secret("ADMIN_PASSWORD", "abitadmin1234")


def demo_warden_password():
    return _secret("WARDEN_PASSWORD", "warden123")


def authorized_warden_emails():
    emails = {e.strip().lower() for e in config.AUTHORIZED_WARDEN_EMAILS}
    try:
        extra = st.secrets["AUTHORIZED_WARDEN_EMAILS"]
    except Exception:
        extra = []
    if isinstance(extra, str):
        extra = extra.split(",")
    emails |= {str(e).strip().lower() for e in extra if str(e).strip()}
    return emails


def authenticate(username, password):
    user = db.get_user(username)
    if user and user["active"] and verify_password(password, user["password_hash"]):
        info = {k: user[k] for k in ("id", "name", "username", "role", "hostel")}
        if user["role"] == "warden":
            info["hostels"] = db.get_warden_hostels(user["id"])
        elif user["role"] == "admin":
            info["hostels"] = list(config.HOSTELS)
        else:
            info["hostels"] = [user["hostel"]] if user["hostel"] else []
        return info
    return None


def register_student(name, email, hostel, password, confirm):
    name, email = name.strip(), email.strip().lower()
    if not name or not email or not hostel or not password:
        return False, "Please fill all the fields."
    if not is_college_email(email):
        return False, f"Only {config.COLLEGE_SHORT} college emails are allowed (example: {config.EMAIL_EXAMPLE})."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if password != confirm:
        return False, "Passwords do not match."
    if not db.create_user(name, email, hash_password(password), "student", hostel):
        return False, "An account with this email already exists."
    return True, "Account created. You can now sign in with your college email."


def _create_warden(name, email, hostels, password):
    user_id = db.create_user(name, email, hash_password(password), "warden")
    if not user_id:
        return False
    db.set_warden_hostels(user_id, hostels)
    return True


def register_warden(name, email, hostels, password, confirm):
    """Warden self sign-up: the email must be authorised first."""
    name, email = name.strip(), email.strip().lower()
    if not name or not email or not hostels or not password:
        return False, "Please fill all the fields and choose at least one hostel."
    if not GENERIC_EMAIL_PATTERN.match(email):
        return False, "Please enter a valid email address."
    if email not in authorized_warden_emails():
        return False, "This email is not authorised for warden access. Please contact the college administration."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if password != confirm:
        return False, "Passwords do not match."
    if not _create_warden(name, email, hostels, password):
        return False, "An account with this email already exists."
    return True, "Warden account created. You can now sign in."


def create_warden_account(name, email, hostels, password):
    """Used by the administrator."""
    name, email = name.strip(), email.strip().lower()
    if not name or not email or not password:
        return False, "Please fill name, email and a temporary password."
    if not GENERIC_EMAIL_PATTERN.match(email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not _create_warden(name, email, hostels, password):
        return False, "An account with this email already exists."
    return True, f"Warden account created for {email}."


@st.cache_resource
def bootstrap():
    """Runs once per server start: tables, admin account, kept legacy students, demo data."""
    db.init_db()
    admin = db.get_user(config.ADMIN_EMAIL)
    if admin is None:
        db.create_user("Administrator", config.ADMIN_EMAIL, hash_password(admin_password()), "admin")
    else:
        db.set_password(admin["id"], hash_password(admin_password()))
    db.migrate_legacy()
    if config.SEED_DEMO_DATA and db.count_users("warden") == 0 and db.count_complaints() == 0:
        import demo_data

        demo_data.seed()
    return True
