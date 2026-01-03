from flask import Flask, request, jsonify
import os
import pickle

# ==========================
# Загрузка базы пользователей
# ==========================

DATA_FILE = "users.pkl"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_users(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

users = load_users()

# ==========================
# IPN SECRET KEY (из Render)
# ==========================

IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY")

# ==========================
# Flask app
# ==========================

app = Flask(__name__)

@app.route("/webhook/nowpayments", methods=["POST"])
def nowpayments_webhook():
    data = request.json

    # Проверка IPN ключа
    if data.get("ipn_secret") != IPN_SECRET_KEY:
        return jsonify({"error": "Invalid IPN secret"}), 403

    payment_status = data.get("payment_status")

    if payment_status == "finished":
        try:
            user_id = int(data["order_id"])      # Telegram ID
            amount = float(data["price_amount"]) # Сумма платежа
        except:
            return jsonify({"error": "Invalid data"}), 400

        if user_id not in users:
            users[user_id] = {
                "balance": 0,
                "currency": "USD"
            }

        users[user_id]["balance"] += amount
        save_users(users)

        print(f"✅ Payment OK | User {user_id} | +{amount}")

    return jsonify({"status": "ok"})

# ==========================
# Start server (Render)
# ==========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
