# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from trade_engine import run_backtest, run_live_forward_test

st.set_page_config(page_title="📊 NIFTY Options Dashboard", layout="wide")
st.title("📊 NIFTY Options | Heikin Ashi Strategy")

mode = st.sidebar.selectbox("Mode", ["Backtest", "Forward Test"])
capital = st.sidebar.number_input("Capital (INR)", value=100000, step=5000)

# === Manual File Upload for Backtesting ===
if mode == "Backtest":
    uploaded_file = st.file_uploader("📁 Upload 3-minute NIFTY option CSV file", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.lower() for c in df.columns]

        if all(col in df.columns for col in ['time', 'open', 'high', 'low', 'close']):
            st.success("✅ CSV loaded")
            st.dataframe(df.head())
            trades = run_backtest(df, capital=capital)
        else:
            st.error("❌ CSV must contain: time, open, high, low, close")
            trades = pd.DataFrame()
    else:
        trades = pd.DataFrame()

# === Live Forward Test (Zerodha) ===
elif mode == "Forward Test":
    symbol = st.text_input("Enter Trading Symbol (e.g., NIFTY25JUL25500CE)", value="NIFTY25JUL25500CE")
    if st.button("🚀 Run Live Forward Test"):
        with st.spinner("Fetching live OHLC data from Zerodha..."):
            trades = run_live_forward_test(symbol=symbol, capital=capital)
        if trades.empty:
            st.warning("No trades triggered from live data.")
        else:
            st.success("✅ Live data processed")

else:
    trades = pd.DataFrame()

# === Show Results ===
if not trades.empty:
    st.subheader("📄 Trade Log")
    st.dataframe(trades)

    st.subheader("📈 Capital Over Time")
    import altair as alt
    chart = alt.Chart(trades).mark_line(point=True).encode(
        x='exit_time:T',
        y='capital_after:Q',
        tooltip=['exit_time', 'capital_after', 'pnl']
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)

    st.metric("💰 Net P&L", f"₹{trades['pnl'].sum():,.2f}")
    st.metric("📊 Final Capital", f"₹{trades['capital_after'].iloc[-1]:,.2f}")
else:
    st.info("Run a test to view trade results.")

st.markdown("---")
st.markdown("📌 Strategy: Heikin Ashi | 3-min | Entry on Green | Exit on Red or 20% Drawdown")

