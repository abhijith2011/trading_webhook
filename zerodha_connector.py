# zerodha_connector.py
import os
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import pandas as pd

# === Load environment variables ===
load_dotenv()
API_KEY = os.getenv("Z_API_KEY")
API_SECRET = os.getenv("Z_API_SECRET")

kite = KiteConnect(api_key=API_KEY)

# === Manual login flow ===
def login():
    print("Go to the following URL and get your request token:")
    print(kite.login_url())
    request_token = input("Paste request token here: ").strip()
    session = kite.generate_session(request_token, api_secret=API_SECRET)
    kite.set_access_token(session["access_token"])
    with open("access_token.txt", "w") as f:
        f.write(session["access_token"])
    print("✅ Login successful! Access token saved.")

# === Use access token to connect ===
def get_kite():
    if not os.path.exists("access_token.txt"):
        raise Exception("❌ access_token.txt not found. Run login() first.")
    with open("access_token.txt", "r") as f:
        token = f.read().strip()
    kite.set_access_token(token)
    return kite

# === Get instrument token from symbol ===
def get_instrument_token(trading_symbol, exchange="NFO"):
    kite = get_kite()
    instruments = kite.instruments(exchange)
    for inst in instruments:
        if inst["tradingsymbol"] == trading_symbol:
            return inst["instrument_token"]
    raise ValueError(f"❌ Instrument token not found for: {trading_symbol}")

# === Get OHLC data ===
def get_ohlc_data(token=None, interval="3minute", days=5, trading_symbol="NIFTY25JUL25500CE"):
    kite = get_kite()
    if token is None:
        token = get_instrument_token(trading_symbol)

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    data = kite.historical_data(token, from_date, to_date, interval)
    df = pd.DataFrame(data)
    df.rename(columns={"date": "time"}, inplace=True)
    return df

# === Get list of nearby strike prices ===
def get_strike_list(option_type="CE", atm_price=25500, gap=50, count=3, expiry="25JUL"):
    # Example output: ['NIFTY25JUL25450CE', 'NIFTY25JUL25500CE', ...]
    strikes = []
    for i in range(-count, count + 1):
        strike = atm_price + (i * gap)
        symbol = f"NIFTY{expiry}{strike}{option_type.upper()}"
        strikes.append(symbol)
    return strikes
