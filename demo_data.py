"""Sample accounts and complaints so the app never opens empty (demo only)."""
import random
from datetime import datetime, timedelta

import auth
import config
import database as db

STUDENTS = [
    ("Aarav Mohanty", "23cse001", "A-101"),
    ("Ishita Sahoo", "23cse014", "B-203"),
    ("Rohan Behera", "23ece022", "C-110"),
    ("Sneha Patra", "22eee009", "A-307"),
    ("Debasish Nayak", "23cse031", "B-118"),
    ("Priya Mishra", "24mec005", "C-204"),
    ("Subham Das", "23cse045", "A-215"),
    ("Anjali Rout", "22cse018", "B-309"),
    ("Manas Swain", "23ece037", "C-102"),
    ("Lopamudra Panda", "24cse011", "A-122"),
    ("Kunal Jena", "22ece026", "B-221"),
    ("Smruti Ranjan", "23eee016", "C-318"),
]

TEMPLATES = {
    "Water": [("Water leakage in bathroom", "Tap keeps leaking and the floor stays wet."),
              ("No water supply", "No water coming in the wing since morning."),
              ("Low water pressure", "Very low pressure on the upper floors.")],
    "Electricity": [("Fan not working", "Ceiling fan makes noise and stops."),
                    ("Power socket sparking", "Socket near the bed sparks when used."),
                    ("Tube light fused", "Light in the corridor is not working.")],
    "Cleaning": [("Corridor not cleaned", "Corridor has not been cleaned for days."),
                 ("Dustbin overflowing", "Garbage is not being collected on time.")],
    "Food": [("Mess food quality", "Dinner was cold and undercooked."),
             ("Unhygienic mess utensils", "Plates were not washed properly.")],
    "Internet": [("Wi-Fi very slow", "Speed drops badly in the evening."),
                 ("Wi-Fi not connecting", "Router in the wing is down.")],
    "Furniture": [("Broken study table", "Table leg is broken."),
                  ("Cupboard lock broken", "Cupboard door will not lock.")],
    "Other": [("Main gate light off", "Gate area is dark at night."),
              ("Window glass broken", "Glass cracked and is unsafe.")],
}
CAT_WEIGHTS = {"Water": 28, "Electricity": 20, "Cleaning": 14, "Food": 17, "Internet": 12, "Furniture": 5, "Other": 4}
FIX_HOURS = {"Water": 28, "Electricity": 52, "Cleaning": 18, "Food": 34, "Internet": 70, "Furniture": 96, "Other": 48}
HOUR_WEIGHTS = [1, 1, 1, 1, 1, 2, 4, 8, 9, 6, 4, 4, 4, 3, 3, 4, 5, 6, 8, 10, 10, 9, 6, 3]
DAY_WEIGHTS = [10, 7, 6, 6, 7, 6, 9]  # Mon..Sun


def seed():
    hostels = config.HOSTELS
    warden_id = db.create_user("Demo Warden", config.DEMO_WARDEN_EMAIL, auth.hash_password(auth.demo_warden_password()), "warden")
    db.set_warden_hostels(warden_id, hostels[:2])

    students = []
    for i, (name, roll, room) in enumerate(STUDENTS):
        email = f"{roll}@{config.COLLEGE_DOMAIN}"
        if i == 0:
            email = config.DEMO_STUDENT_EMAIL
        hostel = hostels[i % len(hostels)]
        uid = db.create_user(name, email, auth.hash_password("student123"), "student", hostel)
        if uid is None:  # account already exists (kept from an older version)
            uid = db.get_user(email)["id"]
            db.set_student_hostel(uid, hostel)
        students.append({"id": uid, "hostel": hostel, "room": room})

    rng = random.Random(7)
    now = datetime.now().replace(microsecond=0)
    # a few "problem rooms" per hostel so the repeat-room insight is meaningful
    hotspot = {h: f"{rng.choice('ABC')}-{rng.randint(101, 320)}" for h in hostels}
    rows = []
    for _ in range(85):
        days_ago = 80 * rng.random() ** 1.25
        created = now - timedelta(days=days_ago)
        for _try in range(10):  # pick a weekday using the weights
            if rng.random() * max(DAY_WEIGHTS) < DAY_WEIGHTS[created.weekday()]:
                break
            created -= timedelta(days=1)
        hour = rng.choices(range(24), weights=HOUR_WEIGHTS)[0]
        created = created.replace(hour=hour, minute=rng.randint(0, 59), second=0)
        if created > now:
            created -= timedelta(days=1)

        category = rng.choices(list(CAT_WEIGHTS), weights=list(CAT_WEIGHTS.values()))[0]
        title, desc = rng.choice(TEMPLATES[category])
        high = 35 if category in ("Water", "Electricity") else 15
        priority = rng.choices(["Low", "Medium", "High"], weights=[30, 70 - high, high])[0]
        student = dict(rng.choice(students))
        student["room"] = hotspot[student["hostel"]] if rng.random() < 0.22 else f"{rng.choice('ABC')}-{rng.randint(101, 320)}"

        fix_hours = 2 + rng.expovariate(1 / FIX_HOURS[category])
        age_hours = (now - created).total_seconds() / 3600
        if age_hours > fix_hours and rng.random() < 0.88:
            status, remarks = "Solved", "Resolved by the maintenance team."
            resolved = created + timedelta(hours=fix_hours)
            updated = resolved
        elif age_hours > 6 and rng.random() < 0.5:
            status, remarks, resolved = "In Progress", "Technician has been assigned.", None
            updated = created + timedelta(hours=min(age_hours, 5))
        else:
            status, remarks, resolved = "Pending", "", None
            updated = created
        fmt = db.TS_FORMAT
        rows.append((created, student, title, category, desc, priority, status, remarks,
                     created.strftime(fmt), updated.strftime(fmt), resolved.strftime(fmt) if resolved else None))

    rows.sort(key=lambda r: r[0])
    for _created, s, title, category, desc, priority, status, remarks, c_at, u_at, r_at in rows:
        db.insert_seed_complaint(s["id"], s["hostel"], s["room"], title, category, desc, priority,
                                 status, remarks, c_at, u_at, r_at)
