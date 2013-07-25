##Functions for sentiment analysis

#Creates dictionary from AFINN file

def sentimentPreprocess():

	doc = open("AFINN-111.txt")

	docLines = doc.readlines()

	for line in range(0, len(docLines)):

		docLines[line] = docLines[line].split()

	sentimentDict = {}

	for line in docLines:

		sentimentDict[line[0]] = line[len(line)-1]

	return sentimentDict

#Runs basic analysis on tweet

def tweetAnalysis(tweet, sentimentDict):

	sentiment = 0

	tweet = tweet.split()

	for word in tweet:

		try:

			sentiment = sentiment + int(sentimentDict[word])

		except KeyError:

			pass

	return sentiment

#Find the strength of relationship between two words

def sentimentComparison(tweetDict, keyword1, keyword2, sentimentDict):

	relationship = 0

	for tweet in tweetDict:

		check1 = 0
		check2 = 0

		actualTweet = tweetDict[tweet]

		actualTweet = actualTweet.split()

		for word in actualTweet:

			if word == keyword1:

				check1 = check1 + 1

			if word == keyword2:

				check2 = check2 + 1

		if check1 > 0 and check2 > 0:

			relationship = relationship + tweetAnalysis(tweetDict[tweet], sentimentDict)

	return relationship
