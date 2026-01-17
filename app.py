import streamlit as st
import pandas as pd

st.set_page_config(page_title="2026 Crypto Tracker", layout="wide", page_icon="🪙")
st.title("🪙 Real-Time Crypto Pipeline")

try:
    conn = st.connection("postgresql", type="sql")
    df = conn.query("SELECT * FROM crypto_prices ORDER BY timestamp DESC LIMIT 500", ttl=10)
except Exception as e:
    st.error("Database connection failed. Check Streamlit Secrets.")
    st.stop()

if not df.empty:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    latest_pull = df.sort_values('timestamp', ascending=False).groupby('coin').nth(0)
    previous_pull = df.sort_values('timestamp', ascending=False).groupby('coin').nth(1)

    st.subheader("Current Prices (vs Last Hour)")
    cols = st.columns(len(latest_pull))

    for i, (coin, row) in enumerate(latest_pull.iterrows()):
        current_price = row['price']

        try:
            old_price = previous_pull.loc[coin]['price']
            price_delta = current_price - old_price
            delta_percent = (price_delta / old_price) * 100
        except:
            delta_percent = 0

        cols[i].metric(
            label=coin.upper(),
            value=f"${current_price:,.2f}",
            delta=f"{delta_percent:.2f}% (1h)"
        )

    st.subheader("Price Fluctuations (Last 24 Hours)")
    last_24h = df[df['timestamp'] > (pd.Timestamp.now() - pd.Timedelta(hours=24))]

    if len(last_24h) > len(latest_pull):
        chart_data = last_24h.pivot_table(index='timestamp', columns='coin', values='price')
        st.line_chart(chart_data)
    else:
        st.info("Gathering more data points to generate the 24-hour chart...")
else:
    st.warning("No data found. Ensure GitHub Action is running and NOT truncating the table.")