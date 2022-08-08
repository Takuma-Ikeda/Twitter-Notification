from dotenv import load_dotenv
from google.auth import load_credentials_from_file
from googleapiclient.discovery import build
import os

load_dotenv()


class Config():
    EMPLOYEE_1 = 1
    SERVICE_ACCOUNT_JSON_KEY_FILE = 'credential.json'

    def __init__(self):
        is_debug = os.getenv('IS_DEBUG')

        if is_debug is None:
            self.is_debug = False
        else:
            self.is_debug = bool(int(is_debug))

        credential = {
            'type': os.getenv('TYPE'),
            'project_id': os.getenv('PROJECT_ID'),
            'private_key_id': os.getenv('PRIVATE_KEY_ID'),
            'private_key': os.getenv('PRIVATE_KEY'),
            'client_email': os.getenv('CLIENT_EMAIL'),
            'client_id': os.getenv('CLIENT_ID'),
            'auth_uri': os.getenv('AUTH_URI'),
            'token_uri': os.getenv('TOKEN_URI'),
            'auth_provider_x509_cert_url': os.getenv('CLIENT_X509_CERT_URL'),
            'client_x509_cert_url': os.getenv('WEBHOOK_URL_DEFAULT'),
        }

        # credential.json の作成
        with open(self.SERVICE_ACCOUNT_JSON_KEY_FILE, 'w') as file:
            count = 1
            stop = len(credential)
            file.write('{' + '\n')
            for key, val in credential.items():
                if count == stop:
                    file.write(f'  \"{key}\": \"{val}\"')
                else:
                    file.write(f'  \"{key}\": \"{val}\",\n')
                count += 1
            file.write('}' + '\n')

        self.google_api_client = build('calendar', 'v3', credentials=load_credentials_from_file(self.SERVICE_ACCOUNT_JSON_KEY_FILE, [
            'https://www.googleapis.com/auth/calendar.readonly'
        ])[0])

        self.webhook_urls = {
            'default': os.getenv('WEBHOOK_URL_DEFAULT'),
            'google_calendar_todo_notification': os.getenv('WEBHOOK_URL_GOOGLE_CALENDAR_TODO_NOTIFICATION'),
        }

        self.calendar_ids = {
            self.EMPLOYEE_1: os.getenv('CALENDAR_ID'),
        }

        self.slack_mentions = {
            self.EMPLOYEE_1: os.getenv('SLACK_MENTION')
        }
