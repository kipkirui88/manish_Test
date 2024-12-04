import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from kwiz import Kwiz, Button, Row, Section, Action, ButtonEncoder
import requests
import base64
import logging
import json

app = Flask(__name__)

os.environ["TOKEN"] = "EAAI7KQfphY0BOyvENKJQZCqPc27OeNSsPz32lZARFwaw8lLrRwAl0sottUBNEXIJHETXfFCUjSJlgi4qefWmt8XXAHTeZCUl3kCgHLpfBwm5EP6VOM3W9haJKDLPpMyvLhf2XZC6RCUw5CZB9fA6JGrGAUG3RVJojQZByE2mD5JyAX5v1S80sJUyfXdefJ4fdCqQZDZD"
os.environ["PHONE_NUMBER_ID"] = "210203168844024"

VERIFY_TOKEN = "koechbot"
kwiz = Kwiz(os.getenv("TOKEN"), phone_number_id=os.getenv("PHONE_NUMBER_ID"))

# M-Pesa Access Token
def get_access_token():
    consumer_key = '9uvkU2GwA7E5ygZrfHrAbXX9A1Af8w5bXUO8o1IOeaVo55h9'
    consumer_secret = 'd1DPs2ZjFjDrcMY1Fqh26xeWPQzHRVZXcaWrGkA9fJJGYeE7LP5s2tjtDGDWwgZX'
    credentials = base64.b64encode((consumer_key + ':' + consumer_secret).encode()).decode()
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {
        'Authorization': 'Basic ' + credentials,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()['access_token']

@app.route("/", methods=["GET"])
def verify():
    try:
        if request.method == 'GET':
            if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
                if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
                    return "Verification token mismatch", 403
                return request.args['hub.challenge'], 200
    except Exception as e:
        logger.error(f"Error: {e}")
    return '200 OK HTTPS.'

# Payment processing
def perform_stk_push(phone_number, amount):
    business_short_code = '174379'
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    transaction_type = 'CustomerPayBillOnline'
    account_reference = 'BookShop'
    callback_url = 'https://c971-2c0f-fe38-2212-23eb-3d7c-ef6-d5b9-240a.ngrok-free.app/callback_url'
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

    payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': transaction_type,
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': business_short_code,
        'PhoneNumber': phone_number,
        'CallBackURL': callback_url,
        'AccountReference': account_reference,
        'TransactionDesc': 'Assignment Purchase'
    }

    access_token = get_access_token()
    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to log the transaction details
def log_transaction(data):
    try:
        # Check if CallbackMetadata and Item exist
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        callback_metadata = stk_callback.get('CallbackMetadata', {})
        items = callback_metadata.get('Item', [])

        # Log the relevant fields, check if they exist first
        merchant_request_id = stk_callback.get('MerchantRequestID', 'N/A')
        checkout_request_id = stk_callback.get('CheckoutRequestID', 'N/A')
        result_code = stk_callback.get('ResultCode', 'N/A')
        result_desc = stk_callback.get('ResultDesc', 'N/A')

        amount = items[0].get('Value', None) if len(items) > 0 else None
        mpesa_receipt_number = items[1].get('Value', None) if len(items) > 1 else None
        balance = items[2].get('Value', None) if len(items) > 2 else None
        transaction_date = items[3].get('Value', None) if len(items) > 3 else None
        phone_number = items[4].get('Value', None) if len(items) > 4 else None

        # Format the log message
        log_message = f"MerchantRequestID: {merchant_request_id}, CheckoutRequestID: {checkout_request_id}, ResultCode: {result_code}, ResultDesc: {result_desc}, Amount: {amount}, MpesaReceiptNumber: {mpesa_receipt_number}, Balance: {balance}, TransactionDate: {transaction_date}, PhoneNumber: {phone_number}\n"

        # Log to a file (or use a logging framework)
        with open("transactions_log.txt", "a") as log_file:
            log_file.write(log_message)

    except Exception as e:
        logging.error(f"Error in log_transaction: {str(e)}")

@app.route('/callback_url', methods=['POST'])
def mpesa_callback():
    try:
        # Get the callback data from the request
        callback_data = request.get_json()

        # Log the raw callback data for debugging purposes
        with open("raw_callback_data.txt", "a") as raw_log_file:
            raw_log_file.write(json.dumps(callback_data) + "\n")
        
        # Log the transaction details
        log_transaction(callback_data)

        # Respond to M-Pesa to acknowledge the callback
        return "OK", 200

    except Exception as e:
        logging.error(f"Error handling callback: {str(e)}")
        return "Error", 500


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    changed_field = kwiz.changed_field(data)

    if changed_field == "messages":
        new_message = kwiz.get_mobile(data)

        if new_message:
            mobile = kwiz.get_mobile(data)
            name = kwiz.get_name(data)
            message_type = kwiz.get_message_type(data)

            if message_type == "text":
                message = kwiz.get_message(data)
                logger.info("Message: %s", message)
                # Sending the button in response to a text message
                rows = [
                    Row("PP1", "PP1", ""),
                    Row("PP2", "PP2", ""),
                    Row("Grade 1", "Grade 1", ""), 
                    Row("Grade 2", "Grade 2", ""), 
                    Row("Grade 3", "Grade 3", ""), 
                    Row("Grade 4", "Grade 4", ""), 
                    Row("Grade 5", "Grade 5", ""), 
                    Row("Grade 6", "Grade 6", ""), 
                    Row("Grade 7", "Grade 7", ""), 
                    Row("Grade 8", "Grade 8", ""), 
                ]
                sections = [Section("", rows)]
                action = Action("Select Grade:", sections)
                button = Button(
                    f"📚Hello {name}, Welcome to Our BookShop! 📚",
                    "We are here to make holiday assignments easy to access for your child. Please choose a grade to continue.",
                    "",
                    action
                )
                data = ButtonEncoder().encode(button)
                kwiz.send_list(data, mobile)

            elif message_type == "interactive":
                message_response = kwiz.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")

                if message_id == "PP1":
                    # Ask for payment for PP1
                    ask_payment(mobile, "PP1")

                elif message_id == "PP2":
                    # Ask for payment for PP2
                    ask_payment(mobile, "PP2")
                
                elif message_id == "Yes":
                    # Retrieve the selected grade and amount from the user's data
                    user_data = user_selections.get(mobile)
                    if user_data:
                        grade = user_data["grade"]
                        amount = user_data["amount"]
                        
                        # Proceed with STK Push for the correct amount
                        logger.info(f"User {mobile} responded with 'Yes' for {grade}. Proceeding with STK Push of KSh {amount}.")
                        perform_stk_push(mobile, amount)  # Pass the dynamic amount
                    else:
                        logger.error(f"No payment details found for {mobile}")


            else:
                logger.info(f"{mobile} sent {message_type} ")
                logger.info(data)
        else:
            delivery = kwiz.get_delivery(data)
            if delivery:
                logger.info(f"Message : {delivery}")
            else:
                logger.info("No new message")

    return "ok"


# In-memory storage to keep track of selected grades and amounts
user_selections = {}

# Map assignment to its respective price
assignment_prices = {
    "PP1": 20, 
    "PP2": 20,
    "Grade 1": 20,
    "Grade 6": 30,
}

def ask_payment(mobile, grade):
    # Get the price for the selected grade
    amount = assignment_prices.get(grade, 0)  # Default to 0 if grade not found
    if amount == 0:
        logger.error(f"Invalid grade selected: {grade}")
        return

    # Store the selected grade and amount for the user
    user_selections[mobile] = {"grade": grade, "amount": amount}

    # Send payment request to user
    payment_message = f"To receive the {grade} document, Please select 'Yes' to pay KSh {amount}."
    
    # Defining buttons for payment options
    buttons = [
        {"id": "Yes", "title": "Yes"},
        {"id": "No", "title": "No"}
    ]

    # Sending the message with buttons
    kwiz.send_button(mobile, payment_message, buttons=buttons)
    logger.info(f"Requested payment of KSh {amount} for {grade} from {mobile}")



def PP1(mobile):
    document_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    response = kwiz.send_document(document=document_link, recipient_id=mobile, caption="PP1 Assignment!")
    send_lists_after_message(mobile, response)

def PP2(mobile):
    document_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    response = kwiz.send_document(document=document_link, recipient_id=mobile, caption="PP2 Assignment!")
    send_lists_after_message(mobile, response)

def send_lists_after_message(mobile, response):
    # Function to send the next set of messages after sending the document
    rows = [
        Row("More Assignments", "More", ""),
        Row("Help", "Help", ""),
    ]
    sections = [Section("", rows)]
    action = Action("What would you like to do next?", sections)
    button = Button(
        f"📚Thank you for your payment! 📚", 
        "Your document has been sent. What would you like to do next?", 
        "", 
        action
    )
    data = ButtonEncoder().encode(button)
    kwiz.send_list(data, mobile)


if __name__ == '__main__':
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=7020)
