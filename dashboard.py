# dashboard.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# === PAGE SETUP ===
st.set_page_config(page_title="NIFTY Options Paper Trading Dashboard", layout="wide")
st.title("📊 NIFTY Options | Paper Trading Dashboard")

# === SIDEBAR CONTROLS ===
st.sidebar.header("🔧 Strategy Configuration")
mode = st.sidebar.selectbox("Mode", ["Backtest", "Forward Test", "Live (Coming Soon)"])
capital = st.sidebar.number_input("Capital (INR)", value=100000, step=5000)
option_type = st.sidebar.radio("Option Type", ["CE", "PE"])
strike_type = st.sidebar.selectbox("Strike Price", ["ATM", "ATM+50", "ATM-50", "Manual"])
manual_strike = st.sidebar.text_input("Manual Strike Price (if selected above)", value="25500")
expiry_date = st.sidebar.date_input("Expiry Date", value=datetime.today() + timedelta(days=2))

st.sidebar.markdown("---")
run_button = st.sidebar.button("▶️ Start Backtest / Forward Test")
stop_button = st.sidebar.button("⏹️ Stop")

# === BACKTEST CSV UPLOAD ===
if mode == "Backtest":
    st.subheader("📁 Upload Historical 3m Candle CSV")
    uploaded_file = st.file_uploader("Upload 3-minute NIFTY option candle file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV Loaded Successfully")
        st.write(df.head())
        
        # Mock trade signal logic (we'll replace this later)
        df['Signal'] = df['close'].diff().apply(lambda x: "BUY" if x > 2 else ("SELL" if x < -2 else ""))
        trades = df[df['Signal'] != ""]

        st.subheader("📋 Mock Trades (Based on CSV)")
        st.dataframe(trades[['time', 'close', 'Signal']])

        st.subheader("📈 Trade Summary")
        st.metric("Total Trades", len(trades))
        st.metric("Capital Remaining", f"₹{capital:,}")

# === FORWARD TEST PLACEHOLDER ===
elif mode == "Forward Test":
    st.subheader("🚀 Forward Testing Mode (Live Market Hours Only)")
    st.info("This mode will connect to Zerodha Kite API, fetch 3m candles live, and simulate trades.")
    st.warning("Please ensure API keys and tokens are set up in config.")

# === TRADE LOG VIEW ===
st.subheader("📄 Trade History (trades.csv)")
if os.path.exists("data/trades.csv"):
    trade_log = pd.read_csv("data/trades.csv")
    st.dataframe(trade_log.tail(10))
    total_pnl = trade_log['pnl'].sum()
    st.metric("Total P&L", f"₹{total_pnl:,.2f}")
else:
    st.info("No trade log found yet. Run a test to generate trades.")

# === FOOTER ===
st.markdown("---")
st.markdown("Made for 🔁 Backtest, 🚀 Forward Test & 💰 Live Trading with Zerodha | v1.0")
