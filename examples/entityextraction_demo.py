from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *

hodClient = HODClient("your-apikey", "v2")
parser = HODResponseParser()

# callback function
def requestCompleted(response, **context):
    text = ""
    payloadObj = parser.parse_payload(response)
    if payloadObj is None:
        errorObj = parser.get_last_error()
        for err in errorObj.errors:
            if err.error == ErrorCode.QUEUED or err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print (err.reason)
                time.sleep(5)
                hodClient.get_job_status(err.jobID, requestCompleted)
            else:
                text += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    else:
        entities = payloadObj["entities"]
        for entity in entities:
            if entity["type"] == "companies_eng":
                text += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                text += "Place name: " + entity["normalized_text"] + "\n"
            else:
                text += "People name: " + entity["normalized_text"] + "\n"
    print (text)

def asyncRequestCompleted(response, **context):
    jobID = parser.parse_jobid(response)
    if jobID is None:
		errorObj = parser.get_last_error()
		for err in errorObj.errors:
			print ("Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail))
	else:
		hodClient.get_job_result(jobID, requestCompleted, **context)


paramArr = {}
paramArr["url"] = "http://www.cnn.com"
paramArr["unique_entities"] = "true"
paramArr["entity_type"] = ["people_eng","places_eng"]


hodClient.get_request(paramArr, HODApps.ENTITY_EXTRACTION, async=True, callback=asyncRequestCompleted)