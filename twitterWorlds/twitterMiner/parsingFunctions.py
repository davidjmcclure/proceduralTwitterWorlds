import string
import re
import math

from nltk.corpus import stopwords
from nltk.corpus import reuters

def stopwordRemover(stringWithStopwords, query):

	queryList = query.split()

	STOPWORDS = ['a','able','about','across','after','all','almost','also','am','among',
'an','and','any','are','as','at','be','because','been','but','by','can',
'cannot','could','dear','did','do','does','either','else','ever','every',
'for','from','get','got','had','has','have','he','her','hers','him','his',
'how','however','i','if','in','into','is','it','its','just','least','let',
'like','likely','may','me','might','most','must','my','neither','no','nor',
'not','of','off','often','on','only','or','other','our','own','rather','said',
'say','says','she','should','since','so','some','than','that','the','their',
'them','then','there','these','they','this','tis','to','too','twas','us',
'wants','was','we','were','what','when','where','which','while','who',
'whom','why','will','with','would','yet','you','your', 'rt', '...','"',
'via','|','-', '&amp','de','la','i\'m','won\'t']

	for word in queryList:

		STOPWORDS.append(word)
		STOPWORDS.append(word + 's')
		STOPWORDS.append(word + '\'s')

	stringWithoutStopwords = []
	stringWithStopwords = re.sub('[...]', ' ', stringWithStopwords)
	stringWithStopwords.translate(None, string.punctuation)
	stringWithStopwords = stringWithStopwords.split()

	for word in stringWithStopwords:
		if word.lower() not in stopwords.words('english') and word.lower() not in STOPWORDS and word.lower() not in stopwords.words('spanish'):
			if word.find('#') == -1 and word.find('@') == -1 and word.find(query) == -1 and word.find('http') == -1 and word.find('\\x') == -1 and word.find('&') == -1:
				word = re.sub('[!@#$.:,;?\]\[]()', '', word)
				stringWithoutStopwords.append(word.lower())

	newString = " ".join(stringWithoutStopwords)
	return newString

def countWords(tweetDict):

	wordCount = {}
	for tweet in tweetDict:
		sentence = tweetDict[tweet].split()
		for word in sentence:
			if word in wordCount:
				wordCount[word] = wordCount[word] + 1

			else:
				wordCount[word] = 1

	return wordCount

def tfidf(word, wordCount):

	docCount = len(reuters.fileids())

	wordCountCorpus = 0
	count = 0
	for doc in reuters.fileids():
		count = count + 1
		present = 0
		for word2 in reuters.words(doc):
			if word.lower() == word2.lower():
				present = 1
				break

		if present == 1:
			wordCountCorpus == wordCountCorpus + 1

		if count == 200:
			break

	tf = wordCount
	idf = math.log(docCount/(1 + wordCountCorpus))

	tfidf = tf * idf

	return tfidf

def duplicateRemover(tweetDict):

	tmp = [(k, tweetDict[k]) for k in tweetDict]
	tweetDict = {}
	for k, v in tmp:
		if v in tweetDict.values():
			continue
		tweetDict[k] = v

	return tweetDict

