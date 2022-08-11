# Twitter-Notification

- 1 時間おきに、特定キーワード・ハッシュタグの最新ツイート 20 件ずついいねする

## 動作環境

```sh
pipenv install
pipenv shell
```

- Python 3.9.6

### Library

- [tweepy](https://github.com/tweepy/tweepy)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
  - ローカルで実行するときに `.env` を読み込む
- [pytz](https://github.com/stub42/pytz)
- [python-dateutil](https://github.com/dateutil/dateutil)

## Tweepy Reference

- https://developer.twitter.com/en
  - 利用している Twitter API は 2 系
