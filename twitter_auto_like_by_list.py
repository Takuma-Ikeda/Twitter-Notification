from my_twitter import MyTwitter
import datetime
from datetime import timedelta


class TwitterAutoLikeByList:

    def __init__(self) -> None:
        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        self.now = datetime.datetime.now(tokyo_tz) - timedelta(minutes=1)
        self.one_hour_ago = self.now - timedelta(hours=1)

    def run(self):
        twitter = MyTwitter()
        # LIKE は 15 分以内で 50 回まで。それ以上実行すると 429 Too Many Requests がしばらく発生するので注意
        # NOTE: https://developer.twitter.com/en/docs/twitter-api/rate-limits
        api_limit = 50
        max_results = 10

        tweets = twitter.get_list_tweets(twitter.config.auto_like_list_id, max_results)

        if len(tweets) <= api_limit:
            twitter.like(tweets)
        else:
            twitter.like(tweets[0:api_limit])

        print('Auto Like By List Done')


twitter_auto_like_by_list = TwitterAutoLikeByList()
twitter_auto_like_by_list.run()
