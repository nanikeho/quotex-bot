import websocket
import json
import time
import numpy as np
from collections import deque
import requests
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8754386975:AAHMQqCWiZlR7PW-YfEMYXmfweEZrVo3KFw"
TELEGRAM_CHAT_ID = "5016643207"
ASSET = "EUR_USD_OTC"
QUOTEX_WS_URL = "wss://ws.quotex.com/socket"

# Strategy Parameters (Tuned for 1-Minute OTC)
MIN_PAYOUT = 0.80
CONFIDENCE_THRESHOLD = 0.75
SIGNAL_COOLDOWN = 60  # Seconds between signals
LOOKBACK_PERIOD = 50  # Number of candles to analyze

class QuotexCandleMatchBot:
    def __init__(self):
        self.api_url = QUOTEX_WS_URL
        self.asset = ASSET
        self.ticks = deque(maxlen=LOOKBACK_PERIOD * 2)
        self.ws = None
        self.payout = 0.85
        self.ema_9 = 0
        self.ema_21 = 0
        self.atr = 0.0002
        self.rsi = 50
        self.vol_state = "NEUTRAL"
        self.trend = "NEUTRAL"
        self.signal = "NO-TRADE"
        self.confidence = 0.0
        self.reason = ""
        self.last_signal_time = 0
        self.candle_data = []

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Telegram Message Sent: {message[:50]}...")
            else:
                logger.error(f"❌ Telegram Error: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Telegram Send Failed: {e}")

    def connect(self):
        logger.info(f"🚀 Connecting to Quotex for {self.asset}...")
        self.ws = websocket.WebSocketApp(
            self.api_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "tick" in data:
                price = float(data["tick"]["price"])
                timestamp = data["tick"]["timestamp"]
                self.ticks.append({"price": price, "timestamp": timestamp})
                
            if "payout" in data:
                self.payout = float(data["payout"])

            if len(self.ticks) > LOOKBACK_PERIOD:
                self.update_candle_data()
                self.update_analysis()
                self.generate_signal()
                self.maybe_send_signal()
                
        except Exception as e:
            logger.error(f"⚠️ Data parsing error: {e}")

    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.info("🔌 Disconnected. Reconnecting in 5 seconds...")
        time.sleep(5)
        self.connect()

    def update_candle_data(self):
        recent_prices = [tick["price"] for tick in list(self.ticks)[-20:]]
        if len(recent_prices) >= 2:
            self.candle_data = {
                "high": max(recent_prices),
                "low": min(recent_prices),
                "close": recent_prices[-1],
                "rsi_values": self.calculate_rsi_series(recent_prices)
            }

    def calculate_ema(self, prices, period):
        if len(prices) < period:
            return 0
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    def calculate_atr(self, prices):
        if len(prices) < 2:
            return 0
        tr = np.abs(np.diff(prices))
        return np.mean(tr)

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices)
        seed = deltas[:period]
        seed_ups = np.sum([delta for delta in seed if delta > 0])
        seed_downs = np.sum([abs(delta) for delta in seed if delta < 0])
        
        for i in range(period, len(deltas)):
            delta = deltas[i]
            if delta > 0:
                seed_ups += delta
                seed_downs -= abs(deltas[i-period])
            else:
                seed_ups -= abs(deltas[i-period])
                seed_downs += abs(delta)
        
        rs = seed_ups / seed_downs if seed_downs != 0 else float('inf')
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_rsi_series(self, prices, period=14):
        if len(prices) < period + 1:
            return []
        deltas = np.diff(prices)
        seed = deltas[:period]
        seed_ups = np.sum([delta for delta in seed if delta > 0])
        seed_downs = np.sum([abs(delta) for delta in seed if delta < 0])
        
        rsi_series = []
        for i in range(period, len(deltas)):
            delta = deltas[i]
            if delta > 0:
                seed_ups += delta
                seed_downs -= abs(deltas[i-period])
            else:
                seed_ups -= abs(deltas[i-period])
                seed_downs += abs(delta)
            
            rs = seed_ups / seed_downs if seed_downs != 0 else float('inf')
            rsi = 100 - (100 / (1 + rs))
            rsi_series.append(rsi)
        return rsi_series

    def detect_divergence(self):
        if len(self.candle_data.get("rsi_values", [])) < 3:
            return None
            
        rsi_vals = self.candle_data["rsi_values"]
        prices = [tick["price"] for tick in list(self.ticks)[-5:]]
        
        if prices[-1] < prices[-2] and rsi_vals[-1] > rsi_vals[-2]:
            return "BULLISH"
            
        if prices[-1] > prices[-2] and rsi_vals[-1] < rsi_vals[-2]:
            return "BEARISH"
            
        return None

    def update_analysis(self):
        prices = [tick["price"] for tick in list(self.ticks)[-LOOKBACK_PERIOD:]]
        if not prices:
            return
        
        self.ema_9 = self.calculate_ema(prices, 9)
        self.ema_21 = self.calculate_ema(prices, 21)
        self.atr = self.calculate_atr(prices)
        self.rsi = self.calculate_rsi(prices)
        
        if self.atr < 0.00015:
            self.vol_state = "CHOP"
        elif self.atr > 0.00030:
            self.vol_state = "TREND"
        else:
            self.vol_state = "NEUTRAL"
            
        if self.ema_9 > self.ema_21:
            self.trend = "UP"
        elif self.ema_9 < self.ema_21:
            self.trend = "DOWN"
        else:
            self.trend = "NEUTRAL"

    def generate_signal(self):
        latest_price = self.ticks[-1]["price"] if self.ticks else 0
        payout = self.payout
        divergence = self.detect_divergence()
        
        if payout < MIN_PAYOUT:
            self.signal = "NO-TRADE"
            self.confidence = 0.0
            self.reason = "Low Payout"
            return

        if divergence == "BULLISH" and self.trend != "DOWN":
            self.signal = "CALL"
            self.confidence = 0.85
            self.reason = "Bullish Divergence (Candle Match)"
            return
        if divergence == "BEARISH" and self.trend != "UP":
            self.signal = "PUT"
            self.confidence = 0.85
            self.reason = "Bearish Divergence (Candle Match)"
            return

        if self.vol_state == "TREND" and self.trend == "UP":
            self.signal = "CALL"
            self.confidence = 0.80
            self.reason = "Trend Up (High Vol)"
            return
        if self.vol_state == "TREND" and self.trend == "DOWN":
            self.signal = "PUT"
            self.confidence = 0.80
            self.reason = "Trend Down (High Vol)"
            return

        if self.vol_state == "CHOP":
            if self.trend == "UP":
                self.signal = "CALL"
                self.confidence = 0.70
                self.reason = "Choppy Uptrend"
            elif self.trend == "DOWN":
                self.signal = "PUT"
                self.confidence = 0.70
                self.reason = "Choppy Downtrend"
            else:
                self.signal = "NO-TRADE"
                self.confidence = 0.0
                self.reason = "Choppy Neutral"
            return

        self.signal = "NO-TRADE"
        self.confidence = 0.0
        self.reason = "No Clear Signal"

    def maybe_send_signal(self):
        current_time = time.time()
        if self.confidence >= CONFIDENCE_THRESHOLD and (current_time - self.last_signal_time > SIGNAL_COOLDOWN):
            if self.signal != "NO-TRADE":
                message = (
                    f"🔔 *OTC CANDLE MATCH SIGNAL* 🔔\n"
                    f"📊 *Asset:* {self.asset}\n"
                    f"⏱️ *Timeframe:* 1 Minute\n"
                    f"📈 *Price:* {self.ticks[-1]['price']:.5f}\n"
                    f"💰 *Payout:* {self.payout:.2%}\n"
                    f"📉 *ATR:* {self.atr:.6f}\n"
                    f"🔄 *Volatility:* {self.vol_state}\n"
                    f"📊 *Trend:* {self.trend}\n"
                    f"📉 *RSI:* {self.rsi:.2f}\n"
                    f"✅ *SIGNAL:* *{self.signal}*\n"
                    f"🎯 *Confidence:* {self.confidence:.2f}\n"
                    f"📝 *Reason:* {self.reason}\n"
                    f"⏰ *Time:* {time.strftime('%H:%M:%S')}"
                )
                self.send_telegram_message(message)
                self.last_signal_time = current_time
                logger.info(f"📤 Signal Sent: {self.signal} ({self.confidence:.2f})")

    def run(self):
        logger.info("🚀 Starting Quotex OTC Candle Match Bot (1-Minute Timeframe)...")
        self.connect()

if __name__ == "__main__":
    bot = QuotexCandleMatchBot()
    bot.run()
        
