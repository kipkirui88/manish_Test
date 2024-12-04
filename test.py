from kwiz import Kwiz, M_Pesa_WhatsApp  # Assuming your wrapper is installed or accessible
import json
# Initialize the Kwiz object
token = "EAAI7KQfphY0BOyvENKJQZCqPc27OeNSsPz32lZARFwaw8lLrRwAl0sottUBNEXIJHETXfFCUjSJlgi4qefWmt8XXAHTeZCUl3kCgHLpfBwm5EP6VOM3W9haJKDLPpMyvLhf2XZC6RCUw5CZB9fA6JGrGAUG3RVJojQZByE2mD5JyAX5v1S80sJUyfXdefJ4fdCqQZDZD"
phone_number_id = "210203168844024"

# Create a Kwiz instance
kwiz = Kwiz(token=token, phone_number_id=phone_number_id)

# Send a text message
recipient_number = "254727176688"  # Replace with the recipient's number
message = "Hello, this is a test message."
response = kwiz.send_msg(message=message, recipient_id=recipient_number)
# print(response)

# # Send a document
# document_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
# response = kwiz.send_document(document=document_link, recipient_id=recipient_number, caption="Check out this document!")
# print(response)

from kwiz import Button, Action, Section, Row, ButtonEncoder
import json

# Create rows for the button options
row1 = Row(id="1", title="Option 1", description="This is the first option")
row2 = Row(id="2", title="Option 2", description="This is the second option")

# Create sections to hold rows
section = Section(title="Choose an option", rows=[row1, row2])

# Create the action with button ID and sections
action = Action(button="action_button_id", sections=[section])

# Create the button with header, body, footer, and action
button = Button(header="Choose an option", body="Please select an option from below.", footer="Footer text", action=action)

# Convert the button to JSON using the encoder
button_json = json.dumps(button, cls=ButtonEncoder)

# Now use the send_button method to send the button
response = kwiz.send_list(button=button_json, recipient_id=recipient_number)

# # Print the response to see if the button was sent successfully
# print(response)

# body_text = "What is your favourite color?"  # Body of the message

#     # Defining buttons
# buttons = [
#     {"id": "UNIQUE_BUTTON_ID_1", "title": "Purple"},
#     {"id": "UNIQUE_BUTTON_ID_2", "title": "Black"},
#     {"id": "UNIQUE_BUTTON_ID_3", "title": "Pink"}
# ]

# # Sending the message with buttons
# response = kwiz.send_button(recipient_id=recipient_number, body_text=body_text, buttons=buttons)
# print(response)

# Initialize the wrapper
mpesa_and_whatsapp = M_Pesa_WhatsApp(token=token, phone_number_id=phone_number_id,
                                    mpesa_consumer_key='9uvkU2GwA7E5ygZrfHrAbXX9A1Af8w5bXUO8o1IOeaVo55h9',
                                    mpesa_consumer_secret='d1DPs2ZjFjDrcMY1Fqh26xeWPQzHRVZXcaWrGkA9fJJGYeE7LP5s2tjtDGDWwgZX')

# Send payment prompt to user
whatsapp_response = mpesa_and_whatsapp.send_payment_prompt('254727176688', 10)

# Perform STK push and notify the user via WhatsApp
whatsapp_response, stk_response = mpesa_and_whatsapp.initiate_stk_and_send_message('254727176688', 10)

print(whatsapp_response)  # WhatsApp message response
print(stk_response)  # M-Pesa STK push response
