from flask import Flask, request
import os, requests
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = "bollberg123"
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Bollberg Bot laeuft!"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Falsch", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        text = msg["text"]["body"]
        reply = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "Du bist der freundliche Assistent von Bollberg Personal in Berlin. Du hilfst bei Jobs, Personalvermittlung, Social Media Marketing und Online-Handel. Antworte kurz, freundlich und auf Deutsch."}, {"role": "user", "content": text}]).choices[0].message.content
        requests.post(f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages", headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}, json={"messaging_product": "whatsapp", "to": from_number, "text": {"body": reply}})
    except Exception as e:
        print(e)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
