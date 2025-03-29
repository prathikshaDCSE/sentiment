import re
import tweepy
from textblob import TextBlob
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class TwitterClient(object):
    """
    Generic Twitter Class for sentiment analysis using Twitter API v2.
    """
    def __init__(self):
        # Fetch API keys and tokens from environment variables
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if not bearer_token:
            raise ValueError("Twitter Bearer Token is missing. Check your environment variables.")

        try:
            # Create Tweepy client for API v2
            self.client = tweepy.Client(bearer_token=bearer_token)
        except Exception as e:
            print(f"Error: Authentication Failed - {str(e)}")
            self.client = None

    def clean_tweet(self, tweet):
        """
        Utility function to clean tweet text by removing links, special characters
        using regex statements.
        """
        return ' '.join(re.sub(r"(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+://\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method.
        """
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        """
        Main function to fetch tweets and parse them using Twitter API v2 recent search endpoint.
        """
        if not self.client:
            raise ValueError("Twitter API client is not authenticated.")

        tweets = []
        try:
            # Fetch tweets using Twitter API v2
            fetched_tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, 100),  # API v2 allows a max of 100 tweets per request
                tweet_fields=["text", "public_metrics"]
            )

            if not fetched_tweets.data:
                return []

            for tweet in fetched_tweets.data:
                parsed_tweet = {
                    "text": tweet.text,
                    "sentiment": self.get_tweet_sentiment(tweet.text),
                }
                tweets.append(parsed_tweet)

            return tweets
        except tweepy.TweepyException as e:
            print(f"Error: {str(e)}")
            return []

def main():
    """
    Main function for Twitter sentiment analysis.
    """
    # Create TwitterClient instance
    api = TwitterClient()

    # Fetch tweets
    query = "dhanushaishwaryadivorce"
    tweets = api.get_tweets(query=query, count=200)

    if not tweets:
        print("No tweets found!")
        return

    # Filter tweets by sentiment
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

    # Print sentiment analysis results
    print(f"Positive tweets percentage: {100 * len(ptweets) / len(tweets):.2f}%")
    print(f"Negative tweets percentage: {100 * len(ntweets) / len(tweets):.2f}%")
    print(f"Neutral tweets percentage: {100 * (len(tweets) - len(ptweets) - len(ntweets)) / len(tweets):.2f}%")

    # Print positive tweets
    print("\nPositive tweets:")
    for tweet in ptweets[:5]:
        print(tweet['text'])

    # Print negative tweets
    print("\nNegative tweets:")
    for tweet in ntweets[:5]:
        print(tweet['text'])

if __name__ == "__main__":
    main()
