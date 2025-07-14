# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from trade_engine import run_backtest

# === PAGE SETUP ===
st.set_page_config(page_title="NIFTY Options Dashboard", layout="wide")
st.title("📊 NIFTY Options | Paper/Live/Backtest Dashboard")

# === SIDEBAR CONTROLS ===
st.sidebar.header("🔧 Strategy Configuration")

mode = st.sidebar.selectbox("Mode", ["Backtest", "Forward Test", "Live (Coming Soon)"])
candle_type = st.sidebar.radio("Candle Type", ["Heikin Ashi", "Normal"])
timeframe = st.sidebar.selectbox("Timeframe", ["1min", "3min", "5min", "15min", "1hr"])
capital = st.sidebar.number_input("Capital (INR)", value=100000, step=5000)
dynamic_position = st.sidebar.toggle("Dynamic Position Sizing", value=True)
option_type = st.sidebar.radio("Option Type", ["CE", "PE"])
strike_selection = st.sidebar.selectbox("Strike Price", ["ATM", "ATM+50", "ATM-50", "Manual"])
manual_strike = st.sidebar.text_input("Manual Strike (only if selected above)", value="25500")
expiry_date = st.sidebar.date_input("Expiry Date", value=datetime.today() + timedelta(days=2))

st.sidebar.divider()
emergency_stop = st.sidebar.toggle("🛑 Emergency Stop", value=False)
start_button = st.sidebar.button("▶️ Start Strategy")
stop_button = st.sidebar.button("⏹️ Stop Strategy")

# === BACKTEST SECTION ===
if mode == "Backtest":
    st.subheader("📁 Upload Historical CSV")
    uploaded_file = st.file_uploader("Upload 3-minute NIFTY option candle file", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.lower() for c in df.columns]
        
        if not all(col in df.columns for col in ['time', 'open', 'high', 'low', 'close']):
            st.error("❌ CSV must contain: time, open, high, low, close")
        else:
            st.success("✅ CSV validated")
            st.dataframe(df.head(), use_container_width=True)

            if start_button:
                trades = run_backtest(
                    df,
                    capital=capital,
                    use_heikin_ashi=(candle_type == "Heikin Ashi"),
                    dynamic_position=dynamic_position
                )

                if trades.empty:
                    st.warning("⚠️ No trades found in this config.")
                else:
                    st.subheader("📄 Trade Log")
                    st.dataframe(trades, use_container_width=True)

                    st.subheader("📈 Trade Summary")
                    st.metric("Total Trades", len(trades))
                    st.metric("Final Capital", f"₹{trades['capital_after'].iloc[-1]:,.2f}")
                    st.metric("Net P&L", f"₹{trades['pnl'].sum():,.2f}")

                    # Download button
                    csv = trades.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", data=csv, file_name="nifty_trades.csv", mime="text/csv")

# === FORWARD TEST SECTION ===
elif mode == "Forward Test":
    st.subheader("🚀 Forward Test (Beta)")
    st.info("This mode will use live 3-min candle data to simulate trades.")
    st.warning("Zerodha Kite integration required. API config will be used after login setup.")

# === LIVE SECTION ===
elif mode == "Live (Coming Soon)":
    st.subheader("💡 Live Trading Mode")
    st.info("Live trading automation will be enabled after Zerodha integration.")

# === FOOTER ===
st.divider()
st.markdown("Made with ❤️ for Algo Trading | Zerodha + Heikin Ashi + Dynamic Position Sizing")



