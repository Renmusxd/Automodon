
import random
import re


class MarkovTweets:
    ENDSPECIALCHAR = " "
    punct = '.!?'
    CONTINUE_CHANGE = 0.3

    def __init__(self, quotefile):
        self.startnode = MarkovNode('^',startnode=True)
        self.endnode = MarkovNode(MarkovTweets.ENDSPECIALCHAR,endnode=True)
        self.model = {}
        self.model[MarkovTweets.ENDSPECIALCHAR] = self.endnode  # If ends without punctuation
        with open(quotefile, "r") as f:
            i = 0
            for line in f:
                self.addTweet(line)
                i += 1

    def addTweet(self, tweetstring):
        tweetstring = tweetstring.replace('&amp;','&').replace('"','')
        if tweetstring != "":
            endindx = 0
            pat = "["+MarkovTweets.punct+"]+"
            for sentencetuple in enumerateSplit(tweetstring,pat):
                sentence, ending = sentencetuple

                endindx += len(sentence)
                words = [x.replace(",","") for x in sentence.split() if x != ""]

                if len(words)>0:
                    if words[0] not in self.model:
                        self.model[words[0]] = MarkovNode(words[0])
                    self.startnode.addNext(words[0])

                    for i in range(0,len(words)-1):
                        word = words[i]
                        nextword = words[i+1]
                        if not word in self.model:
                            self.model[word] = MarkovNode(word)
                        self.model[word].addNext(nextword)

                    lastword = words[-1]

                    if not lastword in self.model:
                        self.model[lastword] = MarkovNode(lastword)

                    self.model[lastword].addNext(ending)

    def makeTweet(self, charlimit=140):
        newtweet = ""
        availiters = 100

        while len(newtweet)==0 and availiters>0:
            pot = self.makeSentence()
            while len(newtweet) + len(pot) < charlimit:
                newtweet += pot
                cancont = (len(newtweet)==0 or newtweet[-1]!=" ")
                if cancont and random.random() < MarkovTweets.CONTINUE_CHANGE:
                    newtweet += " "
                    pot = self.makeSentence()
                else:
                    break
            availiters -= 1

        return newtweet

    def makeSentence(self, charlimit=140):
        sent = ""
        selnode = self.startnode
        while len(sent)<charlimit:
            nxtwrd = selnode.getNext()

            if nxtwrd not in MarkovTweets.punct and nxtwrd != " ":
                if nxtwrd not in self.model:
                    print("[!] " + selnode.word + " -> " + nxtwrd)
                    print(selnode.next)
                    input()
                selnode = self.model[nxtwrd]
                sent += " "+nxtwrd
            else:
                sent += nxtwrd
                break

        return sent

class MarkovNode:
    def __init__(self, word,startnode=False,endnode=False):
        self.word = word
        self.tot = 0
        self.nextobjs = []
        self.next = {}
        self.startnode = startnode
        self.endnode = endnode

    def addNext(self, next):
        if next not in self.next:
            nextobj = [next,0]
            self.nextobjs.append(nextobj)
            self.next[next] = nextobj
        self.next[next][1] += 1
        self.tot += 1

    def getNext(self):
        r = random.randint(0,self.tot)
        for nextobj in self.nextobjs:
            r -= nextobj[1]
            if r<=0:
                return nextobj[0]
        if self.tot==0:
            return " "
        return self.nextobjs[-1][0]

def enumerateSplit(s, pat):
    lastend = 0
    for m in re.finditer(pat,s):
        if m.group(0) is not None:
            yield(s[lastend:m.start()],m.group(0))
            lastend = m.end()
    yield s[lastend:], MarkovTweets.ENDSPECIALCHAR

if __name__=="__main__":
    mt = MarkovTweets("realDonaldTrump_tweets.csv")
    print(mt.makeTweet())