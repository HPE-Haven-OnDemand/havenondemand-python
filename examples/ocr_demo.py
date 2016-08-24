from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *

hodClient = HODClient("your-apikey", "v1")
parser = HODResponseParser()

hodApp = HODApps.OCR_DOCUMENT
paramArr = {}
paramArr["file"] = "testdata/review.jpg"
paramArr["mode"] = "document_photo"

response = hodClient.post_request(paramArr, hodApp, async=True)
jobID = parser.parse_payload(response)

if jobID is None:
	errorObj = parser.get_last_error()
	for err in errorObj.errors:
		print ("Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail))
else:
	#print (response['jobID'])
	response = hodClient.get_job_result(jobID)
	payloadObj = parser.parse_payload(response)
	if payloadObj is None:
		errorObj = parser.get_last_error()
		for err in errorObj.errors:
			print ("Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error, err.reason, err.detail, err.jobID))
	else:
		texts = response["text_block"]
		resp = ""
		for text in texts:
			resp += "Recognized text: " + text["text"]
		params = dict()
		params["text"] = resp
		response = hodClient.post_request(params, HODApps.ANALYZE_SENTIMENT, False)
		payloadObj = parser.parse_payload(response)
		if payloadObj is None:
			errorObj = parser.get_last_error()
			for err in errorObj.errors:
				print ("Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error, err.reason, err.detail, err.jobID))
		else:
			positives = payloadObj["positive"]
			resp = "Positive:\n"
			for pos in positives:
				resp += "Sentiment: " + pos["sentiment"] + "\n"
				if pos.get('topic'):
					resp += "Topic: " + pos["topic"] + "\n"
				resp += "Score: " + "%f " % (pos["score"]) + "\n"
				if 'documentIndex' in pos:
					resp += "Doc: " + str(pos["documentIndex"]) + "\n"
			negatives = payloadObj["negative"]
			resp += "Negative:\n"
			for neg in negatives:
				resp += "Sentiment: " + neg["sentiment"] + "\n"
				if neg.get('topic'):
					resp += "Topic: " + neg["topic"] + "\n"
				resp += "Score: " + "%f " % (neg["score"]) + "\n"
				if 'documentIndex' in neg:
					resp += "Doc: " + str(neg["documentIndex"]) + "\n"
			aggregate = payloadObj["aggregate"]
			resp += "Aggregate:\n"
			resp += "Sentiment: " + aggregate["sentiment"] + "\n"
			resp += "Score: " + "%f " % (aggregate["score"])
			print (resp)