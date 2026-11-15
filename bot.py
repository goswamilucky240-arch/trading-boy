from datetime import datetime
import requests
import yfinance as yf
import pandas as pd
import numpy as np

print("Bot script shuru ho gayi hai - Advanced Trading Engine Activated")

# ================= CONFIGURATION =================
BOT_TOKEN = "9209112895:AAGQl48kaijFVZq1LpL6PeUgdL90r_1sKTo"
CHAT_ID = "5781972115"

ASSETS = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN"
}

# Advanced Risk Management Parameters
STOP_LOSS_PCT = 0.005  # 0.5% Stop Loss
TARGET_PCT = 0.012     # 1.2% Target
# =================================================

def send_telegram_message(message):
    print("Telegram message bhejne ki koshish ki ja rahi hai")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print("Telegram Response:", response.text)
    except Exception as e:
        print("Telegram Error:", e)

def analyze_market_and_generate_signal(symbol, ticker_name):
    try:
        # Fetching historical candle data (1-day interval, last 60 days for accurate EMA & RSI)
        data = yf.download(ticker_name, period="60d", interval="1d", progress=False)
        
        if data.empty or len(data) < 30:
            return f"⚠️ {symbol}: Data insufficient for professional analysis."

        # Flatten multi-index columns if returned by yfinance
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        close_prices = data['Close']
        high_prices = data['High']
        low_prices = data['Low']
        volume = data['Volume']

        # --- PROFESSIONAL TECHNICAL INDICATORS CALCULATIONS ---
        # 1. Exponential Moving Averages (EMA 9 & EMA 21) for Trend Direction
        ema_9 = close_prices.ewm(span=9, adjust=False).mean()
        ema_21 = close_prices.ewm(span=21, adjust=False).mean()

        # 2. RSI (Relative Strength Index - 14 Period) for Overbought/Oversold
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Current Values (Latest Candle)
        current_price = float(close_prices.iloc[-1])
        prev_price = float(close_prices.iloc[-2])
        curr_ema9 = float(ema_9.iloc[-1])
        curr_ema21 = float(ema_21.iloc[-1])
        curr_rsi = float(rsi.iloc[-1])
        avg_volume = float(volume.rolling(window=10).mean().iloc[-1])
        current_volume = float(volume.iloc[-1])

        # --- ADVANCED PROFESSIONAL DECISION ENGINE ---
        signal = "HOLD / AVOID TRADE 🛡️"
        reason = "Market sideways hai ya momentum clear nahi hai. Risk lene se bachein."
        emoji = "⏳"

        # Bullish Crossover & Momentum Check (BUY CONDITION)
        if curr_ema9 > curr_ema21 and curr_rsi < 65 and current_price > curr_ema9:
            if current_volume > (avg_volume * 0.8): # Volume confirmation
                signal = "🚀 STRONG BUY SIGNAL"
                emoji = "🟢"
                reason = (f"• EMA 9 ({curr_ema9:.2f}) EMA 21 ({curr_ema21:.2f}) ke اوپر है (Bullish Trend).\n"
                          f"• RSI ({curr_rsi:.1f}) healthy zone mein hai (Not Overbought).\n"
                          f"• Volume support strong hai.")

        # Bearish Crossover & Breakdown Check (SELL / SHORT CONDITION)
        elif curr_ema9 < curr_ema21 and curr_rsi > 35:
            signal = "⚠️ STRONG SELL / EXIT SIGNAL"
            emoji = "🔴"
            reason = (f"• EMA 9 ({curr_ema9:.2f}) EMA 21 ({curr_ema21:.2f}) ke niche cross kar gaya hai (Bearish Trend).\n"
                      f"• Momentum sellers ke control mein hai (RSI: {curr_rsi:.1f}).")

        # Overbought / Oversold Avoidance (DO NOT TRADE CONDITION)
        elif curr_rsi > 75:
            signal = "⛔ DO NOT BUY (OVERBOUGHT ZONE)"
            emoji = "🛑"
            reason = f"• RSI ({curr_rsi:.1f}) 75 se upar hai. Market mein sharp pullback ya correction aa sakta hai. Nayi buying bilkul na karein!"
        elif curr_rsi < 25:
            signal = "⛔ DO NOT SELL / WAIT FOR REVERSAL"
            emoji = "🛑"
            reason = f"• RSI ({curr_rsi:.1f}) 25 se niche hai (Oversold). Panic mein sell na karein, bounce-back ka wait kareین."

        # Risk Management Levels Calculation
        sl_price = current_price * (1 - STOP_LOSS_PCT)
        target_price = current_price * (1 + TARGET_PCT)

        # Formatting Report Message
        report = (
            f"{emoji} **Market Analysis: {symbol}**\n\n"
            f"📊 **Action Decision:** *{signal}*\n"
            f"💰 **Current Price:** `{current_price:.2f}`\n"
            f"📈 **Technical Indicators:**\n"
            f"  - EMA 9: `{curr_ema9:.2f}` | EMA 21: `{curr_ema21:.2f}`\n"
            f"  - RSI (14): `{curr_rsi:.2f}`\n\n"
            f"🔍 **Professional Logic / Reason:**\n{reason}\n\n"
            f"🛡️ **Suggested Risk Management:**\n"
            f"  - Stop Loss (0.5%): `₹{sl_price:.2f}`\n"
            f"  - Target (1.2%): `₹{target_price:.2f}`\n"
            f"-----------------------------------"
        )
        return report

    except Exception as e:
        return f"❌ Error analyzing {symbol}: {str(e)}"

def main():
    print("Trading bot analysis shuru ho raha hai...")
    header_msg = "🤖 **Institutional Pro Trading Bot v3.0**\n*Advanced Multi-Indicator & Price Action Engine Active*\n\n"
    send_telegram_message(header_msg)

    for symbol, ticker in ASSETS.items():
        print(f"{symbol} ({ticker}) ka data fetch kiya ja raha hai...")
        analysis_result = analyze_market_and_generate_signal(symbol, ticker)
        send_telegram_message(analysis_result)

if __name__ == "__main__":
    main()
