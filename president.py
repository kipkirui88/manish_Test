import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from manish import MaNish, Button, Row, Section, Action, ButtonEncoder
from manish.contact import *
from flask import Response

app = Flask(__name__)

# Replace load_dotenv() with setting environment variables directly
os.environ["TOKEN"] = "EAAI7KQfphY0BOxk5Sn8kZAgqFCq101eUO2TZAvJCrIeFlq9lQtTgOTeEhGUrtfO19GzkZBjrEHl8jIgEfErlYoaFkePjrueHucuaS4ZAHowteeYI9ivvMGjfp1MxG2CN3akjOHhjIQISjA4uDQDiu2UcsNPWz8iUCzhX8AHqSDvX4KGaZA54vZBQIjETxixdqGK47plZCMnpgPEY3YMltz2mevHjlNiFxMDFAQZD"
os.environ["PHONE_NUMBER_ID"] = "210203168844024"

VERIFY_TOKEN = "koechbot"
manish = MaNish(os.getenv("TOKEN"), phone_number_id=os.getenv("PHONE_NUMBER_ID"))

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

import requests

def send_document(document_url, wa_id):

    headers = {
        'Authorization': 'Bearer EAAI7KQfphY0BOxk5Sn8kZAgqFCq101eUO2TZAvJCrIeFlq9lQtTgOTeEhGUrtfO19GzkZBjrEHl8jIgEfErlYoaFkePjrueHucuaS4ZAHowteeYI9ivvMGjfp1MxG2CN3akjOHhjIQISjA4uDQDiu2UcsNPWz8iUCzhX8AHqSDvX4KGaZA54vZBQIjETxixdqGK47plZCMnpgPEY3YMltz2mevHjlNiFxMDFAQZD',
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': wa_id,   # example 91<your number>
        'type': 'document',
        "document": {
            "link": document_url
        }
    }
    response = requests.post(
        'https://graph.facebook.com/v17.0/210203168844024/messages', headers=headers, json=json_data)
    print(response.text)


@app.route("/", methods=["POST"])
def webhook():
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

                # Determine the time of day
                time_of_day = get_time_of_day()

                # Sending the button in response to a text message
                rows = [
                    Row("English", "English", ""),
                    Row("Kiswahili", "Kiswahili", ""),
                ]
                sections = [Section("Election", rows)]
                action = Action("Choose from the List", sections)
                button = Button("Select language/Chagua lugha", "Tap to Select:", "Election", action)
                data = ButtonEncoder().encode(button)
                manish.send_button(data, mobile)

            elif message_type == "interactive":
                message_response = manish.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")

                if message_id == "English":
                        rows = [
                            Row("View Candidates", "View Candidates", ""),
                            Row("Enter issues", "Enter issues", ""),
                            Row("Civic Education", "Civic Education", ""),
                            Row("Share Peace", "Share Peace", ""),
                            Row("Change Language", "Change Language", ""),
                        ]
                        sections = [Section("Election", rows)]
                        action = Action("Choose from the List", sections)
                        button = Button(f"Dear {name}", "Tap to Select:", "Election", action)
                        data = ButtonEncoder().encode(button)
                        manish.send_button(data, mobile)
                
                elif message_id == "View Candidates":
                    view_candidates(mobile)
                elif message_id == "Nairobi":
                    province(mobile)
                elif message_id == "Presidential Candidates":
                    presidential_candidates(mobile)
                elif message_id == "Manifesto":
                    manifesto(mobile)
                elif message_id == "Health care":
                    health_care(mobile)

            else:
                logger.info(f"{mobile} sent {message_type} ")
                logger.info(data)
        else:
            delivery = manish.get_delivery(data)
            if delivery:
                logger.info(f"Message : {delivery}")
            else:
                logger.info("No new message")

    return "ok"

def view_candidates(mobile):
    # Sending the button in response to a text message
    rows = [
        Row("Nairobi", "Nairobi", ""),
        Row("Eastern", "Eastern", ""),
        Row("Coast", "Coast", ""),
        Row("Central", "Central", ""),
        Row("North Eastern", "North Eastern", ""),
        Row("Nyanza", "Nyanza", ""),
        Row("Rift Valley", "Rift Valley", ""),
        Row("Western", "Western", ""),
    ]
    sections = [Section("Election", rows)]
    action = Action("Choose from the List", sections)
    button = Button("Select your Province to proceed", "Tap to Select:", "Election", action)
    data = ButtonEncoder().encode(button)
    manish.send_button(data, mobile)

def province(mobile):
    # Sending the button in response to a text message
    rows = [
        Row("Presidential Candidates", "Presidential Candidates", ""),
        Row("Nairobi Governor", "Nairobi Governor", ""),
        Row("Nairobi Senator", "Nairobi Senator", ""),
        Row("Nairobi Women Rep", "Nairobi Women Rep", ""),
        Row("Nairobi Constituencies", "Nairobi Constituencies", ""),
    ]
    sections = [Section("Election", rows)]
    action = Action("Choose from the List", sections)
    button = Button("NAIROBI County", "Tap to Select:", "", action)
    data = ButtonEncoder().encode(button)
    manish.send_button(data, mobile)

def presidential_candidates(mobile):
    # Sending the button in response to a text message
    rows = [
        Row("Manifesto", "Manifesto", ""),
        Row("Achievements", "Achievements", ""),
        Row("Political History", "Political History", ""),
        Row("Vision", "Vision", ""),
        Row("Mission", "Mission", ""),
        Row("Agenda for Nairobi", "Agenda for Nairobi", ""),
    ]
    sections = [Section("Election", rows)]
    action = Action("Choose from the List", sections)
    button = Button("Cyril Ramaphosa campaign material", "Tap to Select:", "Election", action)
    data = ButtonEncoder().encode(button)
    manish.send_button(data, mobile)

def manifesto(mobile):
    # Sending the button in response to a text message
    rows = [
        Row("Health care", "Health care", ""),
        Row("Youth Employment", "Youth Employment", ""),
        Row("Transport", "Transport", ""),
    ]
    sections = [Section("Election", rows)]
    action = Action("Choose from the List", sections)
    button = Button("Cyril Ramaphosa's Manifesto", "Tap to Select:", "Election", action)
    data = ButtonEncoder().encode(button)
    manish.send_button(data, mobile)
    

def health_care(mobile):
    # Sending the button in response to a text message
    manish.send_message("*National Healthcare:* My Government will introduce the following National Healthcare policies\n\n"
                    "1. Comprehensive medical insurance for all South Africans above 18 years\n"
                    "2. Free Maternal healthcare in all Government hospitals\n"
                    "3. Free medical care in all hospitals for all South Africans\n"
                , recipient_id=mobile)
    document_url = "https://wajibikamkenya.com/elections/content/documents/89031705986822.pdf"
    send_document(document_url, mobile)

    # # Example usage for sending an image
    # image_url = "https://wajibikamkenya.com/elections/content/photos/89031705986822.jpeg"
    # send_media(image_url, "image", "254727176688")
    
if __name__ == '__main__':
    logger.info("Whatsapp Webhook is up and running")
    app.run(host="0.0.0.0", port=7020)