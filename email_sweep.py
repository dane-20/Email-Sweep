from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json
import time
time.sleep(0.05)

SAFE_SENDERS = ["Abel P", "LinkedIn", "Indeed", "Capital One", "TFCU"]

def main():
    service = init()
    messages = service.users().messages().list(userId="me", q="category:promotions OR category:social").execute()
    user_input = input("What do you want to do?\n 'v' - view the messages\n 'x' delete the messages\n 'a' - add a sender to safe sender list\n 's' - search for sender\n")
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
    elif user_input.lower() == 's':
        search(service, messages)
    elif user_input.lower() == 't':
        test_visual(service, messages)
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

    # -- checks other pages to extend the amount of emails to be deleted
    while "nextPageToken" in messages:
        messages = service.users().messages().list(
            userId="me",
            q="category:promotions OR category:social",
            pageToken=messages["nextPageToken"]
        ).execute()
        message_list.extend(messages["messages"])

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

# -- searches for a particular sender and shows how many emails from them
def search(service, messages, query):
    message_list = messages["messages"]
    key_search = input("Enter the name of the sender: ")
    total = 0
    errors = 0

    # -- checks other pages to extend the amount of emails to be searched
    while "nextPageToken" in messages:
        messages = service.users().messages().list(
            userId="me",
            q=query,
            pageToken=messages["nextPageToken"]
        ).execute()
        message_list.extend(messages["messages"])

    for message in message_list:
        message_id = message['id']
        try:
            full_message = service.users().messages().get(
                userId="me", id=message_id, format='metadata', metadataHeaders=['From']
            ).execute()
        except Exception as e:
            print(f"Skipped {message_id}, error: {e}")
            errors += 1
            continue

        message_header = full_message["payload"]["headers"]
        sender_matches = [header["value"] for header in message_header if header["name"] == "From"]

        if not sender_matches:
            continue  # no "From" header found, skip this message

        sender = sender_matches[0]

        if key_search in sender:
            print(sender)
            total += 1

    print(f"Found a total of {total} senders! ({errors} errors)")


def test_visual(service, messages):
    print(messages["messages"])

# TODO: - Need to check how the project should be pushed to github, given that I have my own credentials in this project folder. 
#           - Also check how the project should be pushed given that we have an environment with libraries imported
#       - Need to increase the amount of emails that are deleted. 


main()