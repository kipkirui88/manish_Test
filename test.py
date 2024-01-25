import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from manish import MaNish, Button, Row, Section, Action, ButtonEncoder
from flask import Response

app = Flask(__name__)

# Replace load_dotenv() with setting environment variables directly
os.environ["TOKEN"] = "EAAI7KQfphY0BO1HDFPwGD82SciKtfHLHG2qwX2jxfPqpMnOOqZCZAnNxtdLtUuXaQ7otvLZC71QYiS1ZAPLksTfzHHFeN9heU8dKk3ZC6ZCDkhce7JsEZC8Fly0ciizH3tGV2iryEIrxWUdusJ1zXoudZC7PGzeInmfbJedYf8pZAdKNQi8iBJEwTuOm2DmmZA3CUOzqU0oWNw4hjLX65M4KrCapyjXEVPtsaxNAEZD"
os.environ["PHONE_NUMBER_ID"] = "107082732389411"

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
    if (
        request.args.get('hub.mode') == "subscribe"
        and request.args.get("hub.challenge")
        and request.args.get('hub.verify_token') == VERIFY_TOKEN
    ):
        return Response(request.args.get('hub.challenge'), content_type='text/plain')
    return Response("Hello world", status=200, content_type='text/plain')

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

                # Greeting based on the time of day
                greeting = f"Hello {name}! Welcome to Rovan!🏗️. How can I assist you today?"

                # Sending the button in response to a text message
                rows = [
                    Row("Browse Products", "Browse Products", ""),
                    Row("Speak to Agent", "Speak to Agent", ""),
                ]
                sections = [Section("Rovan", rows)]
                action = Action("Choose from the List", sections)
                button = Button(greeting, "Select an option from the List below:", "My Rovan", action)
                data = ButtonEncoder().encode(button)
                manish.send_button(data, mobile)

            elif message_type == "interactive":
                message_response = manish.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")
                
                # Process the interactive message and determine the response
                if message_id == "Browse Products":
                    # Greeting based on the time of day
                    greeting = f"Rovan Products Categories 🛍️."

                    # Sending the button in response to the selected option
                    rows = [
                        Row("Cement", "Cement", ""),
                        Row("Bricks", "Bricks", ""),
                        Row("Iron Sheets", "Iron Sheets", ""),
                        # Add more rows as needed
                    ]
                    sections = [Section("Rovan", rows)]
                    action = Action("Choose from the List", sections)
                    button = Button(greeting, "Select any category below:", "My Rovan", action)
                    data = ButtonEncoder().encode(button)
                    manish.send_button(data, mobile)
                
                # Process the interactive message and determine the response
                elif message_id == "Cement":
                    # Greeting based on the time of day
                    greeting = f"Rovan Products 🛍️."

                    # Sending the button in response to the selected option
                    rows = [
                        Row("Simba", "Simba Cement", "Kes 850 per Bag"),
                        Row("Bamburi", "Bamburi Cement", "Kes 800 per Bag"),
                        Row("Mombasa", "Mombasa Cement", "Kes 750 per Bag"),
                        # Add more rows as needed
                    ]
                    sections = [Section("Rovan", rows)]
                    action = Action("Choose from the List", sections)
                    button = Button(greeting, "Select any category below:", "My Rovan", action)
                    data = ButtonEncoder().encode(button)
                    manish.send_button(data, mobile)
                    # Ask the user to enter the quantity
                    ask_quantity_message = "Please enter the quantity for the selected product."
                    manish.send_message(message=ask_quantity_message, recipient_id=mobile)

                # Process the interactive message and determine the response
                elif message_id == "Speak to Agent":
                    # Provide contact information for the agent
                    phones = [Phone(phone="+254727176688", type="CELL")]
                    name = Name(formatted_name="Rovan Agent", first_name="Rovan", last_name="Agent")
                    addresses = [Address(street="Westlands", city="Nairobi", zip="00000", country="Kenya")]
                    emails = [Email("agent@rovan.com")]
                    contact = Contact(name=name, addresses=addresses, emails=emails, phones=phones)
                    contact_data = ContactEncoder().encode([contact])
                    manish.send_contacts(contact_data, mobile)

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

if __name__ == '__main__':
    logger.info("Whatsapp Webhook is up and running")
    app.run(host="0.0.0.0", port=7020)
