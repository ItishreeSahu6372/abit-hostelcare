"""All database work (SQLite) lives here."""
import os
import sqlite3
from datetime import datetime

import pandas as pd

import config

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "abit_hostelcare.db")

CATEGORIES = ["Water", "Electricity", "Cleaning", "Food", "Internet", "Furniture", "Other"]
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Solved"]
TS_FORMAT = "%Y-%m-%d %H:%M:%S"


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now():
    return datetime.now().strftime(TS_FORMAT)


def _df(query, params=()):
    conn = _connect()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def init_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'warden', 'admin')),
            hostel TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS warden_hostels (
            user_id INTEGER NOT NULL,
            hostel TEXT NOT NULL,
            PRIMARY KEY (user_id, hostel),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hostel TEXT NOT NULL,
            room_no TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Pending',
            remarks TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


# ---------- Users ----------
def create_user(name, username, password_hash, role, hostel=""):
    """Returns the new user id, or None if the username already exists."""
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, username, password_hash, role, hostel, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, username, password_hash, role, hostel, _now()),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user(username):
    conn = _connect()
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def count_users(role=None):
    conn = _connect()
    if role:
        n = conn.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,)).fetchone()[0]
    else:
        n = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return n


def set_warden_hostels(user_id, hostels):
    conn = _connect()
    conn.execute("DELETE FROM warden_hostels WHERE user_id = ?", (user_id,))
    conn.executemany("INSERT INTO warden_hostels (user_id, hostel) VALUES (?, ?)", [(user_id, h) for h in hostels])
    conn.commit()
    conn.close()


def get_warden_hostels(user_id):
    conn = _connect()
    rows = conn.execute("SELECT hostel FROM warden_hostels WHERE user_id = ? ORDER BY hostel", (user_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_warden_emails(hostel):
    """[(name, email)] of every warden responsible for this hostel."""
    conn = _connect()
    rows = conn.execute(
        "SELECT u.name, u.username FROM users u JOIN warden_hostels w ON w.user_id = u.id "
        "WHERE w.hostel = ? AND u.active = 1 AND u.role = 'warden'",
        (hostel,),
    ).fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows]


def get_students(hostels=None):
    query = """
        SELECT u.id, u.name, u.username AS email, u.hostel, u.created_at, COUNT(c.id) AS complaints
        FROM users u LEFT JOIN complaints c ON c.user_id = u.id
        WHERE u.role = 'student'
    """
    params = []
    if hostels is not None:
        if not hostels:
            query += " AND 1 = 0"
        else:
            query += f" AND u.hostel IN ({','.join('?' * len(hostels))})"
            params += list(hostels)
    query += " GROUP BY u.id ORDER BY u.id DESC"
    return _df(query, params)


# ---------- Complaints ----------
def add_complaint(user_id, hostel, room_no, title, category, description, priority):
    conn = _connect()
    now = _now()
    cur = conn.execute(
        "INSERT INTO complaints (user_id, hostel, room_no, title, category, description, priority, status, remarks, created_at, updated_at, resolved_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', '', ?, ?, NULL)",
        (user_id, hostel, room_no, title, category, description, priority, now, now),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def insert_seed_complaint(user_id, hostel, room_no, title, category, description, priority,
                          status, remarks, created_at, updated_at, resolved_at):
    """Used only for demo data (lets us set past dates)."""
    conn = _connect()
    conn.execute(
        "INSERT INTO complaints (user_id, hostel, room_no, title, category, description, priority, status, remarks, created_at, updated_at, resolved_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, hostel, room_no, title, category, description, priority, status, remarks, created_at, updated_at, resolved_at),
    )
    conn.commit()
    conn.close()


def get_complaints(user_id=None, hostels=None, status=None, category=None, search=None):
    query = """
        SELECT c.id, c.user_id, c.hostel, c.room_no AS room, c.title, c.category, c.priority,
               c.status, c.description, c.remarks, c.created_at, c.updated_at, c.resolved_at,
               u.name AS student, u.username AS student_email
        FROM complaints c JOIN users u ON u.id = c.user_id
        WHERE 1 = 1
    """
    params = []
    if user_id:
        query += " AND c.user_id = ?"
        params.append(user_id)
    if hostels is not None:
        if not hostels:
            query += " AND 1 = 0"
        else:
            query += f" AND c.hostel IN ({','.join('?' * len(hostels))})"
            params += list(hostels)
    if status and status != "All":
        query += " AND c.status = ?"
        params.append(status)
    if category and category != "All":
        query += " AND c.category = ?"
        params.append(category)
    if search:
        query += " AND (u.name LIKE ? OR c.room_no LIKE ? OR c.title LIKE ? OR c.hostel LIKE ?)"
        params += [f"%{search}%"] * 4
    query += " ORDER BY c.id DESC"
    return _df(query, params)


def count_complaints():
    conn = _connect()
    n = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    conn.close()
    return n


def update_complaint(complaint_id, status, remarks):
    conn = _connect()
    now = _now()
    conn.execute(
        "UPDATE complaints SET status = ?, remarks = ?, updated_at = ?, "
        "resolved_at = CASE WHEN ? = 'Solved' THEN COALESCE(resolved_at, ?) ELSE NULL END "
        "WHERE id = ?",
        (status, remarks, now, status, now, complaint_id),
    )
    conn.commit()
    conn.close()


def delete_complaint(complaint_id):
    conn = _connect()
    conn.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()


# ---------- Admin / warden management ----------
LEGACY_PATH = os.path.join(os.path.dirname(__file__), "data", "hostelcare.db")


def set_user_active(user_id, active):
    conn = _connect()
    conn.execute("UPDATE users SET active = ? WHERE id = ?", (1 if active else 0, user_id))
    conn.commit()
    conn.close()


def set_password(user_id, password_hash):
    conn = _connect()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    conn.close()


def set_student_hostel(user_id, hostel):
    conn = _connect()
    conn.execute("UPDATE users SET hostel = ? WHERE id = ?", (hostel, user_id))
    conn.commit()
    conn.close()


def get_wardens():
    conn = _connect()
    conn.row_factory = sqlite3.Row
    users = conn.execute(
        "SELECT id, name, username, active, created_at FROM users WHERE role = 'warden' ORDER BY id DESC"
    ).fetchall()
    links = conn.execute("SELECT user_id, hostel FROM warden_hostels ORDER BY hostel").fetchall()
    conn.close()
    by_user = {}
    for link in links:
        by_user.setdefault(link["user_id"], []).append(link["hostel"])
    return [
        {"id": u["id"], "name": u["name"], "email": u["username"], "active": bool(u["active"]),
         "created_at": u["created_at"], "hostels": by_user.get(u["id"], [])}
        for u in users
    ]


def get_hostel_wardens():
    """{hostel: [warden names]} for ACTIVE wardens only."""
    conn = _connect()
    rows = conn.execute(
        "SELECT w.hostel, u.name FROM warden_hostels w JOIN users u ON u.id = w.user_id "
        "WHERE u.active = 1 AND u.role = 'warden'"
    ).fetchall()
    conn.close()
    result = {}
    for hostel, name in rows:
        result.setdefault(hostel, []).append(name)
    return result


def hostels_without_warden():
    assigned = get_hostel_wardens()
    return [h for h in config.HOSTELS if not assigned.get(h)]


def migrate_legacy():
    """Keeps student accounts from the older version (data/hostelcare.db). Safe to run repeatedly."""
    if not os.path.exists(LEGACY_PATH):
        return 0
    try:
        old = sqlite3.connect(LEGACY_PATH)
        rows = old.execute("SELECT name, username, password_hash FROM users WHERE role = 'student'").fetchall()
        old.close()
    except Exception:
        return 0
    moved = 0
    for name, username, password_hash in rows:
        if get_user(username) is None and create_user(name, username, password_hash, "student", ""):
            moved += 1
    return moved


def delete_warden(user_id):
    conn = _connect()
    conn.execute("DELETE FROM warden_hostels WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ? AND role = 'warden'", (user_id,))
    conn.commit()
    conn.close()