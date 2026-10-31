import pandas as pd
import streamlit as st

import analytics
import charts
import database as db
import styles

scope = st.session_state.get("scope", [])
label = scope[0] if len(scope) == 1 else f"{len(scope)} hostels"
styles.page_header("Analytics", f"Insights and summary statistics for {label}." if scope else "No hostel assigned yet.", "Analytics")

raw = db.get_complaints(hostels=scope)
if raw.empty:
    st.info("There is no data to analyse yet.")
    st.stop()

PERIODS = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": None}
choice = st.radio("Period", list(PERIODS), index=1, horizontal=True)

d = analytics.prepare(raw)
if PERIODS[choice]:
    d = d[d["created_at"] >= pd.Timestamp.now() - pd.Timedelta(days=PERIODS[choice])]
if d.empty:
    st.info("No complaints in this period. Try a longer period.")
    st.stop()


def show(builder, *args, empty_msg="Not enough data for this chart.", **kwargs):
    try:
        chart = builder(*args, **kwargs)
        if chart is None:
            st.info(empty_msg)
        else:
            st.altair_chart(chart)
    except Exception as exc:  # a chart problem must never break the page
        st.warning(f"This chart could not be drawn: {exc}")


k = analytics.kpis(d)
styles.metric_row(
    [
        ("Complaints", k["total"], "#4F46E5", f"{choice.lower()}"),
        ("Resolution rate", f"{k['rate']:.0f}%", "#10B981", f"{k['solved']} solved, {k['open']} open"),
        ("Avg. resolution time", analytics.fmt_duration(k["mean_hours"]), "#3B82F6", "solved complaints"),
        ("Median resolution time", analytics.fmt_duration(k["median_hours"]), "#7C3AED", "typical case"),
    ]
)
st.write("")
styles.metric_row(
    [
        ("Fixed within 48 h", "-" if pd.isna(k["within_48h"]) else f"{k['within_48h']:.0f}%", "#10B981", "service level"),
        ("Open over 7 days", k["overdue"], "#EF4444", "backlog"),
        ("High priority open", k["high_open"], "#F59E0B", "act first"),
        ("Hostels in view", d["hostel"].nunique(), "#64748B", ""),
    ]
)

st.write("")
st.subheader("Key insights")
items = analytics.insights(d)
cols = st.columns(2)
for i, (title, text, tone) in enumerate(items):
    cols[i % 2].markdown(styles.insight_card(title, text, tone), unsafe_allow_html=True)

st.write("")
tab_trend, tab_cat, tab_perf, tab_hot = st.tabs(["Trends", "Categories", "Performance", "Hotspots"])

with tab_trend:
    st.markdown("**Weekly volume: new vs solved**")
    show(charts.trend_chart, d)
    st.markdown("**When are complaints raised?** (day of week and time of day)")
    show(charts.heatmap_chart, d)
    st.caption("Night: 12-6 AM. Morning: 6 AM-12 PM. Afternoon: 12-6 PM. Evening: 6 PM-12 AM.")

with tab_cat:
    left, right = st.columns(2)
    with left:
        st.markdown("**Share of complaints by category**")
        show(charts.category_donut, d)
    with right:
        st.markdown("**Priority mix by category**")
        show(charts.priority_chart, d)

with tab_perf:
    left, right = st.columns(2)
    with left:
        st.markdown("**Median time to resolve, by category**")
        show(charts.resolution_chart, d, empty_msg="No solved complaints yet.")
    with right:
        st.markdown("**Open complaints by age**")
        show(charts.ageing_chart, d, empty_msg="No open complaints. Everything is solved.")

with tab_hot:
    multi = d["hostel"].nunique() > 1
    left, right = st.columns(2)
    with left:
        st.markdown("**Rooms with the most complaints**")
        show(charts.rooms_chart, d, multi_hostel=multi)
    with right:
        if multi:
            st.markdown("**Open vs solved by hostel**")
            show(charts.hostel_chart, d)
        else:
            st.caption("Select more than one hostel to compare hostels.")

st.write("")
st.subheader("Summary statistics")
table = analytics.summary_table(d)
st.dataframe(table, hide_index=True)
st.download_button("Download summary as CSV", table.to_csv(index=False).encode("utf-8"), "summary_statistics.csv", "text/csv")
