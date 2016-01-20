sys.path.append('../havenondemand')

from hodclient import *

hodClient = HODClient("your-api-key", "v1")
hodApp = ""

# callback function
def asyncRequestCompleted(jobID, error, **context):
    if error is not None:
        for err in error.errors:
            print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif jobID is not None:
        hodClient.get_job_status(jobID, requestCompleted, **context)

def requestCompleted(response, error, **context):
	resp = ""
	if error is not None:
		for err in error.errors:
			if err.error == ErrorCode.QUEUED:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print "job is queued. Retry in 10 secs. jobID: " + err.jobID
				time.sleep(10)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			elif err.error == ErrorCode.IN_PROGRESS:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print "task is in progress. Retry in 60 secs. jobID: " + err.jobID
				time.sleep(60)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			else:
				resp += "Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error,err.reason, err.jobID)
	elif response is not None:
		app = context["hodapp"]
		if app == HODApps.RECOGNIZE_SPEECH:
			documents = response["document"]
			for doc in documents:
				resp += doc["content"] + "\n"
			paramArr = {}
			paramArr["text"] = resp
			context["hodapp"] = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, True, asyncRequestCompleted, **context)
			return
		elif app == HODApps.OCR_DOCUMENT:
			texts = response["text_block"]
			for text in texts:
				resp += text["text"]
			paramArr = {}
			paramArr["text"] = resp
			context["hodapp"] = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, True, asyncRequestCompleted, **context)
			return
		elif app == HODApps.ANALYZE_SENTIMENT:
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
			resp += "Sentiment: " + aggregate["sentiment"] + "\n"
			resp += "Score: " + "%f " % (aggregate["score"])
			print resp


hodApp = HODApps.OCR_DOCUMENT
paramArr = {}
if hodApp == HODApps.RECOGNIZE_SPEECH:
	paramArr["file"] = "testdata/attendant.mp3"
elif hodApp == HODApps.OCR_DOCUMENT:
	paramArr["file"] = "testdata/review.jpg"
	paramArr["mode"] = "document_photo"

context = {}
context["hodapp"] = hodApp

hodClient.post_request(paramArr, hodApp, async=True, callback=asyncRequestCompleted, **context)
