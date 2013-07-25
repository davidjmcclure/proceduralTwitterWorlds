import string, json, pprint
import urllib
import oauth2 as oauth
import re

##Takes a query and returns a dictionary of twitter results for a search of that query

def miner(query):

	query = re.sub(' ', '%20', query)

	tweetDict = {}

	returnCount = 100
	pagesReturned = 12

	countStatement = "&count=" + str(returnCount)

	searchURL = "https://api.twitter.com/1.1/search/tweets.json?q=" + query + countStatement

##Place keys in here and uncomment
"""
	CONSUMER_KEY = 
	CONSUMER_SECRET = 
	ACCESS_KEY = 
	ACCESS_SECRET = 
"""
	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
	client = oauth.Client(consumer, access_token)

	response, data = client.request(searchURL)

	tweets = json.loads(data)

	Output = open("tweets.txt", "w")

	Output.write("Tweets:" + "\n")
	Output.write("\n")
	Output.write("\n")

	for content in range(0, len(tweets['statuses'])):

		user_name = tweets['statuses'][content]['user']['name'].encode('utf-8')
		text = tweets['statuses'][content]['text'].encode('utf-8')
		tweetDict[user_name] = text
		Output.write(user_name + ":" + "\n")
		Output.write(text + "\n")
		Output.write("\n")

	tweetID = tweets["statuses"][len(tweets["statuses"])-1]["id"]

	for page in range(2, pagesReturned + 1):

		maxID = "&max_id=" + str(tweetID)

		searchURL = "https://api.twitter.com/1.1/search/tweets.json?q=" + query + countStatement + maxID

		response, data = client.request(searchURL)

		tweets = json.loads(data)

		for content in range(0, len(tweets['statuses'])):
			user_name = tweets['statuses'][content]['user']['name'].encode('utf-8')
			text = tweets['statuses'][content]['text'].encode('utf-8')
			tweetDict[user_name] = text
			Output.write(user_name + ":" + "\n")
			Output.write(text + "\n")
			Output.write("\n")

		tweetID = tweets["statuses"][len(tweets["statuses"])-1]["id"]

	print response["x-rate-limit-limit"]
	print response["x-rate-limit-remaining"]

	if int(response["x-rate-limit-remaining"]) < pagesReturned*2:

		print "WARNING: APPROACHING RATE LIMIT. THIS IS RESET EVERY 15 MINUTES, PLEASE TAKE A BREAK."

	return tweetDict

###
#Twitter data format
###
"""
Returns dict:

Keys- search_metadata (dict), statuses(list)

search_metadata:

statues:

returns a dictionary for each list entry

each tweets entry is a dictionary containing many entries containing information about the user

of interest:

the dictionary user and it's key 'name'

the unicode entry text (the actual tweet)

So to access tweet:

tweets["statuses"][user entry number]["text"]

and username:

tweets["statuses"][user entry number]["user"]["name"]

and tweet id:

tweets["statuses"][user entry number]["id"]

"""
###
