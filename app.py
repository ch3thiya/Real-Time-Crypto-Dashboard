import streamlit as st
import pandas as pd

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide", page_icon="🪙")
st.title("🪙 Real-Time Crypto Pipeline")

try:
    conn = st.connection("postgresql", type="sql")
    # Fetch 100 rows to ensure we have at least 2 pulls for each of the 4 coins
    df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 100", ttl=10)
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

if not df.empty and len(df) > 4:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort and group to get the latest and previous data points
    # We use .first() and .nth(1) to get the two most recent pulls
    sorted_df = df.sort_values('timestamp', ascending=False)
    latest_pull = sorted_df.groupby('coin').first()
    previous_pull = sorted_df.groupby('coin').nth(1)

    st.subheader("Current Prices (vs Last Hour)")
    cols = st.columns(len(latest_pull))
    
    # .iterrows() now gives (coin_name, row_data)
    for i, (coin_name, row) in enumerate(latest_pull.iterrows()):
        current_price = row['price']
        
        try:
            old_price = previous_pull.loc[coin_name]['price']
            delta_percent = ((current_price - old_price) / old_price) * 100
        except:
            delta_percent = 0 # Fallback if only 1 data point exists

        cols[i].metric(
            label=coin_name.upper(), 
            value=f"${current_price:,.2f}",
            delta=f"{delta_percent:.2f}% (1h)"
        )

    st.subheader("Price Fluctuations (Last 24 Hours)")
    # Pivot the data so each coin has its own line
    chart_data = df.pivot_table(index='timestamp', columns='coin', values='price')
    st.line_chart(chart_data)
else:
    st.warning("Waiting for more data... Please run your GitHub Action twice to see the arrows and chart!")