import requests
import time

TOKEN = "8856305475:AAFlG3b--fC9ULWCfRWEMsg1XvjQScPVe4A"
CHAT_ID = "523347455"
SYMBOL = "EURUSD=X"
INTERVAL = "15m"

def send_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def get_candles():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval={INTERVAL}&range=2d"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = r.json()
    quotes = data["chart"]["result"][0]["indicators"]["quote"][0]
    return quotes["open"], quotes["high"], quotes["low"], quotes["close"]

def check_ifvg(highs, lows):
    alerts = []
    for i in range(4, len(lows)):
        if None in [highs[i-4], lows[i-4], highs[i-2], lows[i-2], highs[i], lows[i]]:
            continue

        # FVG صاعد تكوّن ثم امتلأ = Bearish IFVG
        bull_fvg = lows[i-2] > highs[i-4]
        if bull_fvg:
            fvg_low = highs[i-4]
            fvg_high = lows[i-2]
            if lows[i] <= fvg_high:
                msg = (f"🔴 <b>Bearish IFVG - EURUSD 15M</b>\n"
                       f"📍 منطقة: {fvg_low:.5f} - {fvg_high:.5f}\n"
                       f"📉 FVG صاعد امتلأ — ابحث عن دخول بيع")
                alerts.append(msg)

        # FVG هابط تكوّن ثم امتلأ = Bullish IFVG
        bear_fvg = highs[i-2] < lows[i-4]
        if bear_fvg:
            fvg_low = highs[i-2]
            fvg_high = lows[i-4]
            if highs[i] >= fvg_low:
                msg = (f"🟢 <b>Bullish IFVG - EURUSD 15M</b>\n"
                       f"📍 منطقة: {fvg_low:.5f} - {fvg_high:.5f}\n"
                       f"📈 FVG هابط امتلأ — ابحث عن دخول شراء")
                alerts.append(msg)

    return alerts

send_message("✅ بوت IFVG Alert يعمل الآن!\nيراقب EURUSD كل 15 دقيقة")

last_alerts = set()

while True:
    try:
        opens, highs, lows, closes = get_candles()
        alerts = check_ifvg(highs, lows)
        for alert in alerts[-3:]:
            if alert not in last_alerts:
                send_message(alert)
                last_alerts.add(alert)
        if len(last_alerts) > 50:
            last_alerts = set(list(last_alerts)[-20:])
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(900)
