import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT, "anomaly_log.csv")

st.set_page_config(page_title="RDPMS Live", layout="wide")
st.title("🔴 Real-Time Anomaly Detection")

# Auto-refresh every 2 seconds
refresh = st.empty()

placeholder_chart1 = st.empty()
placeholder_chart2 = st.empty()
placeholder_table  = st.empty()
placeholder_metrics = st.empty()

while True:
    if not os.path.exists(LOG_FILE):
        st.warning("No data yet — start client.py first.")
        time.sleep(2)
        continue

    df = pd.read_csv(LOG_FILE)

    if df.empty:
        st.info("Waiting for readings...")
        time.sleep(2)
        continue

    # ── Keep last 200 rows for display ──────────────────────
    df_plot = df.tail(200).reset_index(drop=True)
    anomalies = df_plot[df_plot["is_anomaly"] == 1]
    normals   = df_plot[df_plot["is_anomaly"] == 0]

    total     = len(df)
    n_anomaly = df["is_anomaly"].sum()
    n_normal  = total - n_anomaly

    # ── Metrics row ──────────────────────────────────────────
    with placeholder_metrics.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Readings",  total)
        c2.metric("Normal",          int(n_normal))
        c3.metric("Anomalies",       int(n_anomaly))
        c4.metric("Anomaly Rate",    f"{(n_anomaly/total*100):.1f}%" if total>0 else "—")

    # ── Sensor 1 chart ───────────────────────────────────────
    with placeholder_chart1.container():
        st.subheader("Sensor 1 (real-time)")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["sensor_1"],
            mode="lines", name="sensor_1",
            line=dict(color="steelblue", width=1.5)
        ))
        fig1.add_trace(go.Scatter(
            x=anomalies.index, y=anomalies["sensor_1"],
            mode="markers", name="Anomaly",
            marker=dict(color="red", size=7, symbol="circle")
        ))
        fig1.update_layout(
            height=280, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#f9fafb"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#374151")
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ── Sensor 2 chart ───────────────────────────────────────
    with placeholder_chart2.container():
        st.subheader("Sensor 2 (real-time)")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["sensor_2"],
            mode="lines", name="sensor_2",
            line=dict(color="#22c55e", width=1.5)
        ))
        fig2.add_trace(go.Scatter(
            x=anomalies.index, y=anomalies["sensor_2"],
            mode="markers", name="Anomaly",
            marker=dict(color="red", size=7, symbol="circle")
        ))
        fig2.update_layout(
            height=280, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#f9fafb"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#374151")
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Recent anomalies table ────────────────────────────────
    with placeholder_table.container():
        st.subheader("Recent Anomalies")
        recent = df[df["is_anomaly"] == 1].tail(10)
        if recent.empty:
            st.success("No anomalies detected yet.")
        else:
            st.dataframe(recent[::-1], use_container_width=True)

    time.sleep(1)