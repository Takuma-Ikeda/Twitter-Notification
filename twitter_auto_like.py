from my_twitter import MyTwitter
import datetime
from datetime import timedelta


class TwitterAutoLike:

    def __init__(self) -> None:
        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        self.now = datetime.datetime.now(tokyo_tz) - timedelta(minutes=1)
        self.one_hour_ago = self.now - timedelta(hours=1)

    def run(self):
        twitter = MyTwitter()
        # LIKE は 15 分以内で 50 回まで。それ以上するとしばらく 429 Too Many Requests が発生するので注意
        # NOTE: https://developer.twitter.com/en/docs/twitter-api/rate-limits
        max_results = 10
        tweets = twitter.search_recent_tweets('#駆け出しエンジニアと繋がりたい', self.one_hour_ago, self.now, max_results)
        twitter.like(tweets)
        print('Auto Like Script Done')


twitter_auto_like = TwitterAutoLike()
twitter_auto_like.run()
