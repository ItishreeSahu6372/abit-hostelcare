"""Premium look: CSS and small HTML helpers (no emojis)."""
from datetime import datetime
from html import escape

import streamlit as st

import config

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 2.2rem; max-width: 1180px;}
h2, h3 {font-weight: 700; letter-spacing: -0.01em; color: #0F172A;}

/* Page header */
.page-head {margin: 0 0 24px 0;}
.page-head .eyebrow {font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; color: #4F46E5; font-weight: 700;}
.page-head h1 {font-size: 1.85rem; font-weight: 700; margin: 4px 0 0 0; padding: 0; color: #0F172A; letter-spacing: -0.02em;}
.page-head p {color: #64748B; margin: 6px 0 0 0; font-size: .98rem;}

/* Buttons */
div.stButton button, div[data-testid="stFormSubmitButton"] button, div.stDownloadButton button {
    width: 100%; border-radius: 10px; font-weight: 600; padding: 0.55rem 1rem;
    border: 1px solid #E2E5EF; background: #fff; color: #0F172A; transition: all .15s ease;
}
button[kind^="primary"], button[data-testid^="stBaseButton-primary"] {
    background: linear-gradient(135deg, #4F46E5, #6D5DF6) !important; color: #fff !important; border: none !important;
    box-shadow: 0 6px 16px rgba(79,70,229,.28);
}
div.stButton button:hover, div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px); box-shadow: 0 6px 16px rgba(15,23,42,.10);
}

/* Inputs */
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"], textarea {border-radius: 10px !important;}
.stTabs [data-baseweb="tab"] {font-weight: 600;}

/* Sidebar */
section[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #ECEEF6;}

/* Metric cards */
.mcard {
    background: #fff; border: 1px solid #E8EAF2; border-radius: 14px; padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(15,23,42,.04); height: 100%;
}
.mcard .label {font-size: .7rem; color: #64748B; text-transform: uppercase; letter-spacing: .09em; font-weight: 600; display: flex; align-items: center; gap: 8px;}
.mcard .dot {width: 8px; height: 8px; border-radius: 50%; background: var(--c); display: inline-block;}
.mcard .value {font-size: 1.9rem; font-weight: 700; color: #0F172A; margin-top: 6px; letter-spacing: -0.02em; line-height: 1.15;}
.mcard .note {font-size: .78rem; color: #94A3B8; margin-top: 3px;}

/* Insight cards */
.icard {
    background: #fff; border: 1px solid #E8EAF2; border-left: 4px solid var(--c); border-radius: 12px;
    padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(15,23,42,.04);
}
.icard .t {font-size: .7rem; text-transform: uppercase; letter-spacing: .09em; color: var(--c); font-weight: 700;}
.icard .b {color: #1E293B; font-size: .92rem; margin-top: 4px; line-height: 1.5;}

/* Complaint cards */
.ccard {background: #fff; border: 1px solid #E8EAF2; border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(15,23,42,.04);}
.ctop {display: flex; justify-content: space-between; align-items: center; gap: 10px;}
.ctitle {font-weight: 700; font-size: 1rem; color: #0F172A;}
.cmeta {color: #64748B; font-size: .8rem; margin: 7px 0 9px 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px;}
.cdesc {color: #334155; font-size: .92rem; line-height: 1.5;}
.cremark {background: #F5F3FF; border-radius: 10px; padding: 9px 12px; margin-top: 11px; font-size: .86rem; color: #4338CA;}

/* Badges */
.badge {padding: 3px 11px; border-radius: 999px; font-size: .72rem; font-weight: 700; white-space: nowrap;}
.b-pending {background: #FEF3C7; color: #B45309;}
.b-progress {background: #DBEAFE; color: #1D4ED8;}
.b-solved {background: #D1FAE5; color: #047857;}
.p-high {background: #FEE2E2; color: #B91C1C;}
.p-medium {background: #FEF3C7; color: #B45309;}
.p-low {background: #E2E8F0; color: #475569;}

/* Login page */
.brand {
    background: radial-gradient(900px 420px at -10% -10%, #4F46E5 0%, rgba(79,70,229,0) 60%),
                radial-gradient(700px 380px at 110% 110%, rgba(124,58,237,.55) 0%, rgba(124,58,237,0) 60%), #0B1020;
    color: #fff; border-radius: 22px; padding: 44px 42px; min-height: 600px;
    box-shadow: 0 20px 50px rgba(11,16,32,.30);
}
.brand .top {display: flex; align-items: center; gap: 12px; margin-bottom: 56px;}
.brand .mark {
    width: 40px; height: 40px; border-radius: 11px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
    display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: .95rem; letter-spacing: .02em;
}
.brand .name {font-weight: 700; font-size: 1.05rem; letter-spacing: .01em;}
.brand h1 {color: #fff; font-size: 2.25rem; line-height: 1.18; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 14px 0; padding: 0;}
.brand .sub {color: rgba(255,255,255,.72); font-size: .98rem; margin-bottom: 44px; max-width: 420px;}
.brand .feat {display: flex; gap: 16px; margin: 0 0 20px 0; align-items: flex-start;}
.brand .num {font-size: .78rem; font-weight: 700; color: #A5B4FC; letter-spacing: .08em; padding-top: 3px;}
.brand .ft {font-weight: 600; font-size: .98rem;}
.brand .fd {color: rgba(255,255,255,.65); font-size: .88rem; margin-top: 2px;}
.brand .foot {margin-top: 36px; padding-top: 18px; border-top: 1px solid rgba(255,255,255,.14); color: rgba(255,255,255,.55); font-size: .8rem;}
.login-title {font-size: 1.5rem; font-weight: 700; color: #0F172A; margin: 0; letter-spacing: -0.02em;}
.login-sub {color: #64748B; font-size: .92rem; margin: 4px 0 14px 0;}

/* Progress stepper */
.stepper {display: flex; gap: 8px; margin-top: 14px;}
.step {flex: 1; font-size: .72rem; color: #94A3B8; border-top: 3px solid #E2E8F0; padding-top: 6px; font-weight: 600;}
.step.on {color: #4F46E5; border-top-color: #4F46E5;}
.step.done-solved {color: #047857; border-top-color: #10B981;}
.b-unassigned {background: #FFE4E6; color: #BE123C;}

/* High-contrast sidebar buttons (logout) */
section[data-testid="stSidebar"] button[kind^="primary"], section[data-testid="stSidebar"] button[data-testid^="stBaseButton-primary"] {
    background: #0F172A !important; color: #FFFFFF !important; box-shadow: none;
}
section[data-testid="stSidebar"] button[kind^="primary"] p, section[data-testid="stSidebar"] button[kind^="primary"] span {color: #FFFFFF !important;}

/* Sidebar user card */
.ucard {background: #F8F9FE; border: 1px solid #E8EAF6; border-radius: 12px; padding: 12px 14px; margin: 6px 0 12px 0;}
.ucard .uname {font-weight: 700; color: #0F172A; font-size: .95rem;}
.ucard .urole {font-size: .68rem; color: #4F46E5; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; margin-top: 2px;}
.ucard .uinfo {font-size: .78rem; color: #64748B; margin-top: 4px;}
</style>
"""

HIDE_SIDEBAR = """
<style>
section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"] {display: none;}
</style>
"""

TONES = {"info": "#4F46E5", "good": "#059669", "warn": "#D97706"}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hide_sidebar():
    st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)


def esc(text):
    return escape(str(text))


def fmt_dt(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)


def page_header(title, subtitle="", eyebrow=""):
    eyebrow_html = f'<div class="eyebrow">{esc(eyebrow)}</div>' if eyebrow else ""
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    st.markdown(f'<div class="page-head">{eyebrow_html}<h1>{esc(title)}</h1>{sub}</div>', unsafe_allow_html=True)


def metric_card(label, value, color="#4F46E5", note=""):
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    return (
        f'<div class="mcard" style="--c:{color}"><div class="label"><span class="dot"></span>{esc(label)}</div>'
        f'<div class="value">{esc(value)}</div>{note_html}</div>'
    )


def metric_row(items):
    """items = [(label, value, color) or (label, value, color, note), ...]"""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        col.markdown(metric_card(*item), unsafe_allow_html=True)


def insight_card(title, text, tone="info"):
    color = TONES.get(tone, TONES["info"])
    return f'<div class="icard" style="--c:{color}"><div class="t">{esc(title)}</div><div class="b">{esc(text)}</div></div>'


def status_badge(status):
    cls = {"Pending": "b-pending", "In Progress": "b-progress", "Solved": "b-solved"}.get(status, "b-pending")
    return f'<span class="badge {cls}">{esc(status)}</span>'


def priority_badge(priority):
    cls = {"High": "p-high", "Medium": "p-medium", "Low": "p-low"}.get(priority, "p-medium")
    return f'<span class="badge {cls}">{esc(priority)} priority</span>'


def stepper(status):
    steps = ["Pending", "In Progress", "Solved"]
    idx = steps.index(status) if status in steps else 0
    out = []
    for i, name in enumerate(steps):
        cls = "step"
        if i <= idx:
            cls += " done-solved" if (status == "Solved") else " on"
        out.append(f'<div class="{cls}">{name}</div>')
    return f'<div class="stepper">{"".join(out)}</div>'


def complaint_card(c, show_student=False, unassigned=False, progress=False):
    parts = [
        f"<span>{esc(c['category'])}</span>",
        priority_badge(c["priority"]),
        f"<span>{esc(c['hostel'])}, Room {esc(c['room'])}</span>",
        f"<span>{esc(fmt_dt(c['created_at']))}</span>",
    ]
    if show_student:
        parts.append(f"<span>{esc(c['student'])}</span>")
    if unassigned and c["status"] != "Solved":
        parts.append('<span class="badge b-unassigned">Unassigned</span>')
    remark = f'<div class="cremark">Warden remark: {esc(c["remarks"])}</div>' if c["remarks"] else ""
    return "".join(
        [
            '<div class="ccard"><div class="ctop">',
            f'<span class="ctitle">#{c["id"]} &middot; {esc(c["title"])}</span>{status_badge(c["status"])}</div>',
            f'<div class="cmeta">{"".join(parts)}</div>',
            f'<div class="cdesc">{esc(c["description"])}</div>{remark}{stepper(c["status"]) if progress else ""}</div>',
        ]
    )


def user_card(user):
    where = "All hostels" if user["role"] == "admin" else ", ".join(user.get("hostels") or [])
    return (
        f'<div class="ucard"><div class="uname">{esc(user["name"])}</div>'
        f'<div class="urole">{esc(user["role"])}</div><div class="uinfo">{esc(where)}</div></div>'
    )


def brand_panel():
    feats = [
        ("01", "Raise", "Report a problem in under a minute."),
        ("02", "Track", "Follow every complaint from Pending to Solved."),
        ("03", "Resolve", "Wardens act faster with clear, data-driven insights."),
    ]
    feat_html = "".join(
        f'<div class="feat"><span class="num">{n}</span><div><div class="ft">{t}</div><div class="fd">{d}</div></div></div>'
        for n, t, d in feats
    )
    return (
        '<div class="brand"><div class="top"><div class="mark">AH</div>'
        f'<div class="name">{esc(config.COLLEGE_SHORT)} HostelCare</div></div>'
        "<h1>Hostel complaints, resolved with accountability.</h1>"
        f'<div class="sub">The official complaint portal for {esc(config.COLLEGE_NAME)} hostels.</div>'
        f"{feat_html}"
        f'<div class="foot">Sign-up is limited to verified {esc(config.COLLEGE_SHORT)} students and authorised wardens.</div></div>'
    )


def count_status(df, status):
    return int((df["status"] == status).sum()) if not df.empty else 0
