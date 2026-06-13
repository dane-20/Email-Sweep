from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json

SCOPES = ['https://mail.google.com/']

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=creds)

with open("token.json", "w") as token:
    token.write(creds.to_json())

profile = service.users().getProfile(userId="me").execute()
messages = service.users().messages().list(userId="me", q="category:promotions").execute()
message_list = messages["messages"]

for message in message_list:
    message_id = message['id']
    full_message = service.users().messages().get(userId="me", id=message_id).execute()
    print(json.dumps(full_message, indent=2))
#print(f"your email is: {profile["emailAddress"]}")
#message = message_list[6]
#message_id = message['id']  # extract the id from the dictionary
#full_message = service.users().messages().get(userId="me", id=message_id).execute()

