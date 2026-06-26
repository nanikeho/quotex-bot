import os
import time
import json
import requests
import urllib3

# SSL Error bypass ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TEST_PAIRS = ["EURUSD_OTC", "GBPUSD_OTC", "AUDUSD_OTC"]

def send_telegram_signal(pair, direction):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    emoji = "🟩 CALL (UP)" if direction == "UP" else "🟥 PUT (DOWN)"
    
    message = (
        f"🤖 *QUOTEX GITHUB BOT ACTIVE* 🤖\n\n"
        f"🌐 *Asset/Pair:* `{pair}`\n"
        f"📊 *Strategy:* `Fast Price Action`\n"
        f"📈 *Signal:* *{emoji}*\n\n"
        f"✅ *Status:* Connection is working flawlessly on GitHub!"
    )
    
    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID),
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, verify=False, timeout=10)
        if response.status_code == 200:
            print(f"👉 SUCCESS: Signal sent to Telegram for {pair}!")
        else:
            print(f"❌ Telegram API Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    print("--- STARTING GITHUB BOT DIAGNOSTIC ---")
    print(f"Target Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Bina folder dependancy ke direct loop chala kar signals test karna
    pair_index = 0
    # Test ke liye hum loop ko 3 baar chalayenge taaki workflow complete ho sake
    for _ in range(3):
        current_pair = TEST_PAIRS[pair_index]
        direction = "UP" if pair_index % 2 == 0 else "DOWN"
        
        send_telegram_signal(current_pair, direction)
        
        pair_index = (pair_index + 1) % len(TEST_PAIRS)
        time.sleep(5)  # 5 second ka gap pairs ke beech mein
        
    print("--- ALL TEST SIGNALS PROCESSED ---")

if __name__ == "__main__":
    main()
    
