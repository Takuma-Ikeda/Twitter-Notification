from my_google_calendar import MyGoogleCalendar


class GoogleCalendarNotificationForSlack:

    def run(self):
        google_calendar = MyGoogleCalendar()

        for name, calendar_id in google_calendar.config.calendar_ids.items():
            text = google_calendar.get_str_next_schedule(calendar_id, name)

            if text is not None:
                google_calendar.slack_post(text, 'Next Calendar TODO', ':calendar:', google_calendar.config.webhook_urls['google_calendar_todo_notification'])
                print('Slack Post About GoogleCalendar Done!')
            else:
                print('You have no event within an hour!')


google_calendar_notification_for_slack = GoogleCalendarNotificationForSlack()
google_calendar_notification_for_slack.run()
