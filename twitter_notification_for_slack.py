from my_twitter import MyTwitter
import datetime
from datetime import timedelta


class TwitterNotificationForSlack:

    def __init__(self) -> None:
        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(tokyo_tz)
        self.yesterday = now - timedelta(days=1)
        self.one_week_ago = now - timedelta(days=7)

    def run(self):
        twitter = MyTwitter()

        # 自分自身のデータ
        me = twitter.get_me()

        # 自分自身のフォロワー情報
        followers = twitter.get_followers(me['id'])

        self.__yesterday_tweets_post(twitter, me)
        self.__weeky_tweets_post(twitter, me, followers)

    def __yesterday_tweets_post(self, twitter, me):
        start_time_for_ytd = self.yesterday.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_for_ytd = self.yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%SZ')

        # 昨日のツイートを取得: リプライ・リツイート含む
        users_all_tweets_ytd = twitter.get_users_tweets(
            me['id'],
            start_time_for_ytd,
            end_time_for_ytd
        )

        # 昨日のツイートを取得: リプライ・リツイート含まない
        users_just_tweets_ytd = twitter.get_users_tweets(
            me['id'],
            start_time_for_ytd,
            end_time_for_ytd,
            True,
            True
        )

        all_tweets_count_ytd = len(users_all_tweets_ytd)
        tweets_count_ytd = len(users_just_tweets_ytd)
        mention_count_ytd = all_tweets_count_ytd - tweets_count_ytd

        yesterday = self.yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d')

        str_for_slack = twitter.get_ytd_str_for_notion(users_all_tweets_ytd, me, tweets_count_ytd, mention_count_ytd, yesterday)

        if str_for_slack is not None:
            twitter.slack_post(str_for_slack, 'Yesterday\'s Twitter Result', ':baby_chick:', twitter.config.webhook_urls['twitter_notification'])
            print('Slack Post About Yesterday\'s Tweets for Slack Done!')
        else:
            print('No Tweets!')

    def __weeky_tweets_post(self, twitter, me, followers):
        start_time_for_one_week_ago = self.one_week_ago.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_for_ytd = self.yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%SZ')

        # 一週間分のツイートを取得: リプライ・リツイート含む
        users_all_tweets_one_week_ago = twitter.get_users_tweets(
            me['id'],
            start_time_for_one_week_ago,
            end_time_for_ytd
        )

        # 一週間分のツイートを取得: リプライ・リツイート含まない
        users_just_tweets_one_week_ago = twitter.get_users_tweets(
            me['id'],
            start_time_for_one_week_ago,
            end_time_for_ytd,
            True,
            True,
        )

        all_tweets_count_one_week_ago = len(users_all_tweets_one_week_ago)
        tweets_count_one_week_ago = len(users_just_tweets_one_week_ago)
        mention_count_one_week_ago = all_tweets_count_one_week_ago - tweets_count_one_week_ago

        since = self.one_week_ago.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d')
        until = self.yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d')
        between = f'{since} - {until}'

        str_for_notion = twitter.get_str_for_notion(users_all_tweets_one_week_ago, me, tweets_count_one_week_ago, mention_count_one_week_ago, between, followers)

        if str_for_notion is not None:
            twitter.slack_post(str_for_notion, 'Weekly Twitter Result', ':bird:', twitter.config.webhook_urls['twitter_notification_for_notion'])
            print('Slack Post About Weekly Tweets for Notion Done!')
        else:
            print('No Tweets!')

        str_for_slack = twitter.get_str_for_slack(users_all_tweets_one_week_ago, me, tweets_count_one_week_ago, mention_count_one_week_ago, between, followers)

        if str_for_notion is not None:
            twitter.slack_post(str_for_slack, 'Weekly Twitter Result', ':bird:', twitter.config.webhook_urls['twitter_notification'])
            print('Slack Post About Weekly Tweets for Slack Done!')
        else:
            print('No Tweets!')


twitter_notification_for_slack = TwitterNotificationForSlack()
twitter_notification_for_slack.run()
