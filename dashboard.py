
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from trade_engine import run_backtest, run_live_forward_test
from zerodha_connector import get_strike_list

st.set_page_config(page_title="NIFTY Options Dashboard", layout="wide")
st.title("📊 NIFTY Options | Paper, Forward & Live Trading Dashboard")

# === SIDEBAR CONFIG ===
st.sidebar.header("🔧 Strategy Configuration")
mode = st.sidebar.radio("Mode", ["Backtest", "Forward Test"])
candle_type = st.sidebar.selectbox("Candle Type", ["Heikin Ashi", "Normal"])
interval = st.sidebar.selectbox("Time Frame", ["1minute", "3minute", "5minute", "15minute", "1hour"])
option_type = st.sidebar.radio("Option Type", ["CE", "PE"])
strike_base = st.sidebar.number_input("ATM Price (estimate)", value=25500, step=50)
expiry = st.sidebar.text_input("Expiry (e.g., 25JUL)", value="25JUL")
strike_gap = st.sidebar.slider("Strike Gap", -300, 300, 0, step=50)
capital = st.sidebar.number_input("Capital (₹)", value=100000, step=5000)
dynamic_position = st.sidebar.checkbox("🧠 Use Dynamic Position Sizing", value=True)
start_date = st.sidebar.date_input("Start Date", value=datetime.today() - timedelta(days=5))
end_date = st.sidebar.date_input("End Date", value=datetime.today())
run_button = st.sidebar.button("▶️ Run Strategy")

# === STRIKE CONSTRUCTION ===
strike_price = strike_base + strike_gap
symbol = f"NIFTY{expiry.upper()}{strike_price}{option_type}"
st.markdown(f"### Selected Option: `{symbol}`")

if run_button:
    if mode == "Backtest":
        st.subheader("📁 Upload Historical Candle CSV")
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success("✅ File loaded")
            trades = run_backtest(df,
                                  capital=capital,
                                  use_heikin_ashi=(candle_type == "Heikin Ashi"),
                                  dynamic_position=dynamic_position,
                                  start_date=start_date,
                                  end_date=end_date)
        else:
            st.error("❌ Please upload a CSV file.")
            trades = pd.DataFrame()

    elif mode == "Forward Test":
        st.info("📡 Fetching live data from Zerodha")
        trades = run_live_forward_test(symbol=symbol, interval=interval, capital=capital)

    if not trades.empty:
        st.subheader("📄 Trades Executed")
        st.dataframe(trades, use_container_width=True)

        pnl_total = trades['pnl'].sum()
        final_cap = trades['capital_after'].iloc[-1]
        st.metric("Net P&L", f"₹{pnl_total:,.2f}")
        st.metric("Final Capital", f"₹{final_cap:,.2f}")

        st.subheader("📈 Capital Over Time")
        cap_chart = alt.Chart(trades).mark_line(point=True).encode(
            x='exit_time:T',
            y='capital_after:Q',
            tooltip=['exit_time', 'capital_after', 'pnl']
        ).properties(height=400)
        st.altair_chart(cap_chart, use_container_width=True)

        csv = trades.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Trades CSV", data=csv, file_name="trades.csv", mime="text/csv")
    else:
        st.warning("⚠️ No trades executed.")


