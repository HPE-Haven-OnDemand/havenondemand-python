from havenondemand.hodclient import *

hodClient = HODClient("API_KEY")

# callback function
def asyncRequestCompleted(jobID, error, **context):
    if error is not None:
        for err in error.errors:
            print ("Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail))
    elif jobID is not None:
        hodClient.get_job_status(jobID, requestCompleted, **context)

def requestCompleted(response, error, **context):
	if error is not None:
		for err in error.errors:
			if err.error == ErrorCode.QUEUED:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print ("job is queued. Retry in 10 secs. jobID: " + err.jobID)
				time.sleep(10)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			elif err.error == ErrorCode.IN_PROGRESS:
				# wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
				print ("task is in progress. Retry in 20 secs. jobID: " + err.jobID)
				time.sleep(20)
				hodClient.get_job_status(err.jobID, requestCompleted, **context)
				return
			else:
				resp += "Error code: %d \nReason: %s \nDetails: %s\njobID: %s\n" % (err.error,err.reason, err.jobID)
	else:
		hodapp = context["hodapp"]
		resp = ""
		if hodapp == HODApps.RECOGNIZE_SPEECH:
			documents = response["document"]
			for doc in documents:
				resp += doc["content"] + "\n"
			paramArr = {}
			paramArr["text"] = resp
			hodApp = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, False, requestCompleted, **context)
			context["hodapp"] = HODApps.ENTITY_EXTRACTION
			paramArr["entity_type"] = "companies_eng"
			hodClient.post_request(paramArr, HODApps.ENTITY_EXTRACTION, False, requestCompleted, **context)
			return
		elif app == HODApps.OCR_DOCUMENT:
			texts = response["text_block"]
			for text in texts:
				resp += text["text"]
			print (resp)
			paramArr = {}
			paramArr["text"] = resp
			context["hodapp"] = HODApps.ANALYZE_SENTIMENT
			hodClient.post_request(paramArr, HODApps.ANALYZE_SENTIMENT, False, requestCompleted, **context)
			context["hodapp"] = HODApps.ENTITY_EXTRACTION
			paramArr["entity_type"] = "companies_eng"
			hodClient.post_request(paramArr, HODApps.ENTITY_EXTRACTION, False, requestCompleted, **context)
			return
		elif app == HODApps.ANALYZE_SENTIMENT:
			positives = response["positive"]
			resp += "Positive:\n"
			for pos in positives:
				if pos.get('sentiment'):
					resp += "Sentiment: " + pos["sentiment"] + "\n"
				if pos.get('topic'):
					resp += "Topic: " + pos["topic"] + "\n"
				resp += "Score: " + "%f " % (pos["score"]) + "\n"
			negatives = response["negative"]
			resp += "Negative:\n"
			for neg in negatives:
				if neg.get('sentiment'):
					resp += "Sentiment: " + neg["sentiment"] + "\n"
				if neg.get('topic'):
					resp += "Topic: " + neg["topic"] + "\n"
				resp += "Score: " + "%f " % (neg["score"]) + "\n"
			aggregate = response["aggregate"]
			resp += "Aggregate:\n"
			resp += "Sentiment: " + aggregate["sentiment"] + "\n"
			resp += "Score: " + "%f " % (aggregate["score"])
			print (resp)
		elif app == HODApps.ENTITY_EXTRACTION:
			print (response)

hodApp = HODApps.RECOGNIZE_SPEECH
paramArr = {}
if hodApp == HODApps.RECOGNIZE_SPEECH:
	#paramArr["url"] = "http://www.marcelopio.com/memory.mp4"
	paramArr["file"] = "testdata/Machine Learning 101.mp3"
	paramArr["language"] = "en-GB"
elif hodApp == HODApps.OCR_DOCUMENT:
	paramArr["file"] = "testdata/review.jpg"
	paramArr["mode"] = "document_photo"

context = {}
context["hodapp"] = hodApp

hodClient.post_request(paramArr, hodApp, async=True, callback=asyncRequestCompleted, **context)