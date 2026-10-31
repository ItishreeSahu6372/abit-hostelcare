"""Reset the admin password directly in the database.

Run this in the project folder (the one that contains app.py):
    python reset_admin.py
"""
import config
import database as db
import auth

db.init_db()
print("Database file in use:", db.DB_PATH)

new_password = input("Type a new admin password (at least 6 characters): ").strip()
if len(new_password) < 6:
    raise SystemExit("Too short. Run the script again with 6 or more characters.")

admin = db.get_user(config.ADMIN_EMAIL)
if admin is None:
    db.create_user("Administrator", config.ADMIN_EMAIL, auth.hash_password(new_password), "admin")
    print("Admin account was missing, so it has been created.")
else:
    db.set_password(admin["id"], auth.hash_password(new_password))
    db.set_user_active(admin["id"], True)
    print("Admin password updated.")

result = auth.authenticate(config.ADMIN_EMAIL, new_password)
print("Login test:", "OK" if result and result["role"] == "admin" else "FAILED")
print()
print("Now sign in with:")
print("  Sign in as : Admin")
print("  Email      :", config.ADMIN_EMAIL)
print("  Password   : (the one you just typed)")
