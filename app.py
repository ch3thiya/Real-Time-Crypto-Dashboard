import streamlit as st
import pandas as pd

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide", page_icon="🪙")

st.title("🪙 Real-Time Crypto Pipeline")

try:
    db_url = st.secrets["DATABASE_URL"]
    conn = st.connection("postgresql", type="sql", url=db_url)
except Exception as e:
    st.error("Could not find DATABASE_URL in secrets!")
    st.stop()

df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 200", ttl=60)

if not df.empty:
    latest_data = df.groupby('coin').first().reset_index()
    cols = st.columns(len(latest_data))
    
    for i, row in latest_data.iterrows():
        cols[i].metric(
            label=row['coin'].upper(), 
            value=f"${row['price']:,.2f}",
            delta=f"{row['change_24h']:.2f}%"
        )

    st.subheader("Price Trends (Last 24 Pulls)")
    chart_data = df.pivot_table(index='timestamp', columns='coin', values='price')
    st.line_chart(chart_data)
else:
    st.warning("No data found in Supabase. Check if your GitHub Action has run yet!")