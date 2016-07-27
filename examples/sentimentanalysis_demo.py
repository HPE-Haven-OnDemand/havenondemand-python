from havenondemand.hodclient import *
import sys

hodClient = HODClient("your-api-key")

# callback function
def requestCompleted(response, error, **context):
	resp = ""
	if error is not None:
		for err in error.errors:
			resp += "Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error, err.reason, err.detail, err.jobID)
	elif response is not None:
		app = context["hodapp"]
		if app == HODApps.ANALYZE_SENTIMENT:
			positives = response["positive"]
			resp += "Positive:\n"
			for pos in positives:
				resp += "Sentiment: " + pos["sentiment"] + "\n"
				if pos.get('topic'):
					resp += "Topic: " + pos["topic"] + "\n"
				resp += "Score: " + "%f " % (pos["score"]) + "\n"
				if 'documentIndex' in pos:
					resp += "Doc: " + str(pos["documentIndex"]) + "\n"
			negatives = response["negative"]
			resp += "Negative:\n"
			for neg in negatives:
				resp += "Sentiment: " + neg["sentiment"] + "\n"
				if neg.get('topic'):
					resp += "Topic: " + neg["topic"] + "\n"
				resp += "Score: " + "%f " % (neg["score"]) + "\n"
				if 'documentIndex' in neg:
					resp += "Doc: " + str(neg["documentIndex"]) + "\n"
			aggregate = response["aggregate"]
			resp += "Aggregate:\n"
			resp += "Score: " + "%f " % (aggregate["score"]) + "\n"
			resp += aggregate["sentiment"]
	print (resp)



hodApp = HODApps.ANALYZE_SENTIMENT
paramArr = {}
paramArr["text"] = ["I like tropical fruits","Public parking service in Palo Alto is really awesome","A mountain lion was killed by a local resident in Los Gatos"]
paramArr["lang"] = "eng"

context = {}
context["hodapp"] = hodApp

hodClient.post_request(paramArr, hodApp, async=False, callback=requestCompleted, **context)