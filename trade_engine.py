# trade_engine.py
import pandas as pd
import math
from zerodha_connector import get_ohlc_data

CAPITAL = 100000
LOT_SIZE = 75
COMMISSION = 70
DRAWDOWN_LIMIT = 0.80  # 20% max loss

def compute_heikin_ashi(df):
    ha_df = df.copy()
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [(df['open'][0] + df['close'][0]) / 2]

    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_df['HA_Close'][i-1]) / 2)

    ha_df['HA_Open'] = ha_open
    ha_df['HA_Green'] = ha_df['HA_Close'] > ha_df['HA_Open']
    ha_df['HA_Red'] = ha_df['HA_Close'] < ha_df['HA_Open']
    ha_df['New_Green'] = ha_df['HA_Green'] & (~ha_df['HA_Green'].shift(1).fillna(False))
    ha_df['New_Red'] = ha_df['HA_Red'] & (~ha_df['HA_Red'].shift(1).fillna(False))

    return ha_df

def run_backtest(df, capital=CAPITAL, use_heikin_ashi=True, dynamic_position=True):
    df = compute_heikin_ashi(df) if use_heikin_ashi else df
    trades = []
    position = None
    entry_price = 0
    entry_time = ''
    qty = 0
    peak_capital = capital
    serial = 1

    for i, row in df.iterrows():
        price = row['close']
        time = row['time']

        if (row.get('New_Green', False) if use_heikin_ashi else row.get('Signal', '') == 'BUY') and position is None:
            lot_price = price * LOT_SIZE
            lots = math.floor(capital / lot_price) if dynamic_position else 1
            if lots == 0:
                continue
            qty = lots * LOT_SIZE
            entry_price = price
            entry_time = time
            position = 'LONG'

        elif (row.get('New_Red', False) if use_heikin_ashi else row.get('Signal', '') == 'SELL') and position == 'LONG':
            exit_price = price
            pnl = (exit_price - entry_price) * qty - COMMISSION
            capital += pnl
            trades.append({
                'S.No': serial,
                'time': entry_time,
                'exit_time': time,
                'entry': entry_price,
                'exit': exit_price,
                'qty': qty,
                'side': 'BUY',
                'pnl': pnl,
                'capital_after': capital
            })
            serial += 1
            position = None

        if capital < (peak_capital * DRAWDOWN_LIMIT) and position is not None:
            exit_price = price
            pnl = (exit_price - entry_price) * qty - COMMISSION
            capital += pnl
            trades.append({
                'S.No': serial,
                'time': entry_time,
                'exit_time': time,
                'entry': entry_price,
                'exit': exit_price,
                'qty': qty,
                'side': 'BUY (STOP)',
                'pnl': pnl,
                'capital_after': capital
            })
            serial += 1
            position = None

        peak_capital = max(capital, peak_capital)

    return pd.DataFrame(trades)

def run_live_forward_test(symbol="NIFTY25JUL25500CE", interval="3minute", days=1, capital=CAPITAL):
    df = get_ohlc_data(token=None, interval=interval, days=days)  # Token will be mapped inside get_ohlc_data
    if df.empty:
        return pd.DataFrame()
    return run_backtest(df, capital=capital, use_heikin_ashi=True, dynamic_position=True)


