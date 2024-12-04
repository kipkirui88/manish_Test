import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from kwiz import Kwiz, Button, Row, Section, Action, ButtonEncoder
import requests

app = Flask(__name__)

os.environ["TOKEN"] = "EAAI7KQfphY0BOyvENKJQZCqPc27OeNSsPz32lZARFwaw8lLrRwAl0sottUBNEXIJHETXfFCUjSJlgi4qefWmt8XXAHTeZCUl3kCgHLpfBwm5EP6VOM3W9haJKDLPpMyvLhf2XZC6RCUw5CZB9fA6JGrGAUG3RVJojQZByE2mD5JyAX5v1S80sJUyfXdefJ4fdCqQZDZD"
os.environ["PHONE_NUMBER_ID"] = "210203168844024"

VERIFY_TOKEN = "koechbot"
kwiz = Kwiz(os.getenv("TOKEN"), phone_number_id=os.getenv("PHONE_NUMBER_ID"))

# Dictionary to hold user interactions
user_requests = {}

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
                    "We are here to make holiday assignments easy to access for your child.", 
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
                    PP1(mobile)
                
                elif message_id == "PP2":
                    PP2(mobile)

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

def send_lists_after_message(mobile, message):
    # Sending the response message
    # kwiz.send_msg(message, mobile)

    # Sending the buttons
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
    button = Button(f"", "Which other Assigment would you like to get?", "", action)
    data = ButtonEncoder().encode(button)
    kwiz.send_list(data, mobile)

def PP1(mobile):
    document_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    response = kwiz.send_document(document=document_link, recipient_id=mobile, caption="PP1 Assignment!")
    send_lists_after_message(mobile, response)

def PP2(mobile):
    document_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    response = kwiz.send_document(document=document_link, recipient_id=mobile, caption="PP2 Assignment!")
    send_lists_after_message(mobile, response)

if __name__ == '__main__':
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=7020)
