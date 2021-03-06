from config import TWITTER_CONFIG
import tweepy

# get the status number from the full url
def get_status_number_from_url(url):
    try:
        status = url.split('/status/')[1]
        return status
    except IndexError as e:
        print('no status ID: {0}'.format(url))
        return None

# query the twitter API based on the status number
# return tweet text
def query_api(status):
    auth = tweepy.OAuthHandler(TWITTER_CONFIG['consumer_key'], TWITTER_CONFIG['consumer_secret'])
    auth.set_access_token(TWITTER_CONFIG['access_token'], TWITTER_CONFIG['access_token_secret'])

    api = tweepy.API(auth)
    tweet_list = api.statuses_lookup([status])
    for tweet in tweet_list:
        return tweet.text

# if passed a twitter status url, return tweet text
# else return the url
def expand_url(url):
    if 'twitter.com' in url:
        status = get_status_number_from_url(url)
        if status:
            text = query_api(status)
            return text
        else:
            return None
    else:
        return None
