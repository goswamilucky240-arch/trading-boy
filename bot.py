from datetime import datetime
import requests
import yfinance as yf

print("Bot script shuru ho gayi hai")

# ================= CONFIGURATION =================
BOT_TOKEN = "9209112895:AAewx154iQyKbwj15HEL1hw-J5znd78Pe_U"
CHAT_ID = "5781972115"

ASSETS = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN"
}

STOP_LOSS_PCT = 0.005  # 0.5%
TARGET_PCT = 0.012     # 1.2%
# ==================================================

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
        if response.status_code == 200:
            print("Telegram message safaltapoorvak bhej diya gaya hai!")
        else:
            print(f"Telegram Error Response: {response.text}")
    except Exception as e:
        print(f"Telegram Exception Error: {e}")

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def run_trading_bot():
    print("Trading bot analysis shuru ho raha hai...")
    
    # Test ke taur par shuruat mein hi Telegram alert bhejna taaki pata chale bot active hai
    send_telegram_message("🚀 *Institutional Pro Bot:* Bot safaltapoorvak run ho gaya hai aur market data analyze kar raha hai!")

    for name, ticker in ASSETS.items():
        try:
            print(f"{name} ({ticker}) ka data fetch kiya ja raha hai...")
            df = yf.download(ticker, period="5d", interval="1d", progress=False)
            
            if df.empty:
                print(f"{name} ka data nahi mila.")
                continue
                
            # Multi-index ya single index handle karne ke liye
            if 'Close' in df.columns:
                close_prices = df['Close']
            else:
                close_prices = df.iloc[:, 0]
                
            current_price = float(close_prices.iloc[-1])
            print(f"{name} ki current price: {current_price}")
            
            # Simple alert message
            msg = f"📊 *Market Update*\n*Asset:* {name}\n*Current Price:* {current_price}"
            send_telegram_message(msg)
            
        except Exception as e:
            print(f"{name} ko process karne mein error aayi: {e}")

if __name__ == "__main__":
    run_trading_bot()
