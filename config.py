"""College-level settings. Edit this file for your college."""

COLLEGE_NAME = "Ajay Binay Institute of Technology"
COLLEGE_SHORT = "ABIT"
COLLEGE_DOMAIN = "abit.edu.in"
EMAIL_EXAMPLE = "23cse051@abit.edu.in"

# Replace these with the real hostel / building names of ABIT.
HOSTELS = [
    "Badambadi Boys Hostel",
    "Badambadi Girls Hostel",
    "CDA Boys Hostel",
    "CDA Girls Hostel",
]

# Only these emails can register as a warden.
# More can be added from Streamlit secrets (AUTHORIZED_WARDEN_EMAILS).
AUTHORIZED_WARDEN_EMAILS = [
    "warden@abit.edu.in",
]

# The administrator account (created automatically on first start).
# Set ADMIN_PASSWORD in Streamlit secrets to change the default password (admin123).
ADMIN_EMAIL = "itishree2301206051@gmail.com"

# Demo accounts and sample complaints (set to False for the real launch).
SEED_DEMO_DATA = True
DEMO_WARDEN_EMAIL = "warden@abit.edu.in"
DEMO_STUDENT_EMAIL = "23cse001@abit.edu.in"
