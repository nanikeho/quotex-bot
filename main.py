import os
import time
import json
import requests
import urllib3
from quotexapi.stable_api import Quotex

# SSL Warnings ko band karne ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# GitHub Secrets se variables load karna
EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 5 Sahi Assets/Pairs ki list (Real + OTC)
PAIRS = ["EURUSD", "GBPUSD", "EURUSD_OTC", "GBPUSD_OTC", "AUDUSD_OTC"]

def send_telegram_signal(pair, direction):
    """Telegram par clean aur attractive signal bhejne ke liye function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    emoji = "🟢 CALL (UP)" if direction == "call" else "🔴 PUT (DOWN)"
    
    message = (
        f"📊 *QUOTEX REAL-TIME SIGNAL* 📊\n\n"
        f"🌐 *Asset/Pair:* `{pair}`\n"
        f"🎯 *Action:* {emoji}\n"
        f"⏳ *Expiry:* `1 MINUTE`\n"
        f"✅ *Status:* Safe Trade Setup"
    )
    
    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID),
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, verify=False, timeout=10)
        if response.status_code == 200:
            print(f"🚀 Signal sent successfully for {pair}!")
        else:
            print(f"❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error while sending Telegram: {e}")

def main():
    print("--- QUOTEX TELEGRAM BOT STARTED ON GITHUB ACTIONS ---")
    
    # Quotex API Initialize aur Login
    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    
    if not check:
        print(f"❌ Quotex Login Failed! Reason: {reason}")
        return
        
    print("✅ Quotex Account Connected Successfully!")
    
    # Loop chalu karke pairs par indicator check karna
    # GitHub workflow test ke liye yeh pehle round mein hi instant test signals trigger karega
    for pair in PAIRS:
        print(f"Analyzing market structure for {pair}...")
        
        # Ek sample signal generator logic (RSI/Moving Average ya Mock Test)
        # Test ke liye hum dummy data fetch karke instant alert bhej rahe hain
        direction = "call" if "USD" in pair else "put"
        
        # Telegram par signal bhejna
        send_telegram_signal(pair, direction)
        time.sleep(2) # Rate limit se bachne ke liye 2 second ka gap
        
    print("--- ALL TEST SIGNALS SENT SUCCESSFULLY ---")

if __name__ == "__main__":
    main()
    
