"""Email notifications (Gmail SMTP). Works only when SMTP secrets are set."""
import logging
import os
import smtplib
import ssl
import threading
from email.message import EmailMessage
from html import escape

import streamlit as st

import config
import database as db


def _get(name, default=""):
    try:
        value = st.secrets[name]
    except Exception:
        value = os.environ.get(name, default)
    return str(value).strip() if value is not None else default


def smtp_settings():
    user = _get("SMTP_USER")
    try:
        port = int(_get("SMTP_PORT", "465") or 465)
    except ValueError:
        port = 465
    return {
        "host": _get("SMTP_HOST", "smtp.gmail.com"),
        "port": port,
        "user": user,
        "password": _get("SMTP_PASSWORD").replace(" ", ""),  # Gmail shows app passwords with spaces
        "sender": _get("SMTP_FROM") or user,
    }


def is_configured(cfg=None):
    cfg = cfg or smtp_settings()
    return bool(cfg["user"] and cfg["password"])


def recipients_for(hostel, cfg=None):
    cfg = cfg or smtp_settings()
    emails = [email for _name, email in db.get_warden_emails(hostel)]  # active wardens of this hostel only
    seen, unique = set(), []
    for e in emails:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique.append(e)
    return unique


def _send(cfg, recipients, subject, text, html):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{config.COLLEGE_SHORT} HostelCare <{cfg['sender']}>"
    msg["To"] = ", ".join(recipients)
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    context = ssl.create_default_context()
    if cfg["port"] == 465:
        with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=20) as server:
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
    else:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
            server.starttls(context=context)
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)


def _safe_send(*args):
    try:
        _send(*args)
    except Exception as exc:  # never break the app because of email
        logging.warning("Email notification failed: %s", exc)


def _html(complaint):
    c = {k: escape(str(v)) for k, v in complaint.items()}
    return (
        '<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #E5E7EB;border-radius:12px;overflow:hidden">'
        f'<div style="background:#4F46E5;color:#fff;padding:18px 22px"><div style="font-size:12px;letter-spacing:.08em">{escape(config.COLLEGE_SHORT)} HOSTELCARE</div>'
        f'<div style="font-size:20px;font-weight:700;margin-top:4px">New complaint #{c["id"]}</div></div>'
        '<div style="padding:20px 22px;color:#0F172A;font-size:14px;line-height:1.6">'
        f'<div style="font-size:16px;font-weight:700">{c["title"]}</div>'
        f'<div style="color:#64748B;margin:4px 0 12px 0">{c["category"]} &middot; {c["priority"]} priority</div>'
        f'<div style="background:#F8FAFC;border-radius:8px;padding:12px">{c["description"]}</div>'
        f'<table style="margin-top:14px;font-size:14px"><tr><td style="color:#64748B;padding-right:14px">Hostel</td><td>{c["hostel"]}</td></tr>'
        f'<tr><td style="color:#64748B;padding-right:14px">Room</td><td>{c["room"]}</td></tr>'
        f'<tr><td style="color:#64748B;padding-right:14px">Student</td><td>{c["student"]} ({c["student_email"]})</td></tr></table>'
        '<div style="margin-top:18px;color:#64748B;font-size:12px">Sign in to HostelCare to update the status.</div>'
        "</div></div>"
    )


def notify_new_complaint(complaint):
    """Sends in the background. Returns True if an email was queued."""
    cfg = smtp_settings()
    if not is_configured(cfg):
        return False
    recipients = recipients_for(complaint["hostel"], cfg)
    if not recipients:
        return False
    subject = f"[{config.COLLEGE_SHORT} HostelCare] {complaint['priority']} priority complaint #{complaint['id']} - {complaint['hostel']}"
    text = (
        f"New complaint #{complaint['id']}\n\n{complaint['title']}\n"
        f"Category: {complaint['category']}  |  Priority: {complaint['priority']}\n"
        f"Hostel: {complaint['hostel']}  |  Room: {complaint['room']}\n"
        f"Student: {complaint['student']} ({complaint['student_email']})\n\n{complaint['description']}\n"
    )
    threading.Thread(target=_safe_send, args=(cfg, recipients, subject, text, _html(complaint)), daemon=True).start()
    return True


def send_test(to_email):
    """Sends one test mail right now. Returns (ok, message)."""
    cfg = smtp_settings()
    if not is_configured(cfg):
        return False, "Email is not configured yet. Add SMTP_USER and SMTP_PASSWORD in secrets."
    try:
        _send(cfg, [to_email], f"[{config.COLLEGE_SHORT} HostelCare] Test email",
              "Your HostelCare email notifications are working.",
              "<p>Your <b>HostelCare</b> email notifications are working.</p>")
        return True, f"Test email sent to {to_email}."
    except Exception as exc:
        return False, f"Could not send: {exc}"
