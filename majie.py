from flask import Flask, request
import requests

app = Flask(__name__)

# Replace with your verification token
VERIFICATION_TOKEN = "EAAI7KQfphY0BO1FQGHvaWZB4dpKTPtS9LFTOjzW0AR2Jrzj1OolZBgqlzypLVFCWZBLTWPr2JhyR6813Hcw9JxOm8gU1UmvZAl6jMI3F7TZBFufM4QfumClgYBDNdfNA8jzIGvZAvWeuqO3tqPpr8uJ7lyswCEcFGcLjg8FCy13FTZB9tL1Cr5ZAu8PZAQS2GOSrPjJCRFnpU4U4GdZBqjqHvfjZBrlvJrhWVzpQ2bWAt0xvgAZD"
# Replace with your phone number ID
PHONE_NUMBER_ID = "210203168844024"
# Replace with the mobile number you want to send messages to
USER_MOBILE_NUMBER = "254713812781"

@app.route('/')
def index():
    return "Hello, Flask is running!"

# Function to send a message
def send_msg(msg):
    headers = {
        'Authorization': f'Bearer {VERIFICATION_TOKEN}',
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': USER_MOBILE_NUMBER,
        'type': 'text',
        "text": {
            "body": msg
        }
    }
    response = requests.post(f'https://graph.facebook.com/v13.0/{PHONE_NUMBER_ID}/messages', headers=headers, json=json_data)
    print(response.text)

# Webhook for handling incoming requests
@app.route('/receive_msg', methods=['POST', 'GET'])
def webhook():
    # Verification step for Facebook webhook
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if request.args.get("hub.verify_token") == 'koechbot':
                return request.args['hub.challenge'], 200
            return "Verification token mismatch", 403

    # Handling incoming message
    if request.method == 'POST':
        res = request.get_json()
        print(res)
        try:
            # Extract the incoming message
            incoming_msg = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            print(f"Received message: {incoming_msg}")
            
            # Check if the incoming message is "hi"
            if incoming_msg.lower() == "hi":
                send_msg("Hello! How can I help you?")
            else:
                send_msg("Thank you for the response.")
        except KeyError:
            pass
        return '200 OK HTTPS.'

if __name__ == "__main__":
    app.run(debug=True)
