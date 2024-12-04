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

import csv

def read_todo_list():
    tasks = []
    try:
        with open('todo_list.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tasks.append(f"{row['Task']} - {row['Status']}")
    except Exception as e:
        logger.error(f"Error reading to-do list: {e}")
    return tasks

def add_task_to_csv(task_title):
    """Appends a new task to the CSV file with a default status of 'Pending'."""
    try:
        with open('todo_list.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([task_title, "Pending"])  # Task title and default status
        return True
    except Exception as e:
        logger.error(f"Error saving task: {e}")
        return False
    
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
# Initialize a dictionary to track user actions
current_action = {}
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    changed_field = kwiz.changed_field(data)

    if changed_field == "messages":
        mobile = kwiz.get_mobile(data)

        if mobile:
            name = kwiz.get_name(data)
            message_type = kwiz.get_message_type(data)

            if message_type == "text":
                message = kwiz.get_message(data).strip().lower()
                logger.info("Message: %s", message)

                # Handle greeting messages
                if message in ["hi", "hello"]:
                    response_message = f"Good {get_time_of_day()}, {name}! I'm *TaskMate*, your To-Do Manager. How can I assist you today?"
                    send_lists_after_message(mobile, response_message)

                # Handle adding a task
                elif current_action.get(mobile) == "Add a Task":
                    task_title = message  # Get the user's input as task title
                    if task_title:
                        success = add_task_to_csv(task_title)
                        if success:
                            response_message = f"The task *'{task_title}'* has been added to your To-Do list!"
                            current_action.pop(mobile, None)  # Clear the current action
                        else:
                            response_message = "There was an error saving the task. Please try again."
                    else:
                        response_message = "Task title cannot be empty. Please enter a valid task title."

                    send_lists_after_message(mobile, response_message)

                else:
                    # Default response for unrecognized text
                    response_message = "I didn't understand that. Please choose an option below."
                    send_lists_after_message(mobile, response_message)

            elif message_type == "interactive":
                message_response = kwiz.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(f"Interactive Message; {message_id}: {message_text}")

                if message_id == "View To-Do List":
                    view_task(mobile)

                elif message_id == "Add a Task":
                    # Track user's action to add a task
                    current_action[mobile] = "Add a Task"
                    response_message = "Please enter the task title."
                    kwiz.send_msg(response_message, mobile)

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
    kwiz.send_msg(message, mobile)

    # Sending the buttons
    rows = [
        Row("View To-Do List", "View To-Do List", ""),
        Row("Add a Task", "Add a Task", ""),
    ]
    sections = [Section("", rows)]
    action = Action("Choose an option:", sections)
    button = Button(f"", "What would you like see next?", "", action)
    data = ButtonEncoder().encode(button)
    kwiz.send_list(data, mobile)

def view_task(mobile):
    tasks = read_todo_list()

    if tasks:
        # Format tasks with numbering and emojis at the end
        formatted_tasks = []
        emoji_map = {
            "Completed": "✅",
            "Ongoing": "🔄",
            "Pending": "🕗"
        }

        for idx, task in enumerate(tasks, start=1):
            task_parts = task.split(" - ")
            if len(task_parts) == 2:
                task_title, task_status = task_parts
                emoji = emoji_map.get(task_status, "📌")  # Default emoji if status doesn't match
                formatted_tasks.append(
                    f"{idx}. *{task_title}* - *{task_status}* {emoji}"
                )
            else:
                formatted_tasks.append(f"{idx}. {task}")  # Fallback for malformed rows

        response_message = "*📌 Here is your To-Do List:*\n\n" + "\n".join(formatted_tasks)
    else:
        response_message = "Your To-Do list is currently empty."

    send_lists_after_message(mobile, response_message)





if __name__ == '__main__':
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=7020)
