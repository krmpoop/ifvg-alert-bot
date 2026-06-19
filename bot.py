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
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval={INTERVAL}&range=1d"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = r.json()
    quotes = data["chart"]["result"][0]["indicators"]["quote"][0]
    opens = quotes["open"]
    highs = quotes["high"]
    lows = quotes["low"]
    closes = quotes["close"]
    return opens, highs, lows, closes

def check_ifvg(opens, highs, lows, closes):
    alerts = []
    for i in range(2, len(closes)):
        if None in [highs[i-2], lows[i], highs[i], lows[i-2]]:
            continue
        # Bullish IFVG
        if lows[i] > highs[i-2]:
            gap_high = lows[i]
            gap_low = highs[i-2]
            msg = (f"🟢 <b>Bullish IFVG - EURUSD 15M</b>\n"
                   f"📍 منطقة الفجوة: {gap_low:.5f} - {gap_high:.5f}\n"
                   f"📈 ابحث عن دخول شراء عند العودة للمنطقة")
            alerts.append(msg)
        # Bearish IFVG
        if highs[i] < lows[i-2]:
            gap_high = lows[i-2]
            gap_low = highs[i]
            msg = (f"🔴 <b>Bearish IFVG - EURUSD 15M</b>\n"
                   f"📍 منطقة الفجوة: {gap_low:.5f} - {gap_high:.5f}\n"
                   f"📉 ابحث عن دخول بيع عند العودة للمنطقة")
            alerts.append(msg)
    return alerts

send_message("✅ بوت IFVG Alert يعمل الآن!\nيراقب EURUSD كل 15 دقيقة")

last_alerts = set()

while True:
    try:
        opens, highs, lows, closes = get_candles()
        alerts = check_ifvg(opens, highs, lows, closes)
        for alert in alerts[-3:]:
            if alert not in last_alerts:
                send_message(alert)
                last_alerts.add(alert)
        if len(last_alerts) > 50:
            last_alerts = set(list(last_alerts)[-20:])
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(900)
