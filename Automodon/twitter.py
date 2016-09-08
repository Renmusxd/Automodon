#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import string
import os

KEY_FILE = 'twitterkeys.txt'
MOST_RECENT_FILE = 'recentid.txt'

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

    alltweets = []

    new_tweets = api.user_timeline(screen_name=screen_name,count=200)

    oldest = new_tweets[-1].id - 1 if len(new_tweets)>0 else 0
    mostrecent = new_tweets[0].id if len(new_tweets)>0 else 0
    storedto = None

    if os.path.exists(MOST_RECENT_FILE):
        try:
            with open(MOST_RECENT_FILE, "r") as f:
                storedto = int(f.read())
            print("[*] Already have tweets up to {}".format(storedto))
        except Exception as e:
            print("[*] Have no record of stored tweets: "+str(e))

    # save most recent tweets
    hitlimit = False
    for tweet in new_tweets:
        if storedto is None or tweet.id > storedto:
            alltweets.append(tweet)
        else:
            print("[*] Found id within range... ending")
            hitlimit = True

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0 and not hitlimit:
        print("getting tweets before %s" % (oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        # update the id of the oldest tweet less one
        if len(new_tweets)>0:
            oldest = new_tweets[-1].id - 1
            for tweet in new_tweets:
                if storedto is None or tweet.id > storedto:
                    alltweets.append(tweet)
                else:
                    print("[*] Found id within range... ending")
                    hitlimit = True
                    break

        print("...%s tweets downloaded so far" % (len(alltweets)))

    if storedto is None:
        with open(MOST_RECENT_FILE,"w") as f:
            f.write(str(mostrecent))

    # transform the tweepy tweets into a 2D array that will populate the csv
    printable = set(string.printable)
    outtweets = ["".join(filter(lambda x: x in printable, tweet.text))
                 for tweet in alltweets]

    with open('%s_tweets.csv' % screen_name, 'a') as f:
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

