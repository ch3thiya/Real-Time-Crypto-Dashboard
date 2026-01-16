import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide")
st.title("🪙 Real-Time Crypto Pipeline")

if "url" in st.secrets.get("connections", {}).get("postgresql", {}):
    db_url = st.secrets["connections"]["postgresql"]["url"]
else:
    db_url = st.secrets.get("DATABASE_URL")

if not db_url:
    st.error("❌ Secrets not found! Check Streamlit Cloud Settings.")
    st.stop()

try:
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 200", engine)
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

if not df.empty:
    st.write(df.head()) 
    st.line_chart(df.pivot_table(index='timestamp', columns='coin', values='price'))
else:
    st.warning("No data found. Check Supabase SQL Editor to see if table is truly empty.")