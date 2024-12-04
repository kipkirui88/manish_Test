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

def get_time_of_day():
    now = datetime.now()
    current_hour = now.hour
    if 5 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 18:
        return "afternoon"
    else:
        return "evening"

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

                # Determine the time of day
                time_of_day = get_time_of_day()

                # Sending the button in response to a text message
                rows = [
                    Row("Dev Projects", "Dev Projects", ""),
                    Row("Achievements", "Achievements", ""),
                    Row("Ongoing", "Ongoing", ""),
                    Row("Events", "Events", ""),
                    Row("Ask a Question", "Ask a Question", ""),
                    Row("Request Meeting", "Request Meeting", ""),
                    Row("Contact Info", "Contact Info", ""),
                ]
                sections = [Section("", rows)]
                action = Action("Choose an option:", sections)
                button = Button(f"🎉 Good {time_of_day}, {name}! 🎉", "How can I assist you today?", "", action)
                data = ButtonEncoder().encode(button)
                kwiz.send_list(data, mobile)

            elif message_type == "interactive":
                message_response = kwiz.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")

                if message_id == "Dev Projects":
                    view_development_projects(mobile)
                
                elif message_id == "Achievements":
                    view_achievements(mobile)
                
                elif message_id == "Ongoing":
                    view_ongoing_projects(mobile)
                
                elif message_id == "Events":
                    view_upcoming_events(mobile)
                
                elif message_id == "Ask a Question":
                    ask_question(mobile)
                
                elif message_id == "Request Meeting":
                    request_meeting(mobile)
                
                elif message_id == "Contact Info":
                    contact_information(mobile)

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
    kwiz.send_message(message, mobile)

    # Sending the buttons
    rows = [
        Row("Dev Projects", "Dev Projects", ""),
        Row("Achievements", "Achievements", ""),
        Row("Ongoing", "Ongoing", ""),
        Row("Events", "Events", ""),
        Row("Ask a Question", "Ask a Question", ""),
        Row("Request Meeting", "Request Meeting", ""),
        Row("Contact Info", "Contact Info", ""),
    ]
    sections = [Section("", rows)]
    action = Action("Choose an option:", sections)
    button = Button(f"", "What would you like see next?", "", action)
    data = ButtonEncoder().encode(button)
    kwiz.send_list(data, mobile)

def view_development_projects(mobile):
    response_message = (
        "Here are the major development projects:\n"
        "1. Road Construction - XYZ Road (Completed)\n"
        "2. School Renovation - ABC Primary (Ongoing)\n"
        "3. Health Clinic - PQR Community (Completed)"
    )
    send_lists_after_message(mobile, response_message)

def view_achievements(mobile):
    response_message = (
        "Here are some of our achievements:\n"
        "1. Youth Empowerment Program\n"
        "2. Water Project\n"
        "3. Healthcare Initiative"
    )
    send_lists_after_message(mobile, response_message)

def view_ongoing_projects(mobile):
    response_message = (
        "Here are the ongoing projects:\n"
        "1. Road Expansion - ABC Road (70% complete)\n"
        "2. New Health Center - XYZ (Expected completion by March 2025)\n"
        "3. School ICT Lab - DEF (40% complete)"
    )
    send_lists_after_message(mobile, response_message)

def view_upcoming_events(mobile):
    response_message = (
        "Here are some upcoming events:\n"
        "1. Community Town Hall - Sep 20 (ABC Grounds)\n"
        "2. Youth Workshop - Oct 5 (Digital skills training)\n"
        "3. Healthcare Camp - Oct 15 (Free medical check-up)"
    )
    send_lists_after_message(mobile, response_message)

def ask_question(mobile):
    response_message = "Please type your question or feedback."
    send_lists_after_message(mobile, response_message)

def request_meeting(mobile):
    response_message = (
        "To request a meeting, please provide the following details:\n"
        "1. Full Name\n"
        "2. Preferred Date\n"
        "3. Meeting Purpose"
    )
    send_lists_after_message(mobile, response_message)

def contact_information(mobile):
    response_message = (
        "Contact Information:\n"
        "Phone: +254 712 345 678\n"
        "Email: mp.richard.yegon@example.com\n"
        "Office Address: Bomet East Constituency Office, Main Street."
    )
    send_lists_after_message(mobile, response_message)

if __name__ == '__main__':
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=7020)
