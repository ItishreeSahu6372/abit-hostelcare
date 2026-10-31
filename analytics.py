"""Pure-pandas analytics: no charts here, only numbers and insights."""
import numpy as np
import pandas as pd

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
BLOCKS = ["Night", "Morning", "Afternoon", "Evening"]
AGE_LABELS = ["0-2 days", "3-7 days", "8-14 days", "15+ days"]


def prepare(df, now=None):
    d = df.copy()
    now = now or pd.Timestamp.now()
    d["created_at"] = pd.to_datetime(d["created_at"])
    d["resolved_at"] = pd.to_datetime(d["resolved_at"])
    d["is_open"] = d["status"] != "Solved"
    d["age_days"] = (now - d["created_at"]).dt.total_seconds() / 86400
    d["resolution_hours"] = (d["resolved_at"] - d["created_at"]).dt.total_seconds() / 3600
    d["weekday"] = d["created_at"].dt.day_name()
    d["hour"] = d["created_at"].dt.hour
    d["time_block"] = pd.cut(d["hour"], bins=[-1, 5, 11, 17, 23], labels=BLOCKS).astype(str)
    d["week"] = d["created_at"].dt.to_period("W").dt.start_time
    return d


def fmt_duration(hours):
    if hours is None or pd.isna(hours):
        return "-"
    if hours < 1:
        return f"{hours * 60:.0f} min"
    if hours < 48:
        return f"{hours:.1f} h"
    return f"{hours / 24:.1f} days"


def kpis(d):
    total = len(d)
    solved = int((~d["is_open"]).sum())
    res = d["resolution_hours"].dropna()
    return {
        "total": total,
        "solved": solved,
        "open": total - solved,
        "rate": (solved / total * 100) if total else 0.0,
        "mean_hours": float(res.mean()) if len(res) else float("nan"),
        "median_hours": float(res.median()) if len(res) else float("nan"),
        "within_48h": float((res <= 48).mean() * 100) if len(res) else float("nan"),
        "overdue": int(((d["is_open"]) & (d["age_days"] > 7)).sum()),
        "high_open": int(((d["is_open"]) & (d["priority"] == "High")).sum()),
    }


def summary_table(d):
    groups = [("All categories", d)]
    order = d["category"].value_counts().index.tolist()
    groups += [(c, d[d["category"] == c]) for c in order]
    rows = []
    for name, g in groups:
        r = g["resolution_hours"].dropna()
        solved = int((~g["is_open"]).sum())
        rows.append(
            {
                "Category": name,
                "Complaints": len(g),
                "Solved": solved,
                "Open": len(g) - solved,
                "Resolution rate": f"{solved / len(g) * 100:.0f}%",
                "Mean time": fmt_duration(r.mean() if len(r) else np.nan),
                "Median time": fmt_duration(r.median() if len(r) else np.nan),
                "90th percentile": fmt_duration(r.quantile(0.9) if len(r) else np.nan),
                "Slowest": fmt_duration(r.max() if len(r) else np.nan),
            }
        )
    return pd.DataFrame(rows)


def insights(d, now=None):
    """Plain-English findings. Each item: (title, text, tone) with tone info/good/warn."""
    now = now or pd.Timestamp.now()
    out = []
    total = len(d)
    if total == 0:
        return out

    vc = d["category"].value_counts()
    out.append(("Top issue", f"{vc.index[0]} makes up {vc.iloc[0] / total * 100:.0f}% of complaints ({int(vc.iloc[0])} of {total}).", "info"))

    solved = d.dropna(subset=["resolution_hours"])
    g = solved.groupby("category")["resolution_hours"].agg(["median", "count"])
    g = g[g["count"] >= 3]
    if len(g) >= 2:
        slow, fast = g["median"].idxmax(), g["median"].idxmin()
        tone = "warn" if g["median"].max() > 72 else "info"
        out.append(("Resolution speed",
                    f"{slow} issues take longest to fix (median {fmt_duration(g['median'].max())}); {fast} is fastest ({fmt_duration(g['median'].min())}).",
                    tone))

    last7 = int((d["created_at"] >= now - pd.Timedelta(days=7)).sum())
    prev7 = int(((d["created_at"] >= now - pd.Timedelta(days=14)) & (d["created_at"] < now - pd.Timedelta(days=7))).sum())
    if prev7 > 0:
        change = (last7 - prev7) / prev7 * 100
        tone = "warn" if change > 20 else ("good" if change < -20 else "info")
        out.append(("Weekly trend", f"{last7} new complaints in the last 7 days vs {prev7} in the 7 days before ({change:+.0f}%).", tone))
    elif last7 > 0:
        out.append(("Weekly trend", f"{last7} new complaints in the last 7 days; none in the 7 days before.", "info"))

    wd = d["weekday"].value_counts()
    tb = d["time_block"].value_counts()
    out.append(("Peak time", f"Most complaints are raised on {wd.index[0]}s, mainly in the {tb.index[0].lower()}.", "info"))

    rooms = d.groupby(["hostel", "room"]).size().sort_values(ascending=False)
    repeat = rooms[rooms >= 3]
    if len(repeat):
        (hostel, room), n = repeat.index[0], int(repeat.iloc[0])
        out.append(("Repeat rooms", f"{len(repeat)} room(s) have 3 or more complaints. Room {room} ({hostel}) has {n}; check for a recurring fault.", "warn"))

    open_ = d[d["is_open"]]
    old = open_[open_["age_days"] > 7]
    if len(old):
        oldest = old.sort_values("age_days", ascending=False).iloc[0]
        out.append(("Backlog", f"{len(old)} complaint(s) have been open for over 7 days. Oldest: #{int(oldest['id'])} ({oldest['category']}), open {oldest['age_days']:.0f} days.", "warn"))
    else:
        out.append(("Backlog", "No complaint has been open for more than 7 days.", "good"))

    if len(solved):
        pct = (solved["resolution_hours"] <= 48).mean() * 100
        out.append(("Service level", f"{pct:.0f}% of solved complaints were fixed within 48 hours.", "good" if pct >= 70 else "warn"))

    high_open = int(((d["is_open"]) & (d["priority"] == "High")).sum())
    if high_open:
        out.append(("High priority", f"{high_open} high-priority complaint(s) are still open and need attention first.", "warn"))
    return out
