import os
import time
import threading
import asyncio
import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from flask import Flask
from quotexpy import Quotex
import undetected_chromedriver as uc
import logging
import random
import signal
import sys

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quotex_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- ENVIRONMENT VARIABLES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8754386975:AAGpsRdk84bP7dFQTiEPF2JmkjQHNhPVPPU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5016643207")
QUOTEX_EMAIL = os.environ.get("QUOTEX_EMAIL", "nanikeho@gmail.com")
QUOTEX_PASS = os.environ.get("QUOTEX_PASS", "78907890@Ho")

# Multi-Pair Configuration
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", 
    "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc"
]

# Cloud Optimization Flags
CLOUD_OPTIMIZATION = {
    "single_process": True,
    "disable_gpu": True,
    "disable_software_rasterizer": True,
    "window_size": "1920,1080",
    "disable_extensions": True,
    "disable_dev_shm_usage": True,
    "no_sandbox": True
}

class CloudQuotexBot:
    def __init__(self):
        self.client = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASS, host="quotex.com")
        self.active_trades = {}  # {pair: timestamp}
        self.is_running = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def _patch_chrome_for_cloud(self):
        """Monkey patch Chrome options for cloud stability."""
        original_init = uc.Chrome.__init__
        
        def patched_init(self, *args, **kwargs):
            options = kwargs.get('options')
            if not options:
                options = uc.ChromeOptions()
            
            # Core Stability Flags
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--headless=new')
            
            # Memory Optimization Flags
            if CLOUD_OPTIMIZATION["single_process"]:
                options.add_argument('--single-process')
            if CLOUD_OPTIMIZATION["disable_gpu"]:
                options.add_argument('--disable-gpu')
            if CLOUD_OPTIMIZATION["disable_software_rasterizer"]:
                options.add_argument('--disable-software-rasterizer')
            if CLOUD_OPTIMIZATION["disable_extensions"]:
                options.add_argument('--disable-extensions')
            
            # Window Size
            options.add_argument(f'--window-size={CLOUD_OPTIMIZATION["window_size"]}')
            
            # Disable unnecessary features
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            
            kwargs['options'] = options
            original_init(self, *args, **kwargs)
        
        uc.Chrome.__init__ = patched_init

    async def connect_to_quotex(self):
        """Robust connection with retry logic."""
        logger.info(f"Connecting to Quotex API (Attempt {self.reconnect_attempts + 1})...")
        
        for attempt in range(self.max_reconnect_attempts):
            try:
                check, reason = await asyncio.wait_for(self.client.connect(), timeout=60.0)
                if check:
                    logger.info("✅ Successfully connected to Quotex!")
                    self.reconnect_attempts = 0
                    return True
                else:
                    logger.warning(f"❌ Connection failed: {reason}")
                    await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff
            except asyncio.TimeoutError:
                logger.error("❌ API Connection Timeout: Chrome hung.")
                await asyncio.sleep(5 * (attempt + 1))
            except Exception as e:
                logger.error(f"❌ API Connection Error: {e}")
                await asyncio.sleep(5 * (attempt + 1))
        
        logger.critical("❌ Max reconnect attempts reached. Exiting.")
        self.is_running = False
        return False

    def generate_chart(self, df, pair, direction):
        """Memory-efficient chart generation."""
        try:
            plt.figure(figsize=(10, 5))
            plt.style.use('dark_background')
            
            plt.plot(df.index, df['close'], label='Price', color='#ffffff', linewidth=2)
            plt.plot(df.index, df['ema_9'], label='9 EMA', color='#00ffff', linestyle='--')
            plt.plot(df.index, df['ema_21'], label='21 EMA', color='#ff00ff', linestyle='--')
            plt.plot(df.index, df['bb_upper'], label='BB Upper', color='#ff3333', alpha=0.7)
            plt.plot(df.index, df['bb_lower'], label='BB Lower', color='#33ff33', alpha=0.7)
            
            plt.fill_between(df.index, df['bb_upper'], df['bb_lower'], color='grey', alpha=0.1)
            
            title_color = '#00ff00' if direction == 'CALL' else '#ff0000'
            plt.title(f"{pair.replace('_', '/')} - {direction} SIGNAL", color=title_color, fontsize=14, fontweight='bold')
            plt.legend(loc="upper left")
            plt.grid(color='gray', linestyle=':', alpha=0.3)
            plt.xticks([])  
            
            image_path = f"{pair}_signal.png"
            plt.savefig(image_path, bbox_inches='tight', dpi=100)
            plt.close()
            return image_path
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return None

    def send_telegram_alert(self, pair, direction, price, rsi, image_path):
        """Telegram alert with rate-limit protection."""
        emoji = "🟢 CALL (UP)" if direction == "CALL" else "🔴 PUT (DOWN)"
        caption = (
            f"⚡ <b>QUOTEX CLOUD ENGINE</b> ⚡\n\n"
            f"📊 <b>Asset:</b> {pair.replace('_', ' ').upper()}\n"
            f"🎯 <b>Direction:</b> {emoji}\n"
            f"💲 <b>Entry Price:</b> {price}\n"
            f"⏳ <b>Timeframe:</b> 1 Minute\n\n"
            f"📈 <b>RSI Level:</b> {round(rsi, 2)}\n"
            f"🛡️ <b>Setup:</b> EMA + BB + RSI Confluence\n\n"
            f"<i>Trade on next candle open.</i>"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        try:
            # Add jitter to avoid rate limits
            time.sleep(random.uniform(0.1, 0.3))
            
            with open(image_path, 'rb') as photo:
                payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}
                response = requests.post(url, data=payload, files={"photo": photo}, timeout=10)
                if response.status_code == 200:
                    logger.info(f"🚀 Signal Sent: {pair} {direction}")
                else:
                    logger.warning(f"Telegram API Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Telegram Error: {e}")
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    async def fetch_and_analyze(self, pair):
        """Analyze a single pair with timeout guard."""
        # Check cooldown
        if pair in self.active_trades:
            if time.time() - self.active_trades[pair] < 60:
                return
        
        try:
            logger.debug(f"Scanning {pair}...")
            
            candles = await asyncio.wait_for(self.client.get_candles(pair, 60, 50, time.time()), timeout=10.0)
            if not candles:
                logger.warning(f"No data for {pair}")
                return
                
            df = pd.DataFrame(candles)
            if 'time' in df.columns:
                df = df.rename(columns={'time': 'datetime'})
            df['close'] = df['close'].astype(float)
            
            df['ema_9'] = ta.ema(df['close'], length=9)
            df['ema_21'] = ta.ema(df['close'], length=21)
            df['rsi'] = ta.rsi(df['close'], length=14)
            
            bbands = ta.bbands(df['close'], length=20, std=2)
            df['bb_upper'] = bbands['BBL_20_2.0']
            df['bb_lower'] = bbands['BBL_20_2.0']

            current = df.iloc[-1]
            
            if (current['ema_9'] > current['ema_21']) and (current['close'] > current['bb_upper']) and (50 < current['rsi'] < 70):
                logger.info(f"🟢 CALL: {pair}")
                img_path = self.generate_chart(df.tail(30), pair, "CALL")
                if img_path:
                    self.send_telegram_alert(pair, "CALL", current['close'], current['rsi'], img_path)
                    self.active_trades[pair] = time.time()
                    
            elif (current['ema_9'] < current['ema_21']) and (current['close'] < current['bb_lower']) and (30 < current['rsi'] < 50):
                logger.info(f"🔴 PUT: {pair}")
                img_path = self.generate_chart(df.tail(30), pair, "PUT")
                if img_path:
                    self.send_telegram_alert(pair, "PUT", current['close'], current['rsi'], img_path)
                    self.active_trades[pair] = time.time()
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout: {pair}")
        except Exception as e:
            logger.error(f"Error {pair}: {e}")

    async def run(self):
        # Apply Chrome patch
        self._patch_chrome_for_cloud()
        
        connected = await self.connect_to_quotex()
        if not connected:
            return

        logger.info("🚀 Cloud Quotex Bot Online!")
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                data={"chat_id": TELEGRAM_CHAT_ID, "text": "🟢 <b>Quotex Cloud Engine Online</b>\nAll systems operational.", "parse_mode": "HTML"},
                timeout=10
            )
        except:
            pass

        while self.is_running:
            try:
                # Scan pairs concurrently
                tasks = [self.fetch_and_analyze(pair) for pair in OTC_PAIRS]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                logger.info(f"Cycle complete. {len(OTC_PAIRS)} pairs scanned.")
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(5)

# --- FLASK HEALTH CHECK ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Quotex Cloud Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Start Flask in background
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    # Start Async Bot
    bot = CloudQuotexBot()
    
    # Graceful shutdown
    def handle_shutdown(signum, frame):
        logger.info("Shutting down...")
        bot.is_running = False
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    asyncio.run(bot.run())
