from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *


hodClient = HODClient("your-apikey")
parser = HODResponseParser()
hodApp = ""

# callback function
def asyncRequestCompleted(response, **context):
	jobID = parser.parse_jobid(response)
	if jobID is None:
		errorObj = parser.get_last_error()
		for err in errorObj.errors:
			print ("Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail))
	else:
		hodClient.get_job_status(jobID, requestCompleted, **context)

def requestCompleted(response, **context):
	payloadObj = parser.parse_payload(response)
	if payloadObj is None:
		errorObj = parser.get_last_error()
		resp = ""
		for err in errorObj.errors:
			if err.error == ErrorCode.QUEUED:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print ("job is queued. Retry in 2 secs. jobID: " + err.jobID)
				time.sleep(2)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			elif err.error == ErrorCode.IN_PROGRESS:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print ("task is in progress. Retry in 10 secs. jobID: " + err.jobID)
				time.sleep(10)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			else:
				resp += "Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error,err.reason, err.detail, err.jobID)
		print (resp)
	else:
		app = context["hodapp"]
		resp = ""
		if app == HODApps.RECOGNIZE_SPEECH:
			documents = payloadObj["document"]
			for doc in documents:
				resp += doc["content"] + "\n"
			paramArr = {}
			print ("Reconized text:\n" + resp)
			paramArr["text"] = resp
			context["hodapp"] = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, True, asyncRequestCompleted, **context)
			#return
		elif app == HODApps.OCR_DOCUMENT:
			texts = payloadObj["text_block"]
			for text in texts:
				resp += text["text"]
			paramArr = {}
			print ("Reconized text:\n" + resp)
			paramArr["text"] = resp
			context["hodapp"] = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, True, asyncRequestCompleted, **context)
			#return
		elif app == HODApps.ANALYZE_SENTIMENT:
			positives = payloadObj["positive"]
			resp += "Positive:\n"
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
			print ("Sentiment Analysis result:\n" + resp)


hodApp = HODApps.RECOGNIZE_SPEECH
paramArr = {}
paramArr["file"] = "testdata/Machine Learning 101.mp3"

context = {}
context["hodapp"] = hodApp

hodClient.post_request(paramArr, hodApp, async=True, callback=asyncRequestCompleted, **context)