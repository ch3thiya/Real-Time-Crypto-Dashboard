import streamlit as st
import pandas as pd
import altair as alt
from datetime import timedelta

st.set_page_config(page_title="Crypto Tracker", layout="wide", page_icon="⚡")

st.title("🪙 Real Time Crypto Pipeline")

try:
    conn = st.connection("postgresql", type="sql")
    df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 400", ttl=10)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if not df.empty:
    df['coin'] = df['coin'].replace({'binancecoin': 'bnb'})
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    last_scrape_utc = df['timestamp'].max()
    last_scrape_local = last_scrape_utc + timedelta(hours=5, minutes=30)
    st.caption(f"🕒 **Last Scrape:** {last_scrape_local.strftime('%Y-%m-%d %H:%M:%S')} (GMT+5:30)")

    df['timestamp'] = df['timestamp'].dt.floor('min')

    unique_times = sorted(df['timestamp'].unique(), reverse=True)
    latest_pull = df[df['timestamp'] == unique_times[0]].set_index('coin')

    st.subheader("Current Prices (vs Last Scrape)")
    metric_cols = st.columns(len(latest_pull), gap="large")

    for i, (coin_name, row) in enumerate(latest_pull.iterrows()):
        current_price = row['price']
        delta_val = 0

        if len(unique_times) > 1:
            prev_time = unique_times[1]
            prev_data = df[(df['timestamp'] == prev_time) & (df['coin'] == coin_name)]
            if not prev_data.empty:
                old_price = prev_data.iloc[0]['price']
                delta_val = ((current_price - old_price) / old_price) * 100

        with metric_cols[i]:
            st.metric(
                label=coin_name.upper(),
                value=f"${current_price:,.2f}",
                delta=f"{delta_val:.2f}%"
            )

    st.divider()
    st.subheader("Coin Fluctuations")

    chart_cols = st.columns(4, gap="large")
    coins = sorted(df['coin'].unique())

    for i, coin in enumerate(coins):
        if i < len(chart_cols):
            with chart_cols[i]:
                st.markdown(f"### {coin.upper()}")
                coin_df = df[df['coin'] == coin].sort_values('timestamp')

                chart = alt.Chart(coin_df).mark_line(
                    color="#00ff00",
                    strokeWidth=3
                ).encode(
                    x=alt.X('timestamp:T', title='Time'),
                    y=alt.Y('price:Q', title='Price (USD)', scale=alt.Scale(zero=False)),
                    tooltip=['timestamp', 'price']
                ).properties(height=250)

                st.altair_chart(chart, use_container_width=True)

else:
    st.warning("No data found. Ensure GitHub Action is running successfully.")
