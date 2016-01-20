sys.path.append('../havenondemand')

from hodclient import *

hodClient = HODClient("your-api-key", "v2")

# callback function
def requestCompleted(response, error, **context):
    text = ""
    if error is not None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED or err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print err.reason
                time.sleep(5)
                hodClient.get_job_status(err.jobID, requestCompleted)
            else:
                text += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response is not None:
        entities = response["entities"]
        for entity in entities:
            if entity["type"] == "companies_eng":
                text += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                text += "Place name: " + entity["normalized_text"] + "\n"
            else:
                text += "People name: " + entity["normalized_text"] + "\n"
    print text

def asyncRequestCompleted(jobID, error, **context):
    if error is not None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED or err.error == ErrorCode.IN_PROGRESS:
                print err.reason
                time.sleep(2)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            else:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif jobID is not None:
        hodClient.get_job_status(jobID, requestCompleted, **context)


paramArr = {}
paramArr["url"] = "http://www.cnn.com"
paramArr["unique_entities"] = "true"
paramArr["entity_type"] = ["people_eng","places_eng"]


hodClient.get_request(paramArr, HODApps.ENTITY_EXTRACTION, async=True, callback=asyncRequestCompleted)
