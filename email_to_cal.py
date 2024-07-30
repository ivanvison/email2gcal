import imaplib
import email
from email.header import decode_header
import os
import re
import datetime
from bs4 import BeautifulSoup
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from dotenv import load_dotenv

# Path to your token.pickle file
token_path = 'token.pickle'

# Delete bday_cal_entries.csv if it exists
if os.path.exists('bday_cal_entries.csv'):
    os.remove('bday_cal_entries.csv')
    print("Deleted bday_cal_entries.csv.")

# Delete the token.pickle file if it exists
# if os.path.exists(token_path):
#     os.remove(token_path)
#     print(f"Deleted {token_path}, please run your script again to re-authenticate.")
# else:
#     print(f"{token_path} does not exist, proceed with authentication.")

# Load environment variables from .env file
load_dotenv()

# Get variables from env file
username = os.getenv('GMAIL_ACCOUNT_EMAIL')
password = os.getenv('GMAIL_ACCOUNT_PASSWORD')
google_calendar_id = os.getenv('GOOGLE_CALENDAR_ID')

# Gmail connection
def connect_to_gmail(username, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    return mail

# Fetch new emails
def fetch_emails(mail):
    mail.select("inbox")
    result, data = mail.uid('search', None, "(UNSEEN)")
    email_ids = data[0].split()
    return list(reversed(email_ids))  # Reverse to start with the most recent

# Parse email body
def parse_email_body(mail, email_id):
    result, email_data = mail.uid('fetch', email_id, '(BODY[TEXT])')
    raw_email = email_data[0][1].decode("utf-8")
    soup = BeautifulSoup(raw_email, "html.parser")
    email_body = soup.get_text()
    match = re.search(r'1973@(.*?)@1973\s*1974@(.*?)@1974', email_body)
    if match:
        description, date = match.groups()
        return description, date
    else:
        return None, None

# Check for duplicate entries
def is_duplicate(description, date, existing_entries):
    return any(entry['Description'] == description and entry['Date'] == date for entry in existing_entries)

# Delete email
def delete_email(mail, email_id):
    mail.uid('store', email_id, '+FLAGS', '(\\Deleted)')
    mail.expunge()

# Google Calendar integration
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Google Calendar authentication
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('google_client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def read_csv_events(filename):
    events = []
    with open(filename, newline='', encoding='utf-8') as csvfile:  # Specify UTF-8 encoding
        reader = csv.DictReader(csvfile)
        for row in reader:
            events.append((row['Description'], row['Date']))
    return events

# Check if event already exists
def check_event_exists(service, description, date, calendar_id='primary'):
    start_date = datetime.datetime.strptime(date, "%d/%m/%Y")
    end_date = start_date + datetime.timedelta(days=1)
    start_date = start_date.isoformat() + 'Z'
    end_date = end_date.isoformat() + 'Z'
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_date, timeMax=end_date, singleEvents=True, orderBy='startTime').execute()
    for event in events_result.get('items', []):
        if event['summary'] == description:
            return True
    return False

# Create event
def create_event(service, description, date, calendar_id='primary'):
    start_date = datetime.datetime.strptime(date, "%d/%m/%Y").date().isoformat()
    event = {
        'summary': description,
        'start': {'date': start_date},
        'end': {'date': start_date},
        'recurrence': ['RRULE:FREQ=YEARLY'],
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()


# Main function
def main(username, password, calendar_id='primary'):
    mail = connect_to_gmail(username, password)
    email_ids = fetch_emails(mail)

    # End script if there are no emails to process
    if len(email_ids) == 0:
        print("No new emails found.")
        exit()
    else:
        print(f"Fetched {len(email_ids)} unseen emails.")    

    existing_entries = []
    if os.path.exists('bday_cal_entries.csv'):
        with open('bday_cal_entries.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_entries = list(reader)
    
    print("|---PROCESSING EMAILS AND POPULATING CSV---|")
    with open('bday_cal_entries.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not existing_entries:
            writer.writerow(['Description', 'Date'])
        for email_id in email_ids:
            description, date = parse_email_body(mail, email_id)
            if description and date and not is_duplicate(description, date, existing_entries):
                writer.writerow([description, date])
                print(f"Added event: {description} on {date}")
                existing_entries.append({'Description': description, 'Date': date})
                delete_email(mail, email_id)

    # Google Calendar integration
    service = authenticate_google_calendar()
    events = read_csv_events("bday_cal_entries.csv")
    print("|---PROCESSING CSV AND POPULATING GOOGLE CALENDAR---|")    
    for description, date in events:
        if not check_event_exists(service, description, date, calendar_id):
            create_event(service, description, date, calendar_id)
        else:
            print(f"{description} - {date} - NOT ADDED")

# Call the main function with specific calendar ID
if __name__ == '__main__':
    main(username, password, google_calendar_id)
