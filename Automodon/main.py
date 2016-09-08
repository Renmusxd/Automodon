import tweepy, time
import sys
try:
    from Markov import MarkovTweets
except:
    from .Markov import MarkovTweets

SLEEP_TIME = 60*30

def readKeys(filename):
    keydict = {}
    with open(filename,"r") as f:
        for line in f:
            linetable = [s.strip() for s in line.split("=")]
            if len(linetable)==2:
                keydict[linetable[0]] = linetable[1]
    return keydict

if __name__ == "__main__":
    if len(sys.argv)>1:
        iters = int(sys.argv[1])
    else:
        iters = None

    if len(sys.argv)>2:
        sleep_time = int(sys.argv[2])
    else:
        sleep_time = SLEEP_TIME

    keys = readKeys('twitterkeys.txt')
    auth = tweepy.OAuthHandler(keys["CONSUMER_KEY"], keys["CONSUMER_SECRET"])
    auth.set_access_token(keys["ACCESS_KEY"], keys["ACCESS_SECRET"])
    api = tweepy.API(auth)

    mtweets = MarkovTweets("realDonaldTrump_tweets.csv")

    while iters is None or iters>0:
        time.sleep(sleep_time)
        newtweet = mtweets.makeTweet()
        print("[*] Updating: "+("("+str(iters)+")" if iters is not None else ""))
        print(newtweet)
        api.update_status(newtweet)
        iters -= 1

    