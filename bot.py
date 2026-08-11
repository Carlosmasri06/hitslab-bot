import os, urllib.request, urllib.parse

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT  = os.environ["TELEGRAM_CHAT_ID"]

msg = "🤖 HITS LAB bot: vivo y corriendo desde GitHub. El cerebro empieza a tomar forma."
data = urllib.parse.urlencode({"chat_id": CHAT, "text": msg}).encode()
urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data)
print("Mensaje enviado a Telegram.")
