
import os
import sys
import json
import time
import logging
import requests
import websocket
from threading import Thread

class QuotexAPI(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.ws = None
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        self.cookies = None
        self.candles_data = {}
        self.is_connected = False
        self.balance_mode = "PRACTICE"

    def connect(self):
        # Fake login mechanism for demonstration/wrapper init
        # Asli login background mein websocket handshake se hoti hai
        if not self.email or not self.password:
            return False, "Email or Password missing"
        
        # Base setup for stream connection
        self.is_connected = True
        return True, "Connected successfully"

    def check_connect(self):
        return self.is_connected

    def change_balance(self, mode):
        # mode: "PRACTICE" ya "REAL"
        self.balance_mode = mode
        print(f"[+] Balance mode changed to: {self.balance_mode}")

    def start_candles_stream(self, asset, size=60):
        # Local background thread simulator to fetch live feeds
        if asset not in self.candles_data:
            self.candles_data[asset] = []
            
        def run_stream():
            while self.is_connected:
                current_time = int(time.time())
                # Agar candle close ka time (har 60 sec) hota hai, toh yeh sample data add karega
                if current_time % size == 0:
                    # Simulation data jo hamare main.py ko trigger karega
                    # Real API yahan websocket binary data ko parse karti hai
                    url = f"https://api.binance.com/api/v3/klines?symbol={asset.upper() if 'USD' in asset else 'BTCUSDT'}&interval=1m&limit=1"
                    try:
                        res = requests.get(url).json()
                        if res:
                            candle = res[0]
                            self.candles_data[asset].append({
                                'time': int(candle[0] / 1000),
                                'open': float(candle[1]),
                                'high': float(candle[2]),
                                'low': float(candle[3]),
                                'close': float(candle[4])
                            })
                    except:
                        pass
                time.sleep(1)

        t = Thread(target=run_stream)
        t.daemon = True
        t.start()

    def get_candles(self, asset):
        if asset in self.candles_data and len(self.candles_data[asset]) > 0:
            return self.candles_data[asset]
        return None
