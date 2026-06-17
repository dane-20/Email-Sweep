from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json

SAFE_SENDERS = ["Abel P", "LinkedIn", "Indeed", "Capital One", "TFCU"]

def main():
    service = init()
    messages = service.users().messages().list(userId="me", q="category:promotions OR category:social").execute()
    user_input = input("What do you want to do?\n 'v' - view the messages\n 'x' delete the messages\n 'a' - add a sender to safe sender list\n")
    if user_input.lower() == 'v':
        val = input("How many would you like to view? ")
        if val.isdigit():
            view(service, messages, int(val))
        else:
            print("Invalid value!")
    elif user_input.lower() == 'x':
        delete(service, messages)
    elif user_input.lower() == 'a': # this might be dumb since it wont save, unsure if i want to add database stuff since this is for me and for fun
        addition = input("Add the name of the sender to prevent from being deleted (- to cancel): ")
        if addition != '-':
            SAFE_SENDERS.append(addition)
        print(SAFE_SENDERS)
    else:
        print("Invalid input!")

def init():
    SCOPES = ['https://mail.google.com/']

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    service = build('gmail', 'v1', credentials=creds)

    with open("token.json", "w") as token:
        token.write(creds.to_json())
    
    return service

#NOTE: this is fine for now but remember that the api call each time is bad practice and high complexity
def view(service, messages, amount):
    message_list = messages["messages"]

    for i in range(amount+1):
        message = message_list[i]
        message_id = message['id']
        full_message = service.users().messages().get(userId="me", id=message_id).execute() # type dict
        #print(type(full_message["payload"]["headers"]))
        message_header = full_message["payload"]["headers"]
        sender = [header["value"] for header in message_header if header["name"] == "From"][0]
        is_safe = any(safe in sender for safe in SAFE_SENDERS)
        if not is_safe:
            print(sender)
        # print(json.dumps(sender, indent=2)) -- AS A JSON
        #print(json.dumps(full_message["payload"], indent=2)) -- AS A JSON

# -- extracting the single message from inbox 
# message = message_list[0]
# message_id = message['id']  # extract the id from the dictionary

# # -- actually getting the message and viewing it from its id
# full_message = service.users().messages().get(userId="me", id=message_id).execute()
# #print(json.dumps(full_message, indent=2))

# -- moving the message to trash
def delete(service, messages):
    deleted_count = 0
    message_list: list = messages["messages"]

    confirm = input(f"About to process {len(message_list)} messages. Continue? (y/n) ")
    if confirm.lower() != 'y':
        return
    
    for message in message_list:
        message_id = message["id"]
        full_message = service.users().messages().get(userId="me", id=message_id).execute() # type dict
        message_header = full_message["payload"]["headers"]
        sender = [header["value"] for header in message_header if header["name"] == "From"][0]
        is_safe = any(safe in sender for safe in SAFE_SENDERS)
        if not is_safe:
            print(f"Deleting: {sender}")
            service.users().messages().trash(userId="me", id=message_id).execute()
            deleted_count += 1
        
    print(f"Done. Deleted {deleted_count} emails!")
    return

main()