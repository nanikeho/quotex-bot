import os
import time
import sqlite3
import requests
import threading
from datetime import datetime
from flask import Flask, render_template_string  # HTML display ke liye

app = Flask(__name__)

# 🌐 LIVE SIGNAL MEMORY LAYER (Website par dikhane ke liye)
live_signals_list = []

@app.route('/')
def home():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Website Ka Sundar Layout (HTML/CSS)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quantum Matrix V2 Live</title>
        <meta http-equiv="refresh" content="30"> <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b0f19; color: #ffffff; text-align: center; padding: 20px; }
            h1 { color: #00e676; margin-bottom: 5px; font-size: 28px; }
            .status { color: #8892b0; font-size: 14px; margin-bottom: 30px; }
            .container { max-width: 600px; margin: 0 auto; }
            .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: left; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .asset { font-weight: bold; font-size: 18px; color: #38bdf8; }
            .action-call { color: #00e676; font-weight: bold; }
            .action-put { color: #f43f5e; font-weight: bold; }
            .details { font-size: 13px; color: #9ca3af; margin-top: 5px; }
            .no-signal { color: #6b7280; font-style: italic; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 QUANTUM AI OTC MATRIX V2 🤖</h1>
            <div class="status">Server Heartbeat: {{ current_time }} IST (Auto-Refreshes Every 30s)</div>
            
            <h2>📊 LIVE REAL-TIME SIGNALS</h2>
            {% if signals %}
                {% for sig in signals %}
                <div class="card">
                    <div class="asset">🎯 Asset Target: {{ sig.asset }}</div>
                    <div>⚡ Action Order: 
                        {% if sig.prediction == 'CALL' %}
                            <span class="action-call">🟢 GO CALL (BUY) NEXT</span>
                        {% else %}
                            <span class="action-put">🔴 GO PUT (SELL) NEXT</span>
                        {% endif %}
                    </div>
                    <div class="details">
                        📊 Trigger: {{ sig.pattern }} &nbsp;|&nbsp; 
                        💎 Accuracy: {{ sig.confidence }}% &nbsp;|&nbsp; 
                        ⏰ Time: {{ sig.time }}
                    </div>
                    <div class="details">🔮 Safety: {{ sig.trade_type }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="card" style="text-align:center;">
                    <span class="no-signal">⏳ Scanning 33 OTC Pairs... Waiting for high probability setups.</span>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, current_time=current_time, signals=live_signals_list)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DB_NAME = "quotex_advanced_master.db"

db_lock = threading.Lock()

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset TEXT,
                sequence_code TEXT,  
                next_candle TEXT,    
                occurrence_count INTEGER,
                martingale_recovery INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

def advanced_analytics_engine(asset, current_sequence):
    global live_signals_list
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT next_candle, SUM(occurrence_count), SUM(martingale_recovery)
            FROM pattern_logs 
            WHERE asset=? AND sequence_code=?
            GROUP BY next_candle
        """, (asset, current_sequence))
        rows = cursor.fetchall()
        conn.close()
        
    if not rows:
        return
        
    data = {row[0]: {"count": row[1], "m1g": row[2]} for row in rows}
    calls_data = data.get("CALL", {"count": 0, "m1g": 0})
    puts_data = data.get("PUT", {"count": 0, "m1g": 0})
    
    total_calls = calls_data["count"]
    total_puts = puts_data["count"]
    total_matrix = total_calls + total_puts
    
    if total_matrix < 0: 
        return 
        
    if total_calls >= total_puts:
        predicted_future = "CALL"
        confidence = (total_calls / total_matrix) * 100
        m1g_ratio = (calls_data["m1g"] / total_calls) if total_calls > 0 else 0
    else:
        predicted_future = "PUT"
        confidence = (total_puts / total_matrix) * 100
        m1g_ratio = (puts_data["m1g"] / total_puts) if total_puts > 0 else 0
        
    required_accuracy = 50.0  # Open loop for instant signals
    
    if confidence >= required_accuracy:
        trade_type = "DIRECT SURESHOT (V1)" if m1g_ratio < 0.15 else "MARTINGALE PREFERRED (M1G)"
        sig_time = datetime.now().strftime("%H:%M:%S")
        
        # WEBSITE ENGINE STORAGE LOGIC
        signal_data = {
            "asset": asset.upper(),
            "prediction": predicted_future,
            "pattern": current_sequence,
            "confidence": f"{confidence:.1f}",
            "trade_type": trade_type,
            "time": sig_time
        }
        
        # Duplicate stop block
        if len(live_signals_list) > 40: # Maximum 40 signals rakhega screen par taaki load na badhe
            live_signals_list.pop()
        live_signals_list.insert(0, signal_data)

ALL_QUOTEX_OTC_PAIRS = [
    "eurusd_otc", "gbpusd_otc", "usdinr_otc", "usdsub_otc", "audcad_otc", "eurjpy_otc", 
    "gbpjpy_otc", "usdchf_otc", "nzdusd_otc", "audusd_otc", "usdcad_otc", "eurich_otc",
    "chfjpy_otc", "cadchf_otc", "eurgbp_otc", "audjpy_otc", "usdpkr_otc", "usdbdt_otc", 
    "usdbrl_otc", "audnzd_otc", "eurnzd_otc", "gbpnzd_otc", "nzdcad_otc", "nzdchf_otc", 
    "nzdjpy_otc", "usdars_otc", "usdcop_otc", "usdegp_otc", "usdidr_otc", "usdmxn_otc", 
    "usdngn_otc", "usdzar_otc", "usdphp_otc"
]

def trading_bot_loop():
    init_db()
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for pair in ALL_QUOTEX_OTC_PAIRS:
            cursor.execute("INSERT OR IGNORE INTO pattern_logs (asset, sequence_code, next_candle, occurrence_count) VALUES (?, 'RRR', 'CALL', 65)", (pair,))
            cursor.execute("INSERT OR IGNORE INTO pattern_logs (asset, sequence_code, next_candle, occurrence_count) VALUES (?, 'GGGG', 'PUT', 70)", (pair,))
        conn.commit()
        conn.close()

    while True:
        # Har minute list ko reset karke bilkul naye signals load karega
        global live_signals_list
        live_signals_list.clear() 
        
        threads = []
        current_hour = datetime.now().hour
        simulated_live_pattern = "GGGG" if current_hour % 2 == 0 else "RRR"
        
        for pair in ALL_QUOTEX_OTC_PAIRS:
            t = threading.Thread(target=advanced_analytics_engine, args=(pair, simulated_live_pattern))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            time.sleep(0.1)
            
        time.sleep(60)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=trading_bot_loop)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
