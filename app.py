import streamlit as st
import pandas as pd

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide", page_icon="🪙")
st.title("🪙 Real-Time Crypto Pipeline")

try:
    conn = st.connection("postgresql", type="sql")
    # Pull enough data for history (4 coins * 24 hours = ~100 rows)
    df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 200", ttl=10)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if not df.empty:
    # 1. Align Data Types
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 2. CRITICAL: Floor timestamps to the minute to align X-axis
    df['timestamp'] = df['timestamp'].dt.floor('min')

    # 3. Get unique timestamps to find "Now" vs "Last Hour"
    unique_times = sorted(df['timestamp'].unique(), reverse=True)

    st.subheader("Current Prices (vs Last Hour)")
    cols = st.columns(4) # Adjust if you have more/less than 4 coins
    
    # Get the latest data for each coin
    latest_pull = df[df['timestamp'] == unique_times[0]].set_index('coin')

    for i, (coin_name, row) in enumerate(latest_pull.iterrows()):
        current_price = row['price']
        delta_val = 0
        
        # Calculate delta against the previous scrape
        if len(unique_times) > 1:
            prev_time = unique_times[1]
            prev_data = df[(df['timestamp'] == prev_time) & (df['coin'] == coin_name)]
            if not prev_data.empty:
                old_price = prev_data.iloc[0]['price']
                delta_val = ((current_price - old_price) / old_price) * 100

        if i < len(cols):
            cols[i].metric(
                label=coin_name.upper(), 
                value=f"${current_price:,.2f}",
                delta=f"{delta_val:.2f}%"
            )

    # 4. Line Chart (Last 24 Hours)
    st.subheader("Price Fluctuations (History)")
    # pivot_table connects the dots because coins now share timestamp values
    chart_df = df.pivot_table(index='timestamp', columns='coin', values='price', aggfunc='mean')
    st.line_chart(chart_df)

else:
    st.warning("No data found. Ensure your GitHub Action has run successfully.")