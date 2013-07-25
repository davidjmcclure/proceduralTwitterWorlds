from miner import *
from parsingFunctions import *
from sentimentAnalyser import *
from massSpringModel import *

import itertools
import nltk
import Queue

def analysis(q, query, window, width, height):

	tweetDict = miner(query)
	for keys in tweetDict:
		tweetDict[keys] = stopwordRemover(tweetDict[keys], query)

	tweetDict = duplicateRemover(tweetDict)
	wordCount = countWords(tweetDict)
	sentimentDict = sentimentPreprocess()

	wordCount = (sorted(wordCount.items(), key=lambda item: item[1]))[-30:]

	tfidfScore = {}

	for key in wordCount:
		score = tfidf(key[0], key[1])
		tfidfScore[key[0]] = (score)

	keywordList = sorted(tfidfScore.items(), key=lambda item: item[1])[-15:]

	print keywordList

	queryKeywordRelationship = {}

	for word in keywordList:

		queryKeywordRelationship[word[0]] = sentimentComparison(tweetDict, query, word[0], sentimentDict)

	relationshipList = []

	for pair in itertools.combinations(keywordList, 2):

		if sentimentComparison(tweetDict, pair[0][0], pair[1][0], sentimentDict) != 0:

			relationshipList.append((pair[0][0], pair[1][0], sentimentComparison(tweetDict, pair[0][0], pair[1][0], sentimentDict)))

	particleDict = massSpringModel(relationshipList, window, width, height)

	twitterData = {}
	twitterData['particles'] = particleDict
	twitterData['querykeywords'] = queryKeywordRelationship

	q.put(twitterData)
