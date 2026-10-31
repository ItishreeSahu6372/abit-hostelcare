"""Altair charts used on the Analytics page."""
import altair as alt
import pandas as pd

import analytics

ACCENT = "#4F46E5"
SOLVED = "#10B981"
PRIORITY_COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#94A3B8"}
CATEGORY_RANGE = ["#4F46E5", "#7C3AED", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#94A3B8"]
AGE_RANGE = ["#10B981", "#84CC16", "#F59E0B", "#EF4444"]


def _finish(chart, height=300):
    return (
        chart.properties(height=height, width="container")
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#EEF1F6", domain=False, tickColor="#EEF1F6",
                        labelColor="#475569", titleColor="#475569", labelFontSize=12, titleFontSize=12)
        .configure_legend(labelColor="#475569", titleColor="#475569", labelFontSize=12)
    )


def _counts(series, name="Count"):
    vc = series.value_counts()
    return pd.DataFrame({series.name: vc.index.tolist(), name: vc.values.tolist()})


def trend_chart(d):
    created = d.groupby("week").size().reset_index(name="Count").rename(columns={"week": "Week"})
    created["Series"] = "New complaints"
    s = d.dropna(subset=["resolved_at"]).copy()
    s["rweek"] = s["resolved_at"].dt.to_period("W").dt.start_time
    solved = s.groupby("rweek").size().reset_index(name="Count").rename(columns={"rweek": "Week"})
    solved["Series"] = "Solved"
    data = pd.concat([created, solved], ignore_index=True)
    chart = (
        alt.Chart(data)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("Week:T", title=None, axis=alt.Axis(format="%d %b")),
            y=alt.Y("Count:Q", title="Complaints"),
            color=alt.Color("Series:N", scale=alt.Scale(domain=["New complaints", "Solved"], range=[ACCENT, SOLVED]),
                            legend=alt.Legend(orient="top", title=None)),
            tooltip=[alt.Tooltip("Week:T", format="%d %b %Y", title="Week of"), "Series:N", "Count:Q"],
        )
    )
    return _finish(chart, 300)


def category_donut(d):
    data = _counts(d["category"], "Complaints")
    cats = data["category"].tolist()
    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=70, outerRadius=120)
        .encode(
            theta=alt.Theta("Complaints:Q"),
            color=alt.Color("category:N", title=None, scale=alt.Scale(domain=cats, range=CATEGORY_RANGE[: len(cats)]),
                            legend=alt.Legend(orient="right")),
            tooltip=["category:N", "Complaints:Q"],
        )
    )
    return _finish(chart, 300)


def priority_chart(d):
    data = d.groupby(["category", "priority"]).size().reset_index(name="Complaints")
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadius=3)
        .encode(
            x=alt.X("category:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Complaints:Q", title="Complaints"),
            color=alt.Color("priority:N", title="Priority", sort=["High", "Medium", "Low"],
                            scale=alt.Scale(domain=list(PRIORITY_COLORS), range=list(PRIORITY_COLORS.values())),
                            legend=alt.Legend(orient="top")),
            tooltip=["category:N", "priority:N", "Complaints:Q"],
        )
    )
    return _finish(chart, 300)


def resolution_chart(d):
    s = d.dropna(subset=["resolution_hours"])
    if s.empty:
        return None
    g = s.groupby("category")["resolution_hours"].median().reset_index(name="Hours")
    g["Days"] = (g["Hours"] / 24).round(2)
    chart = (
        alt.Chart(g)
        .mark_bar(cornerRadius=3, color=ACCENT)
        .encode(
            y=alt.Y("category:N", sort="-x", title=None),
            x=alt.X("Days:Q", title="Median days to resolve"),
            tooltip=["category:N", alt.Tooltip("Days:Q", title="Median days")],
        )
    )
    return _finish(chart, 300)


def ageing_chart(d):
    o = d[d["is_open"]]
    if o.empty:
        return None
    buckets = pd.cut(o["age_days"], bins=[-1, 2, 7, 14, 10**6], labels=analytics.AGE_LABELS).astype(str)
    counts = buckets.value_counts()
    data = pd.DataFrame({"Age": analytics.AGE_LABELS, "Open complaints": [int(counts.get(a, 0)) for a in analytics.AGE_LABELS]})
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadius=3)
        .encode(
            x=alt.X("Age:N", sort=analytics.AGE_LABELS, title="How long they have been open", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Open complaints:Q"),
            color=alt.Color("Age:N", scale=alt.Scale(domain=analytics.AGE_LABELS, range=AGE_RANGE), legend=None),
            tooltip=["Age:N", "Open complaints:Q"],
        )
    )
    return _finish(chart, 300)


def heatmap_chart(d):
    data = d.groupby(["weekday", "time_block"]).size().reset_index(name="Count")
    full = pd.MultiIndex.from_product([analytics.DAY_ORDER, analytics.BLOCKS], names=["weekday", "time_block"])
    data = data.set_index(["weekday", "time_block"]).reindex(full, fill_value=0).reset_index()
    data = data.rename(columns={"weekday": "Day", "time_block": "Time"})
    threshold = max(1, data["Count"].max()) / 2
    base = alt.Chart(data).encode(
        x=alt.X("Time:N", sort=analytics.BLOCKS, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Day:N", sort=analytics.DAY_ORDER, title=None),
    )
    rect = base.mark_rect(cornerRadius=4).encode(
        color=alt.Color("Count:Q", scale=alt.Scale(range=["#EEF2FF", ACCENT]), legend=None),
        tooltip=["Day:N", "Time:N", "Count:Q"],
    )
    text = base.mark_text(fontSize=12, fontWeight="bold").encode(
        text="Count:Q",
        color=alt.condition(alt.datum.Count > threshold, alt.value("white"), alt.value("#1E293B")),
    )
    return _finish(rect + text, 330)


def rooms_chart(d, multi_hostel=False):
    r = d.groupby(["hostel", "room"]).size().reset_index(name="Complaints")
    r["Room"] = (r["hostel"] + " / " + r["room"]) if multi_hostel else r["room"]
    r = r.sort_values("Complaints", ascending=False).head(8)
    chart = (
        alt.Chart(r)
        .mark_bar(cornerRadius=3, color="#7C3AED")
        .encode(
            y=alt.Y("Room:N", sort="-x", title=None),
            x=alt.X("Complaints:Q", title="Complaints raised"),
            tooltip=["Room:N", "Complaints:Q"],
        )
    )
    return _finish(chart, 300)


def hostel_chart(d):
    g = d.groupby("hostel").agg(Open=("is_open", "sum"), Total=("id", "count")).reset_index()
    g["Solved"] = g["Total"] - g["Open"]
    data = g.melt(id_vars="hostel", value_vars=["Open", "Solved"], var_name="State", value_name="Complaints")
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadius=3)
        .encode(
            x=alt.X("hostel:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Complaints:Q"),
            color=alt.Color("State:N", scale=alt.Scale(domain=["Open", "Solved"], range=["#F59E0B", SOLVED]),
                            legend=alt.Legend(orient="top", title=None)),
            tooltip=["hostel:N", "State:N", "Complaints:Q"],
        )
    )
    return _finish(chart, 300)
