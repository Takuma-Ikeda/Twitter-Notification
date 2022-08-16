import datetime
from datetime import timedelta
from my_twitter import MyTwitter
import random
import time


class TwitterAutoLikeByQuery:

    def __init__(self) -> None:
        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        self.now = datetime.datetime.now(tokyo_tz) - timedelta(minutes=1)
        self.one_hour_ago = self.now - timedelta(hours=1)

    def run(self):
        twitter = MyTwitter()
        # LIKE は 15 分以内で 50 回まで。それ以上実行すると 429 Too Many Requests がしばらく発生するので注意
        # NOTE: https://developer.twitter.com/en/docs/twitter-api/rate-limits
        api_limit = 50
        api_limit_count = 0
        max_results = random.choice([12, 11, 10, 9, 8])
        queries = ['#駆け出しエンジニアと繋がりたい', 'エンジニア']

        for query in queries:
            tweets = twitter.search_recent_tweets(query, self.one_hour_ago, self.now, max_results)
            api_limit_count += len(tweets)

            if api_limit_count <= api_limit:
                time.sleep(random.choice([1, 2, 3]))
                twitter.like(tweets)
            else:
                available_count = api_limit_count - api_limit
                time.sleep(random.choice([1, 2, 3]))
                twitter.like(tweets[0:available_count])
                break

        print('Auto Like By Query Done')


twitter_auto_like_by_query = TwitterAutoLikeByQuery()
twitter_auto_like_by_query.run()
