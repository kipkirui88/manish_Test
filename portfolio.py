import os
from datetime import datetime
from flask import Flask, request
from loguru import logger
from manish import MaNish, Button, Row, Section, Action, ButtonEncoder
from manish.contact import *
from flask import Response

app = Flask(__name__)

# Replace load_dotenv() with setting environment variables directly
os.environ["TOKEN"] = "EAAI7KQfphY0BO0AFVWqjfZA2ur3dKBR7vWJpYUbjoS4n9YYLdkZAJiu1q26VyIczfP6nSkHAMZCinnRv7UcyImY6NVVGLrSTZBTZBZCJdPzd6lTaJWJ6lQ4fxNtaTlyKsZC6z7aNbU7JCNYflVYZAaPdPZBqVaM6UZCPnQND5pAQET9PFlem1hjWZBW4dQ3v09ZAYALrQuRR07PPGBLCEhvgmThKDyEEL9ZACRPZBM1H13"
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
                greeting = f"Hello {name}! Welcome to Koech's Portfolio Bot."

                # Sending the button in response to a text message
                rows = [
                    Row("My Background", "My Background", ""),
                    Row("My Achievements", "My Achievements", ""),
                    Row("My Skills", "My Skills", ""),
                    Row("Projects", "Projects", ""),
                    Row("Contact Me", "Contact Me", ""),
                ]
                sections = [Section("Koech", rows)]
                action = Action("Choose from the List", sections)
                button = Button(greeting, "Tap to Select:", "My Portfolio", action)
                data = ButtonEncoder().encode(button)
                manish.send_button(data, mobile)

            elif message_type == "interactive":
                message_response = manish.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")
                
                # Customize the responses based on user selections
                if message_id == "My Background":
                    manish.send_message(f"🚀 *Koech's Inspiring Career Journey in Software Development* 🚀\n"
                    "Embark on a profound journey through my life—a testament to resilience, passion, and the triumph of the human spirit in the realm of software development."
                    " From humble beginnings, my passion for coding became the compass guiding me through the twists and turns of this dynamic field."
                    "\n\n"
                    "🌱 *From Learning to Doing* 🌱\n"
                    "My journey commenced with self-learning, fueled by an insatiable hunger for knowledge. In the face of limited resources, I persevered, acquiring essential coding skills."
                    " Early projects weren't just code; they were dreams materializing into reality—a testament to the power of determination and resourcefulness."
                    "\n\n"
                    "🚀 *From Challenges to Achievements* 🚀\n"
                    "In the shadows of financial constraints, each milestone felt like a victory against the odds. Embracing internships, freelancing, and collaborative projects, I showcased not only my skills but the unwavering spirit within me."
                    " Winning hackathons and gaining recognition became beacons of hope, illuminating a path forward through the darkest moments."
                    "\n\n"
                    "🌐 *Global Impact* 🌐\n"
                    "My work resonated not only in local spheres but rippled across the globe. The creation of a WhatsApp fees bot, earning recognition in People's Daily newspaper, was a testament to the transformative power of technology."
                    " This global impact wasn't just recognition; it was a validation of the countless hours poured into turning dreams into reality."
                    "\n\n"
                    "🔧 *Constant Growth* 🔧\n"
                    "My journey wasn't just about learning to code; it was a continuous evolution. A commitment to constant growth led me to explore new technologies and methodologies."
                    " Certifications and workshops became stepping stones, not just for personal advancement, but to stay ahead in an ever-evolving tech landscape."
                    "\n\n"
                    "🌟 *Future Aspirations* 🌟\n"
                    "As I reflect, my future holds aspirations beyond personal success. It's a vision of falling into roles that wield enormous impact and garnering resources to guide and assist others."
                    " My commitment is not just to my own journey, but to be a beacon for those navigating similar paths—ensuring no one faces the challenges I did alone."
                    "\n\n"
                    "Join me on this journey—a symphony of highs, lows, and an undying spirit that defines my path in software development!"
                                , recipient_id=mobile)
                    send_tap_to_select_button(mobile)
                
                elif message_id == "My Achievements":
                    manish.send_message("Projects:\n"
                    "1. My Portfolio Website: [Link](https://koech-portfolio.vercel.app/)\n"
                    "2. Serene Solutions: [Link](https://sereneconsultancies.co.ke/)\n"
                    "3. Guarantors Guard: [Link](https://guarantorguard.co.ke/)\n"
                    "4. Samaritan Group: [Link](http://samaritan.epizy.com/)\n"
                    "5. WhatsApp Chatbot: [Link](https://seku-chatbot.vercel.app/)"
                , recipient_id=mobile)
                    send_tap_to_select_button(mobile)

                elif message_id == "My Skills":
                    manish.send_message("Work Experience:\n"
                    "1. Freelance Software Developer (Aug 2023 - Present)\n"
                    "- Engaged in freelance projects, developing customized software solutions.\n"
                    "- Developed chatbots using Flask, FastAPI, and Django for enhanced user engagement.\n"
                    "- Actively attended technology events to stay updated with industry trends."
                    "\n\n"
                    "2. Leta Technologies – Junior Backend Engineer (May 2023 - July 2023)\n"
                    "- Collaborated in building and maintaining backend components of web applications using Django framework.\n"
                    "- Participated in the design and implementation of RESTful APIs."
                , recipient_id=mobile)
                    send_tap_to_select_button(mobile)

                elif message_id == "Projects":
                    response_message = "Here are some projects I've worked on..."
                    manish.send_message(message=response_message, recipient_id=mobile)
                    send_tap_to_select_button(mobile)

                elif message_id == "Contact Me":
                    manish.send_message( f"Contact Information:\n"
                    f"📱 Call: +254727176688\n"
                    f"✉️ Email: hezekiahkoech@gmail.com\n", recipient_id=mobile)
                    send_tap_to_select_button(mobile)

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

def send_tap_to_select_button(mobile):
    # Sending the button in response to a text message
    rows = [
                    Row("My Background", "My Background", ""),
                    Row("My Achievements", "My Achievements", ""),
                    Row("My Skills", "My Skills", ""),
                    Row("Projects", "Projects", ""),
                    Row("Contact Me", "Contact Me", ""),
                ]
    sections = [Section("Kipkirui Koech", rows)]
    action = Action("Choose from the List", sections)
    button = Button("Navigation Menu:", "Tap to Select:", "My Portfolio", action)
    data = ButtonEncoder().encode(button)
    manish.send_button(data, mobile)

if __name__ == '__main__':
    logger.info("Whatsapp Webhook is up and running")
    app.run(host="0.0.0.0", port=7020)