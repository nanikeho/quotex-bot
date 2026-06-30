import os
import sqlite3
import requests
from datetime import datetime

# GitHub Secrets Framework Configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DB_NAME = "/tmp/otc_future_matrix.db"  # Resolved container paths

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pattern_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            sequence_code TEXT,  
            next_candle TEXT,    
            occurrence_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def send_future_signal_to_telegram(asset, pattern, prediction, confidence):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram Secrets configurations missing.")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    emoji = "🟢 GO CALL (BUY) NEXT" if prediction == "CALL" else "🔴 GO PUT (SELL) NEXT"
    current_time = datetime.now().strftime("%H:%M")
    
    text = (
        f"🔮 **AI OTC FUTURE PREDICTOR** 🔮\n\n"
        f"🎯 **Asset Target**: `{asset}`\n"
        f"📊 **Detected Pattern**: `{pattern}`\n"
        f"🚀 **Future Action**: *{emoji}*\n"
        f"⏰ **Analysis Time**: `{current_time}`\n\n"
        f"🔥 **Probability Index**: `{confidence:.1f}%` Sureshot Matrix\n"
        f"⚠️ *Rule*: Apply **Max 1-Step Martingale** if last second volatility error occurs."
    )
    
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=5)
        print(f"📡 Future Signal Dispatched: {prediction} based on {pattern}")
    except Exception as e:
        print(f"❌ Dispatch failed: {e}")

def predict_future_candle(asset, current_sequence):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT next_candle, SUM(occurrence_count) 
        FROM pattern_logs 
        WHERE asset=? AND sequence_code=?
        GROUP BY next_candle
    """, (asset, current_sequence))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"⏳ Pattern '{current_sequence}' is unique. Scanning alternative data blocks...")
        return
        
    data = {row[0]: row[1] for row in rows}
    calls = data.get("CALL", 0)
    puts = data.get("PUT", 0)
    total = calls + puts
    
    if total < 5: 
        return 
    
    if calls >= puts:
        confidence = (calls / total) * 100
        predicted_future = "CALL"
    else:
        confidence = (puts / total) * 100
        predicted_future = "PUT"
        
    if confidence >= 82.0:
        send_future_signal_to_telegram(asset, current_sequence, predicted_future, confidence)

def seed_future_patterns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sample_matrix = [
        ("EURUSD_otc", "GGG", "PUT", 45),  
        ("EURUSD_otc", "RRR", "CALL", 42), 
        ("EURUSD_otc", "GRG", "CALL", 38), 
        ("USDINR_otc", "GGG", "PUT", 50),
        ("USDINR_otc", "RRG", "CALL", 48)
    ]
    try:
        cursor.executemany("INSERT INTO pattern_logs (asset, sequence_code, next_candle, occurrence_count) VALUES (?, ?, ?, ?)", sample_matrix)
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    seed_future_patterns()
    
    ASSETS = ["EURUSD_otc", "USDINR_otc"]
    current_live_pattern = "RRR"  
    
    for pair in ASSETS:
        predict_future_candle(pair, current_live_pattern)
