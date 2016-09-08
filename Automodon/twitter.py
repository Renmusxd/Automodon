#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import string

KEY_FILE = 'twitterkeys.txt'

def readKeys(filename):
    keydict = {}
    with open(filename,"r") as f:
        for line in f:
            linetable = [s.strip() for s in line.split("=")]
            if len(linetable)==2:
                keydict[linetable[0]] = linetable[1]
    return keydict

def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    keys = readKeys('twitterkeys.txt')
    auth = tweepy.OAuthHandler(keys["CONSUMER_KEY"], keys["CONSUMER_SECRET"])
    auth.set_access_token(keys["ACCESS_KEY"], keys["ACCESS_SECRET"])
    api = tweepy.API(auth)
    # initialize a list to hold all the tweepy Tweets
    alltweets = []
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)
    # save most recent tweets
    alltweets.extend(new_tweets)
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))
        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
        # save most recent tweets
        alltweets.extend(new_tweets)
        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        print("...%s tweets downloaded so far" % (len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    printable = set(string.printable)
    newlines = '\n\r'
    outtweets = ["".join(filter(lambda x: x in printable, tweet.text))
                 for tweet in alltweets]
    with open('%s_tweets.csv' % screen_name, 'w') as f:
        for singletweet in outtweets:
            if not (singletweet.startswith('RT') or
                        singletweet.startswith("\"") or
                        ("http" in singletweet)):
                if singletweet[0]==".":
                    singletweet = singletweet[1:]
                f.write(singletweet
                        .replace('\n',' ')
                        .replace('\r',' ')+"\n")

if __name__ == '__main__':
    get_all_tweets("realDonaldTrump")

