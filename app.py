import streamlit as st
import pandas as pd

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide", page_icon="🪙")
st.title("🪙 Real-Time Crypto Pipeline")

try:
    conn = st.connection("postgresql", type="sql")
    df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 400", ttl=10)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if not df.empty:
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.floor('min')

    unique_times = sorted(df['timestamp'].unique(), reverse=True)
    latest_pull = df[df['timestamp'] == unique_times[0]].set_index('coin')

    st.subheader("Current Prices (vs Last Scrape)")
    metric_cols = st.columns(4)
    
    for i, (coin_name, row) in enumerate(latest_pull.iterrows()):
        current_price = row['price']
        delta_val = 0
        
        if len(unique_times) > 1:
            prev_time = unique_times[1]
            prev_data = df[(df['timestamp'] == prev_time) & (df['coin'] == coin_name)]
            if not prev_data.empty:
                old_price = prev_data.iloc[0]['price']
                delta_val = ((current_price - old_price) / old_price) * 100

        metric_cols[i].metric(
            label=coin_name.upper(), 
            value=f"${current_price:,.2f}",
            delta=f"{delta_val:.2f}%"
        )

    st.divider()

    st.subheader("Individual Coin Fluctuations")
    
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    chart_containers = [row1_col1, row1_col2, row2_col1, row2_col2]

    coins = sorted(df['coin'].unique()) # ['binancecoin', 'ethereum', 'litecoin', 'solana']

    for i, coin in enumerate(coins):
        with chart_containers[i]:
            st.markdown(f"### {coin.upper()}")
            coin_df = df[df['coin'] == coin].sort_values('timestamp')
            
            st.line_chart(
                coin_df.set_index('timestamp')['price'], 
                height=250,
                use_container_width=True
            )

else:
    st.warning("No data found. Ensure GitHub Action is running successfully.")