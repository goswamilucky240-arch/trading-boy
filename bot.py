from datetime import datetime
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

print("Ultimate Institutional Master Bot v6.0 (Foolproof Edition) shuru ho gaya hai...")

# ================= CONFIGURATION =================
BOT_TOKEN = "9209112895:AAGQl48kaijFVZq1LpL6PeUgdL90r_1sKTo"
CHAT_ID = "5781972115"

ASSETS = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN"
}
# =================================================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    # Retry mechanism to ensure message is never lost due to network glitch
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Telegram message successfully bhej diya gaya hai.")
                return True
            else:
                print(f"Telegram Error Response: {response.text}")
        except Exception as e:
            print(f"Telegram Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    return False

def analyze_market_and_generate_signal(symbol, ticker_name):
    try:
        # Fetching historical candle data (60 days for deep professional calculation)
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
        # 1. Exponential Moving Averages (EMA 9 & EMA 21)
        ema_9 = close_prices.ewm(span=9, adjust=False).mean()
        ema_21 = close_prices.ewm(span=21, adjust=False).mean()

        # 2. RSI (Relative Strength Index - 14 Period) with foolproof division protection
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50) # Fallback to neutral if needed

        # 3. ATR (Average True Range) for Dynamic Volatility-based Stop Loss
        high_low = high_prices - low_prices
        high_close = np.abs(high_prices - close_prices.shift())
        low_close = np.abs(low_prices - close_prices.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=14).mean()

        # Current Values (Latest Candle)
        current_price = float(close_prices.iloc[-1])
        curr_ema9 = float(ema_9.iloc[-1])
        curr_ema21 = float(ema_21.iloc[-1])
        curr_rsi = float(rsi.iloc[-1])
        curr_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else (current_price * 0.008)
        
        avg_volume = float(volume.rolling(window=10).mean().iloc[-1])
        current_volume = float(volume.iloc[-1])

        # --- ULTIMATE PROFESSIONAL DECISION ENGINE ---
        signal = "HOLD / AVOID TRADE 🛡️"
        reason = "Market sideways hai ya direction clear nahi hai. Faltu trade lene se bachein."
        emoji = "⏳"

        # 1. STRONG BUY / CALL SIGNAL CONDITION
        if curr_ema9 > curr_ema21 and curr_rsi < 68 and current_price > curr_ema9:
            if current_volume >= (avg_volume * 0.75):
                signal = "🟢 STRONG BUY (CALL) SIGNAL"
                emoji = "🚀"
                reason = (f"• EMA 9 ({curr_ema9:.2f}) > EMA 21 ({curr_ema21:.2f}) (Bullish Trend)\n"
                          f"• RSI ({curr_rsi:.1f}) safe zone mein hai (Not Overbought)\n"
                          f"• Volume support strong hai.")

        # 2. STRONG SELL / PUT (SHORT) SIGNAL CONDITION
        elif curr_ema9 < curr_ema21 and curr_rsi > 32:
            signal = "🔴 STRONG SELL / PUT (SHORT) SIGNAL"
            emoji = "📉"
            reason = (f"• EMA 9 ({curr_ema9:.2f}) < EMA 21 ({curr_ema21:.2f}) (Bearish Trend)\n"
                      f"• Momentum sellers ke control mein hai (RSI: {curr_rsi:.1f})")

        # 3. OVERBOUGHT AVOIDANCE (DO NOT BUY)
        elif curr_rsi >= 72:
            signal = "⛔ DO NOT BUY (OVERBOUGHT ZONE)"
            emoji = "🛑"
            reason = f"• RSI ({curr_rsi:.1f}) 72 se upar hai. Market mein sharp correction aa sakta hai. Nayi buying bilkul na karein!"

        # 4. OVERSOLD REVERSAL WAIT
        elif curr_rsi <= 28:
            signal = "⛔ OVERSOLD ZONE / WAIT FOR BOUNCE"
            emoji = "🛑"
            reason = f"• RSI ({curr_rsi:.1f}) 28 se niche hai. Panic mein sell na karein, reversal ya bounce ka wait karein."

        # Professional Dynamic ATR-based Risk Management (Smart SL & Target)
        sl_price = current_price - (1.5 * curr_atr)
        target_price = current_price + (2.5 * curr_atr)

        # Formatting Report Message for Mobile / Telegram
        report = (
            f"{emoji} **Master Analysis: {symbol}**\n\n"
            f"📊 **Action Decision:** *{signal}*\n"
            f"💰 **Current Price:** `{current_price:.2f}`\n"
            f"📈 **Technical Indicators:**\n"
            f"  - EMA 9: `{curr_ema9:.2f}` | EMA 21: `{curr_ema21:.2f}`\n"
            f"  - RSI (14): `{curr_rsi:.2f}` | ATR: `{curr_atr:.2f}`\n\n"
            f"🔍 **Professional Logic / Reason:**\n{reason}\n\n"
            f"🛡️ **Dynamic Risk Management (ATR-based):**\n"
            f"  - Smart Stop Loss: `₹{sl_price:.2f}`\n"
            f"  - Smart Target: `₹{target_price:.2f}`\n"
            f"-----------------------------------"
        )
        return report

    except Exception as e:
        return f"❌ Error analyzing {symbol}: {str(e)}"

def main():
    print("Master Bot v6.0 analysis shuru ho raha hai...")
    header_msg = "🤖 **Institutional Master Bot v6.0 (Final)**\n*Foolproof Network & ATR Engine Active*\n\n"
    send_telegram_message(header_msg)

    for symbol, ticker in ASSETS.items():
        print(f"{symbol} ({ticker}) ka data analyze kiya ja raha hai...")
        analysis_result = analyze_market_and_generate_signal(symbol, ticker)
        send_telegram_message(analysis_result)

if __name__ == "__main__":
    main()
