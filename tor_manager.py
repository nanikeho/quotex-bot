import socks
import socket
import requests
from stem import Signal
from stem.control import Controller

def new_tor_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="dadgpt666")
            controller.signal(Signal.NEWNYM)
            print("🆕 New Tor IP assigned.")
    except:
        print("⚠️ Failed to rotate IP. Using current.")

def start_tor():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    new_tor_ip()
