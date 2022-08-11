from config import Config
import json
import requests
import tweepy
from pytz import timezone
from dateutil import parser


class MyTwitter():
    TASK_COUNT = 20

    def __init__(self):
        self.config = Config()

    """
    自分自身の情報を返却する
    """
    def get_me(self):
        me = self.config.client.get_me().data.data

        return {
            'id': me['id'],
            'name': me['name'],
            'username': me['username']
        }

    """
    フォロワー情報を取得して、フォロワー数と一緒に返却
    """
    def get_followers(self, id):
        followers = self.config.client.get_users_followers(id)
        return {
            'followers': followers.data,
            'follower_count': len(followers.data)
        }

    """
    直近のツイート数をカウントする
    """
    def get_recent_tweets_count(self, username, start_time, end_time):
        result = []
        recent_tweets_count = self.config.client.get_recent_tweets_count(
            query=f'from:{username}',
            start_time=start_time,
            end_time=end_time,  # 指定しない場合は現在日時 - 30 秒になる
            granularity='hour'
        ).data

        for r in recent_tweets_count:
            if r['tweet_count'] != 0:
                result.append(r)

        return result

    """
    ユーザ ID からツイートを取得する
    """
    def get_users_tweets(self, id, start_time, end_time, exclude_replies=False, exclude_retweets=False):
        result = []
        exclude = []

        if exclude_replies:
            exclude.append('replies')

        if exclude_retweets:
            exclude.append('retweets')

        # get_users_tweets をそのまま実行すると最新 10 件しかとれないので、Paginator を利用する
        for tweet in tweepy.Paginator(
            self.config.client.get_users_tweets,
            id=id,
            tweet_fields=[
                # 'organic_metrics'  # インプレッションだが、こちらはエンタープライズでしか利用できない
                'public_metrics',
                'created_at'
            ],
            start_time=start_time,
            end_time=end_time,  # 指定しない場合は現在日時 - 30 秒になる
            exclude=None if not exclude else exclude
        ).flatten(limit=250):
            result.append(tweet.data)

        return result

    def search_recent_tweets(self, query, start_time, end_time, max_results=10):
        result = []

        # Paginator を経由すると max_results は無効化される。件数は flatten(limit=max_results) のほうで制御している
        for tweet in tweepy.Paginator(
            self.config.client.search_recent_tweets,
            query=query,
            tweet_fields=[
                # 'organic_metrics'  # インプレッションだが、こちらはエンタープライズでしか利用できない
                'public_metrics',
                'created_at'
            ],
            start_time=start_time,
            end_time=end_time,  # 指定しない場合は現在日時 - 30 秒になる
            max_results=max_results
        ).flatten(limit=max_results):
            result.append(tweet.data)

        return result

    def like(self, tweets):
        for tweet in tweets:
            self.config.client.like(tweet['id'])

    """
    あるユーザ ID に対するメンションツイートを取得する
    """
    def get_users_mention(self, id, start_time, end_time):
        result = []

        # get_users_mentions をそのまま実行すると最新 10 件しかとれないので、Paginator を利用する
        for tweet in tweepy.Paginator(
            self.config.client.get_users_mentions,
            id=id,
            tweet_fields=[
                # 'organic_metrics'  # インプレッションだが、こちらはエンタープライズでしか利用できない
                'public_metrics',
                'created_at'
            ],
            start_time=start_time,
            end_time=end_time,  # 指定しない場合は現在日時 - 30 秒になる
        ).flatten(limit=250):
            result.append(tweet.data)

        return result

    # home_timeline
    # mentions_timeline

    """
    ツイート ID からツイート情報を取得する
    """
    def get_tweet(self, id):
        return self.config.client.get_tweet(id=id, tweet_fields= [
            # 'organic_metrics'  # インプレッションだが、こちらはエンタープライズでしか利用できない
            'public_metrics',
            'created_at'
        ]).data.data

    """
    複数のツイート ID からツイート情報を取得する
    """
    def get_tweets(self, ids):
        result = []

        res = self.config.client.get_tweets(ids=ids, tweet_fields=[
            # 'organic_metrics'  # インプレッションだが、こちらはエンタープライズでしか利用できない
            'public_metrics',
            'created_at'
        ])

        for tweets in res:
            for tweet in tweets:
                result.append(tweet.data)

        return result

    """
    作成したリストをフォローしているユーザを取得できる
    プライベートなリストはエラーが返ってくるので注意
    """
    def get_list_followers(self, list_id):
        return self.config.client.get_list_followers(list_id)

    """
    作成したリスト内の昨日ツイートを取得する
    プライベートなリストはエラーが返ってくるので注意
    """
    def get_list_tweets(self, list_id, max_results=10):
        result = []

        # get_list_tweets をそのまま実行すると最新 10 件しかとれないので、Paginator を利用する
        for tweet in tweepy.Paginator(
            self.config.client.get_list_tweets,
            list_id,
            tweet_fields=[
                'public_metrics',
                'created_at'
            ],
            max_results=max_results
        ).flatten(limit=max_results):
            result.append(tweet.data)

        return result

    """
    いいねされたことのあるツイートを取得
    """
    def get_liked_tweets(self, id):
        return self.config.client.get_liked_tweets(id).data

    """
    昨日の実績文字列を作成
    """
    def get_ytd_str_for_notion(self, users_all_tweets_ytd, me, tweets_count, mention_count, yesterday):
        result = f'Date: *{yesterday}*\nTweet Count: *{tweets_count}*\nMention Count: *{mention_count}*\n\n'
        username = me['username']

        for tweet in users_all_tweets_ytd:
            # ツイート内の改行コードを削除
            text = tweet['text'].replace('\n', '')
            like_count = tweet['public_metrics']['like_count']
            retweet_count = tweet['public_metrics']['retweet_count']
            id = tweet['id']
            url = f'https://twitter.com/{username}/status/{id}/analytics'

            result += f'[Like] *{like_count}* [Retweet] *{retweet_count}* [Tweet] '

            if len(text) > 30:
                result += f'<{url}|{text[0:30]}...>'
            else:
                result += f'<{url}|{text}>'

            result += '\n'

        return result

    """
    週間実績、および一週間以内の LIKE 数によるツイートランキングの文字列を作成 (Notion)
    """
    def get_str_for_notion(self, users_tweets_one_week_ago, me, tweets_count, mention_count, between, followers):
        follower_count = followers['follower_count']
        username = me['username']
        rank = 1
        how_many = 20
        like_ranking = self.__get_like_ranking(how_many, users_tweets_one_week_ago)

        result = '```\n'
        result += '|Between|Tweet Count|Mention Count|Follower Count|Note|\n'
        result += '|:-|:-|:-|:-|:-|\n'
        result += f'|{between}|{tweets_count}|{mention_count}|{follower_count}|[フォロワー増減] xxx [施策内容・結果] xxx [次回施策] xxx|\n\n'
        result += '|Rank|Tweet|Like|Retweet|Created_at|Note|\n'
        result += '|:-|:-|:-|:-|:-|:-|\n'

        for tweet in like_ranking:
            # ツイート内の改行コードを削除
            text = tweet['text'].replace('\n', '')
            like_count = tweet['public_metrics']['like_count']
            retweet_count = tweet['public_metrics']['retweet_count']
            id = tweet['id']
            url = f'https://twitter.com/{username}/status/{id}/analytics'
            created_at_jst = parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")

            if len(text) > 30:
                result += f'|No.{rank}|[{text[0:30]}...]({url})'
            else:
                result += f'|{rank}|[{text}]({url})'

            rank += 1

            result += f'|{like_count}|{retweet_count}|{created_at_jst}||'
            result += '\n'

        result += '```'
        return result

    """
    週間実績、および一週間以内の LIKE 数によるツイートランキングの文字列を作成 (Slack)
    """
    def get_str_for_slack(self, users_tweets_one_week_ago, me, tweets_count, mention_count, between, followers):
        follower_count = followers['follower_count']
        username = me['username']
        rank = 1
        how_many = 20
        like_ranking = self.__get_like_ranking(how_many, users_tweets_one_week_ago)

        result = f'Between: *{between}*\nTweet Count: *{tweets_count}*\nMention Count: *{mention_count}*\nFollower Count: *{follower_count}*\n\n'

        for tweet in like_ranking:
            # ツイート内の改行コードを削除
            text = tweet['text'].replace('\n', '')
            like_count = tweet['public_metrics']['like_count']
            retweet_count = tweet['public_metrics']['retweet_count']
            id = tweet['id']
            url = f'https://twitter.com/{username}/status/{id}/analytics'
            created_at_jst = parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")

            result += f'{rank}. [Like] *{like_count}* [Retweet] *{retweet_count}* [Created_at] *{created_at_jst}* '

            if len(text) > 30:
                result += f'[Tweet] <{url}|{text[0:30]}...> '
            else:
                result += f'[Tweet] <{url}|{text}> '

            rank += 1
            result += '\n'

        return result

    """
    いいねランキング順にソートして List に内包して返却
    """
    def __get_like_ranking(self, how_many, users_tweets_one_week_ago):
        like_ranking = []
        like_dict = {}

        for tweet in users_tweets_one_week_ago:
            id = tweet['id']
            like_dict[id] = int(tweet['public_metrics']['like_count'])

        # LIKE 数 TOP 順に並び替える
        like_dict = sorted(like_dict.items(), key=lambda like: like[1], reverse=True)[0:how_many]

        for element in like_dict:
            tweet = next((x for x in users_tweets_one_week_ago if x["id"] == element[0]), None)

            if tweet is None:
                continue

            like_ranking.append(tweet)

        return like_ranking
