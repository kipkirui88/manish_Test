import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from manish import MaNish, Button, Row, Section, Action, ButtonEncoder
from manish.contact import *
from flask import Response
import requests
import json
from requests.exceptions import JSONDecodeError

app = Flask(__name__)

# Replace load_dotenv() with setting environment variables directly
os.environ["TOKEN"] = "EAAI7KQfphY0BO972hBBVhXtsZB1McoOuNlYN1AjqZBP6BKH1xQGCZBcI7v5nMrzYdd4fTsBvlnTGv7ZCvXGg8Ot30PJNnsHUHwJFJ24VjsBZBwgJurfo2lsfJsbZAmaL2YnsHN2zvrlWoavZBZCfhft6dpUDebPHN3u3bsqvewPNEUfYZCbyFBR3uLcyGjZCVH3NccPNpULYewWzMWKZCnCpq5eK5knRtKd3COD0Q4ZD"
os.environ["PHONE_NUMBER_ID"] = "210203168844024"

VERIFY_TOKEN = "koechbot"
manish = MaNish(os.getenv("TOKEN"), phone_number_id=os.getenv("PHONE_NUMBER_ID"))

# Endpoint URL
base_url = "https://wajibikamkenya.com/elections/bot.php"

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
                if not request.args.get("hub.verify_token") == "koechbot":
                    return "Verification token mismatch", 403
                return request.args['hub.challenge'], 200

        print(request)
        res = request.get_json()
        print(res)

        if 'entry' in res and 'changes' in res['entry'][0] and 'value' in res['entry'][0]['changes'][0] and 'messages' in res['entry'][0]['changes'][0]['value']:
            user_query = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

            # Check if 'contacts' key is present
            if 'contacts' in res['entry'][0]['changes'][0]['value']['messages'][0]:
                wa_id = res['entry'][0]['changes'][0]['value']['messages'][0]['contacts'][0]['wa_id']
            else:
                wa_id = res['entry'][0]['changes'][0]['value']['messages'][0]['from']

            # Handle user response
            webhook(wa_id)

    except Exception as e:
        print(f"Error: {e}")

    return '200 OK HTTPS.'

import traceback  # Import traceback module

...

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        changed_field = manish.changed_field(data)

        if changed_field == "messages":
            new_message = manish.get_mobile(data)

            if new_message:
                mobile = manish.get_mobile(data)
                name = manish.get_name(data)
                message_type = manish.get_message_type(data)

                if message_type == "text":
                    message = manish.get_message(data)
                    logger.info("Message: %s", message)

                    # Send user input to endpoint and get response
                    params = {
                        "phone_number": "0727176688",
                        "token": "343idHQSL71311651802266",
                        "first_name": "Kipkirui",
                        "last_name": "Koech",
                        "text": message
                    }

                    try:
                        response = requests.post(base_url, params=params)
                        if response.status_code == 200:
                            response_data = response.json()
                            greeting = response_data["top"]["message"]
                            options = response_data["top"]["options"]
                            
                            # Sending greeting message
                            manish.send_message(greeting, mobile)
                            greeting_with_options = "Welcome to ANC Chatbot"
                            rows = [Row(option['option'], option['optionValue'][:10], "") for option in options]
                            sections = [Section("Options", rows)]
                            action = Action("Choose from the List", sections)
                            button = Button(greeting_with_options, "Tap to Select:", "My Campaign", action)
                            data = ButtonEncoder().encode(button)
                            manish.send_button(data, mobile)
                        else:
                            logger.error("Error occurred while sending request to endpoint")

                    except Exception as e:
                        # Log the traceback of the exception for debugging
                        logger.error("An error occurred: %s", traceback.format_exc())

                elif message_type == "interactive":
                    interactive_response = manish.get_interactive_response(data)
                    interactive_type = interactive_response.get("type")
                    option_id = interactive_response[interactive_type]["id"]
                    logger.info(f"User selected option ID: {option_id}")

                    # Send user input to endpoint and get response
                    params = {
                        "phone_number": "0727176688",
                        "token": "343idHQSL71311651802266",
                        "first_name": "Kipkirui",
                        "last_name": "Koech",
                        "text": option_id  # Use option_id as the 'text' parameter
                    }

                    try:
                        response = requests.post(base_url, params=params)
                        if response.status_code == option_id:
                            response_data = response.json()
                            greeting = response_data["top"]["message"]
                            options = response_data["top"]["options"]
                            
                            # Sending greeting message
                            manish.send_message(greeting, mobile)
                            # greeting_with_options = "Welcome to ANC Chatbot"
                            rows = [Row(option['option'], option['optionValue'][:10], "") for option in options]
                            sections = [Section("Options", rows)]
                            action = Action("Choose from the List", sections)
                            button = Button("Tap to Select:", "My Campaign", action)
                            data = ButtonEncoder().encode(button)
                            manish.send_button(data, mobile)
                        else:
                            logger.error("Error occurred while sending request to endpoint")

                    except Exception as e:
                        # Log the traceback of the exception for debugging
                        logger.error("An error occurred: %s", traceback.format_exc())


            else:
                delivery = manish.get_delivery(data)
                if delivery:
                    logger.info(f"Message : {delivery}")
                else:
                    logger.info("No new message")

    except Exception as e:
        # Log the traceback of the exception for debugging
        logger.error("Error: %s", traceback.format_exc())

    return "ok"


if __name__ == '__main__':
    logger.info("Whatsapp Webhook is up and running")
    app.run(host="0.0.0.0", port=7020)
