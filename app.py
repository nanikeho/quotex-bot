import os
import time
import threading
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
# Apne Telegram bot ka token aur chat/channel ID yahan daalein
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8754386975:AAGpsRdk84bP7dFQTiEPF2JmkjQHNhPVPPU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5016643207")
ASSET_NAME = "EUR/USD OTC"

# Quotex price element class name 
PRICE_CSS_SELECTOR = ".chart-current-price-class" 

class QuotexTelegramBot:
    def __init__(self):
        self.ticks = []
        self.candles = pd.DataFrame(columns=['open', 'high', 'low', 'close'])
        self.last_candle_minute = int(time.time() // 60)
        self.driver = self.init_browser()

    def init_browser(self):
        print("Starting Headless Browser...")
        
        # Chrome ko system PATH mein add karna taaki Selenium usko detect kar sake
        os.environ["PATH"] += os.pathsep + "/opt/render/project/free/chrome/opt/google/chrome"
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Render par Chrome binary ki specific location
        options.binary_location = "/opt/render/project/free/chrome/opt/google/chrome/google-chrome"
        
        # Selenium 4.10+ in-built manager use karega
        driver = webdriver.Chrome(options=options)
        
        # Domain name updated to avoid net::ERR_NAME_NOT_RESOLVED
        driver.get("https://quotex.com/en/trade")
        print("Browser Started successfully!")
        return driver

    def send_telegram_signal(self, direction, price, ema9, ema21, rsi):
        emoji = "🟢 CALL (UP)" if direction == "CALL" else "🔴 PUT (DOWN)"
        message = (
            f"⚡ <b>QUOTEX 1-MIN SIGNAL</b> ⚡\n\n"
            f"📊 <b>Asset:</b> {ASSET_NAME}\n"
            f"🎯 <b>Signal:</b> {emoji}\n"
            f"💲 <b>Entry Price:</b> {price}\n"
            f"⏳ <b>Expiry:</b> 1 Minute\n\n"
            f"📈 <b>RSI:</b> {round(rsi, 2)}\n"
            f"📉 <b>EMA Cross:</b> 9 EMA ({round(ema9, 5)}) | 21 EMA ({round(ema21, 5)})\n"
            f"🛡️ <b>Strategy:</b> EMA Cross + BB Breakout + RSI"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"[{time.strftime('%H:%M:%S')}] Signal Sent: {direction} at {price}")
            else:
                print(f"Telegram API Error: {response.text}")
        except Exception as e:
            print(f"Telegram Request Error: {e}")

    def get_realtime_price(self):
        """Scrape price directly from HTML for 100% accuracy"""
        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, PRICE_CSS_SELECTOR) 
            price_text = price_element.text.replace(',', '')
            return float(price_text)
        except Exception:
            return None

    def build_candle_and_analyze(self):
        current_minute = int(time.time() // 60)
        
        if current_minute > self.last_candle_minute and len(self.ticks) > 0:
            open_p = self.ticks[0]
            high_p = max(self.ticks)
            low_p = min(self.ticks)
            close_p = self.ticks[-1]
            
            new_candle = pd.DataFrame([{
                'open': open_p, 'high': high_p, 'low': low_p, 'close': close_p
            }])
            
            self.candles = pd.concat([self.candles, new_candle], ignore_index=True)
            self.ticks = []
            self.last_candle_minute = current_minute
            
            if len(self.candles) > 50:
                self.candles = self.candles.iloc[-50:]
                
            self.analyze_strategy()

    def analyze_strategy(self):
        if len(self.candles) < 22:
            return

        df = self.candles.copy()
        
        df['ema_9'] = ta.ema(df['close'], length=9)
        df['ema_21'] = ta.ema(df['close'], length=21)
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        bbands = ta.bbands(df['close'], length=20, std=2)
        df['bb_upper'] = bbands['BBL_20_2.0']
        df['bb_lower'] = bbands['BBL_20_2.0']

        current = df.iloc[-1]
        
        if (current['ema_9'] > current['ema_21']) and (current['close'] > current['bb_upper']) and (50 < current['rsi'] < 70):
            self.send_telegram_signal("CALL", current['close'], current['ema_9'], current['ema_21'], current['rsi'])
            
        elif (current['ema_9'] < current['ema_21']) and (current['close'] < current['bb_lower']) and (30 < current['rsi'] < 50):
            self.send_telegram_signal("PUT", current['close'], current['ema_9'], current['ema_21'], current['rsi'])

    def run(self):
        print("Bot Started. Scraping ticks from Quotex...")
        
        # --- STARTUP TEST MESSAGE ---
        try:
            test_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(test_url, data={
                "chat_id": TELEGRAM_CHAT_ID, 
                "text": "🟢 <b>Quotex Math Bot is LIVE!</b>\nScanning the market 24/7 for high accuracy setups...",
                "parse_mode": "HTML"
            })
            print("Startup message sent to Telegram.")
        except Exception as e:
            print(f"Failed to send startup message: {e}")
        # ----------------------------

        while True:
            price = self.get_realtime_price()
            if price:
                self.ticks.append(price)
            
            self.build_candle_and_analyze()
            time.sleep(0.5)

# --- DUMMY FLASK SERVER FOR RENDER PORT BINDING ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Quotex Telegram Bot is Running 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Flask server ko alag thread mein start karna taaki Render port timeout error na de
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # Main trading bot ko start karna
    bot = QuotexTelegramBot()
    bot.run()
    
