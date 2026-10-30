from datetime import datetime
import requests
import yfinance as yf

# ================= CONFIGURATION =================
BOT_TOKEN = "9209112895:AAewx1S4iQyKbwj15HELlhw-J5znd78Pe_U"
CHAT_ID = "5781972115"

ASSETS = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN",
}

STOP_LOSS_PCT = 0.005  # 0.5%
TARGET_PCT = 0.012  # 1.2%
# =================================================


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram Error: {e}")


def calculate_rsi(data, window=14):
  delta = data.diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
  rs = gain / loss
  rsi = 100 - (100 / (1 + rs))
  return rsi


def get_atm_strike(price, asset_name):
  """Calculates the At-The-Money (ATM) strike price based on asset type."""
  if "Nifty 50" in asset_name:
    return round(price / 50) * 50
  elif "Bank Nifty" in asset_name:
    return round(price / 100) * 100
  elif "Sensex" in asset_name:
    return round(price / 100) * 100
  return round(price)


def analyze_market():
  today_weekday = datetime.now().weekday()
  if today_weekday >= 5:  # Saturday or Sunday
    print("Aaj weekend hai, market band hai. Bot execution skipped.")
    return

  report = (
      "⚡ *INSTITUTIONAL PRO BOT (EMA + RSI + Volume + ATM)* ⚡\n\n"
      f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
  )

  for name, ticker in ASSETS.items():
    try:
      data = yf.download(
          ticker, period="30d", interval="1d", progress=False
      )
      if len(data) < 20:
        continue

      if hasattr(data.columns, "levels"):
        close_prices = data["Close"][ticker]
        volume_data = data["Volume"][ticker]
      else:
        close_prices = data["Close"]
        volume_data = data["Volume"]

      current_close = float(close_prices.iloc[-1])

      # Pro Indicators
      ema_9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1]
      ema_21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1]
      rsi_series = calculate_rsi(close_prices)
      current_rsi = float(rsi_series.iloc[-1])

      # Volume Spike Filter
      avg_volume = volume_data.rolling(window=20).mean().iloc[-1]
      current_volume = float(volume_data.iloc[-1])
      is_volume_strong = current_volume > avg_volume

      # ATM Strike Calculation
      atm_strike = get_atm_strike(current_close, name)

      # Strict Pro Confluence Logic
      if (
          current_close > ema_9
          and ema_9 > ema_21
          and current_rsi > 55
          and is_volume_strong
      ):
        signal = "🟢 *ULTRA BULLISH (HIGH PROBABILITY BUY)*"
        stop_loss = current_close * (1 - STOP_LOSS_PCT)
        target = current_close * (1 + TARGET_PCT)
        option_hint = f"👉 Watch ATM CE: `{atm_strike} CE`"
      elif (
          current_close < ema_9
          and ema_9 < ema_21
          and current_rsi < 45
          and is_volume_strong
      ):
        signal = "🔴 *ULTRA BEARISH (HIGH PROBABILITY SELL)*"
        stop_loss = current_close * (1 + STOP_LOSS_PCT)
        target = current_close * (1 - TARGET_PCT)
        option_hint = f"👉 Watch ATM PE: `{atm_strike} PE`"
      else:
        signal = "⚪ *SIDEWAYS / WEAK VOLUME (AVOID TRADING)*"
        stop_loss = current_close * (1 - STOP_LOSS_PCT)
        target = current_close * (1 + TARGET_PCT)
        option_hint = "👉 Market Sideways, Avoid Options"

      report += f"*{name}*\n"
      report += f"Signal: {signal}\n"
      report += f"Price: {current_close:.2f} | ATM Strike: {atm_strike}\n"
      report += f"{option_hint}\n"
      report += f"RSI: {current_rsi:.2f} | Vol Spike: {'Yes 🚀' if is_volume_strong else 'No ⚠️'}\n"
      report += f"9 EMA: {ema_9:.2f} | 21 EMA: {ema_21:.2f}\n"
      report += f"Stop Loss: {stop_loss:.2f} | Target: {target:.2f}\n"
      report += "-------------------\n"

    except Exception as e:
      report += f"*{name}*: Error fetching data ({e})\n\n"

  send_telegram_message(report)


if __name__ == "__main__":
  analyze_market()
