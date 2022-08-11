from dotenv import load_dotenv
import tweepy
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

        self.client = tweepy.Client(
            bearer_token=os.getenv('BEARER_TOKEN'),
            consumer_key=os.getenv('API_KEY'),
            consumer_secret=os.getenv('API_SECRET'),
            access_token=os.getenv('ACCESS_TOKEN'),
            access_token_secret=os.getenv('ACCESS_TOKEN_SECRET')
        )

        auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
        auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
        self.api = tweepy.API(auth)

        self.auto_like_list_id = os.getenv('AUTO_LIKE_LIST_ID')
