from __future__ import print_function
from config import Config
import json
import requests
import time
import datetime
import re


class MyGoogleCalendar():
    TASK_COUNT = 20

    def __init__(self):
        self.config = Config()
        self.is_all_day_notify = False

        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(tokyo_tz)
        self.time_now = datetime.datetime.strptime(now.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")

        # 終日イベントは朝 8 - 9 時の間だけ通知する
        if now.replace(hour=8, minute=0, second=0) <= now <= now.replace(hour=9, minute=0, second=0):
            self.is_all_day_notify = True

    """
    GoogleCalendar からタスクを取得して、文字列として返却する
    """
    def get_str_next_schedule(self, calendar_id, name):
        events = self.get_events(calendar_id)

        if not events:
            print('No upcoming events found.')
            return None

        return self.create_text(name, self.format_events(events))

    """
    GoogleCalendar からイベント取得する
    """
    def get_events(self, calendar_id):
        print(f'Getting the upcoming {self.TASK_COUNT} events')
        events_result = self.config.google_api_client.events().list(
            calendarId=calendar_id,
            timeMin=datetime.datetime.utcnow().isoformat() + 'Z',
            maxResults=self.TASK_COUNT,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    """
    イベントから値を取り出して List で返却する
    """
    def format_events(self, events):
        return [(
            event['start'].get('dateTime', event['start'].get('date')),
            event['end'].get('dateTime', event['end'].get('date')),
            event['summary'],
            event['htmlLink']
        ) for event in events]

    """
    Slack 送信するテキストを作成する
    """
    def create_text(self, name, formatted_events):
        count = 0
        text = f'{self.config.slack_mentions[name]}\n'

        for event in formatted_events:
            # 終日イベント
            if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
                # 通知時間外
                if not self.is_all_day_notify:
                    continue

                count += 1
                start_date = '{0:%Y-%m-%d}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%d'))
                text += '{0} All Day\n{1}\n\n'.format(start_date, event[2])
            # 時間指定イベント
            else:
                start_time = '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00'))

                # 一時間以内のイベントのみ取得する
                if self.get_diff_second(start_time) >= 3601:
                    continue

                count += 1
                end_time = '{0:%H:%M}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00'))
                text += '{0} ~ {1}\n{2}\n'.format(start_time, end_time, event[2])

            text += f'{event[3]}\n\n'

        if count == 0:
            return None

        return text.rstrip('\n')

    def get_diff_second(self, start_time):
        time_event = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        diff = time_event - self.time_now
        return int(diff.seconds)

    """
    1 時間以内のイベントであれば True を返す
    """
    def is_within_limit(self, task, limit=0):
        if task["due_on"] is None:
            return False

        due_on = time.strptime(task["due_on"], "%Y-%m-%d")
        after_week = time.strptime(str(self.today + datetime.datetime.timedelta(days=limit)), "%Y-%m-%d")

        if due_on > after_week:
            return False

        return True

    """
    Slack チャンネルに Post する
    """
    def slack_post(self, text, bot_name, bot_emoji, webhook_url):
        if self.config.is_debug:
            webhook_url = self.config.webhook_urls['default']

        requests.post(webhook_url, json.dumps({
            'text': text,
            'username': bot_name,
            'icon_emoji': bot_emoji,
        }))
