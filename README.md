# HODClient Library for Python. V2.0

----
## Overview
HODClient for Python is a utility class, which helps you easily integrate your Python project with HPE Haven OnDemand Services.

Version V2.0 also supports asynchronous call which returns server response via a callback function.

Code your Python app with PyCharm. Get it from https://www.jetbrains.com/pycharm/download

----
## Integrate HODClient into Python project
1. Download the HODClient library for Python.
2. Unzip and copy the whole havenondemand folder to your project folder.

*OR*

1. To install the latest version directly from this github repo:
```
pip install git+https://github.com/HPE-Haven-OnDemand/havenondemand-python-v2.0
```

----
## API References
**Constructor**
```
HODClient("apiKey", version = "v1")
```

*Description:* 
* Creates and initializes a HODClient object.

*Parameters:*
* apiKey: your developer apikey.
* version: Haven OnDemand API version. Currently it only supports version 1. Thus, the default value is "v1".

*Example code:*
```
from havenondemand.hodclient import *
hodClient = HODClient("your-apikey")
```
----
**Function get_request**

    get_request(params, hodApp, async, callback, **kwargs)

*Description:* 
* Sends a HTTP GET request to call an Haven OnDemand API.

*Parameters:*
* params: a dictionary dict() containing key/value pair parameters to be sent to a Haven OnDemand API, where the keys are the parameters of that Haven OnDemand API.

>Note: 

>For a parameter with its type is an array<>, the parameter must be defined in an array []. 
>E.g.:
## 
    params = dict()
    params["url"] = "http://www.cnn.com"
    params["entity_type"] = ["people_eng","places_eng","companies_eng"]


* hodApp: a string to identify a Haven OnDemand API. E.g. "extractentities". Current supported APIs are listed in the HODApps class.
* async: True | False. Specifies API call as Asynchronous or Synchronous.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server. If callback is omitted or is None, this function will return a response.
* \*\*kwargs (optional): a dictionary that holds any custom paramters. The parameter \*\*kwargs will be sent back thru the provided callback function.

*Response:* 
* If callback function is provided, the response from the server will be returned via the provided callback function
* If the callback is omitted or is None, the response from the server will be returned from this function. If there is an error occurs, the response will be None and the get_last_error() function will return a list of errors.

*Example code:*
```
# Call the Entity Extraction API synchronously to find people, places and companies from CNN and BBC websites.

#E.g. 1: Calling HODClient function with a callback function

# callback function
def requestCompleted(response, error, **kwargs):
    if error != None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                time.sleep(10)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            elif err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print "task is in progress. Retry in 20 secs. jobID: " + err.jobID
                time.sleep(20)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            else:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        entities = response["entities"]
        text = ""
        for entity in entities:
            if entity["type"] == "companies_eng":
                text += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                text += "Place name: " + entity["normalized_text"] + "\n"
            else:
                text += "People name: " + entity["normalized_text"] + "\n"
        print text

params = dict()
params["url"] = ["http://www.cnn.com","http://www.bbc.com"]
params["entity_type"] = ["people_eng","places_eng","companies_eng"]
    
params["unique_entities"] = "true"
    
hodClient.get_request(params, HODApps.ENTITY_EXTRACTION, False, requestCompleted)


#E.g. 2: Calling HODClient function without a callback function
params = dict()
params["url"] = ["http://www.cnn.com","http://www.bbc.com"]
params["entity_type"] = ["people_eng","places_eng","companies_eng"]
    
params["unique_entities"] = "true"
    
response = hodClient.get_request(params, HODApps.ENTITY_EXTRACTION, False)

if response is None:
    error = hodClient.get_last_error()
    for err in error.errors:
        print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
else:
    entities = response["entities"]
    text = ""
    for entity in entities:
        if entity["type"] == "companies_eng":
            text += "Company name: " + entity["normalized_text"] + "\n"
        elif entity["type"] == "places_eng":
            text += "Place name: " + entity["normalized_text"] + "\n"
        else:
            text += "People name: " + entity["normalized_text"] + "\n"
    print text
```

**Function post_request**
``` 
post_request(params, hodApp, async, callback, **kwargs)
```
*Description:* 
* Sends a HTTP POST request to call a Haven OnDemand API.

*Parameters:*
* params: a dictionary dict() containing key/value pair parameters to be sent to a Haven OnDemand API, where the keys are the parameters of that Haven OnDemand API.

>Note: 

>For a parameter with its type is an array<>, the parameter must be defined in an array []. 
>E.g.:
``` 
params = dict()
params["url"] = "http://www.cnn.com"
params["entity_type"] = ["people_eng","places_eng","companies_eng"]
```

* hodApp: a string to identify an Haven OnDemand API. E.g. "ocrdocument". Current supported apps are listed in the HODApps class.
* async: True | False. Specifies API call as Asynchronous or Synchronous.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server. If callback is omitted or is None, this function will return a response.
* \*\*kwargs (optional): a dictionary that holds any custom paramters. The parameter \*\*kwargs will be sent back thru the provided callback function.

*Response:* 
* If callback function is provided, the response from the server will be returned via the provided callback function
* If the callback is omitted or is None, the response from the server will be returned from this function. If there is an error occurs, the response will be None and the get_last_error() function will return a list of errors.

*Example code:*

```
# Call the OCRDocument API asynchronously to scan text from an image.

#E.g. 1: Calling HODClient function with a callback function

# callback function
def asyncRequestCompleted(jobID, error, **kwargs):
    if error != None:
        for err in error.errors:
            result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
            print result
    elif jobID != None:
        hodClient.get_job_result(jobID, requestCompleted, **kwargs)

# callback function
def requestCompleted(response, error, **kwargs):
    if error != None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                time.sleep(10)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            elif err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print "task is in progress. Retry in 20 secs. jobID: " + err.jobID
                time.sleep(20)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            else:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        texts = response["text_block"]
        for text in texts:
            print "Recognized text: " + text["text"]
    
params = {}
params["file"] = "testdata/review.jpg",
params["mode"] = "document_photo"

hodClient.post_request(params, HODApps.OCR_DOCUMENT, True, asyncRequestCompleted)


#E.g. 2: Calling HODClient function without a callback function

params = {}
params["file"] = "testdata/review.jpg",
params["mode"] = "document_photo"

response = hodClient.post_request(params, HODApps.OCR_DOCUMENT, True)

if response is None:
    error = hodClient.get_last_error();
    for err in error.errors:
        print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
else:
    response = hodClient.get_job_result(response['jobID'])
    if response is None:
        for err in error.errors:
            print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    else:
        texts = response["text_block"]
        for text in texts:
            print "Recognized text: " + text["text"]
    
```    

**Function get_job_result**
```
get_job_result(jobID, callback, **kwargs)
```
*Description:*
* Sends a request to Haven OnDemand to retrieve content identified by a job ID. This function acts like a synchronous call, it waits until the result is ready and returns the response or times out for a long operation job.

*Parameter:*
* jobID: the job ID returned from an Haven OnDemand API upon an asynchronous call.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server. If the callback is omitted or is None, this function will return a response.
* \*\*kwargs (optional): a dictionary that holds any custom paramters. The parameter \*\*kwargs will be sent back thru the provided callback function.

*Response:* 
* If callback function is provided, the response from the server will be returned via the provided callback function
* If the callback is omitted or is None, the response from the server will be returned from this function. If there is an error occurs, the response will be None and the get_last_error() function will return a list of errors.

*Example code:*
``` 
# Call get_job_result function to get content from Haven OnDemand server.

# callback function
def requestCompleted(response, error, **kwargs):
    if error != None:
        for err in error.errors:
            resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        # walk thru the response

hodClient.get_job_result(jobID, requestCompleted)
```

**Function get_job_status**
```
get_job_status(jobID, callback, **kwargs)
```
*Description:*
* Sends a request to Haven OnDemand to retrieve status of a job identified by a job ID. If the job is completed, the response will be the result of that job. Otherwise, the response will be None and the current status of the job will be held in the error object. 

*Parameter:*
* jobID: the job ID returned from an Haven OnDemand API upon an asynchronous call.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server. If the callback is omitted or is None, this function will return a response.
* \*\*kwargs (optional): a dictionary that holds any custom paramters. The parameter \*\*kwargs will be sent back thru the provided callback function.

*Response:* 
* If callback function is provided, the response from the server will be returned via the provided callback function
* If the callback is omitted or is None, the response from the server will be returned from this function. If there is an error occurs, the response will be None and the get_last_error() function will return a list of errors.

*Example code:*
``` 
# Call get_job_status function to get content from Haven OnDemand server.

# callback function
def requestCompleted(response, error, **kwargs):
    if error != None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                time.sleep(10)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            elif err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print "task is in progress. Retry in 20 secs. jobID: " + err.jobID
                time.sleep(20)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            else:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        # walk thru the response

hodClient.get_job_status(jobID, requestCompleted)
```

**Function get_last_error**
```
get_last_error()
```
*Description:*
* Get the latest error list which describe the errors happened during an operation

*Parameter:* None

*Response:* 
* An array of HODErrorObject

*Example code:*
```
error = hodClient.get_last_error();
for err in error.errors:
    print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
```

## Define and implement callback functions

# 
When you call the get_request() or post_request() with the async=True, the response in a callback function will be a string containing a jobID.
```
def asyncRequestCompleted(response, error, **kwargs):
    # check error

    # call get_job_result function with the jobID
```    
# 
When you call the get_request() or post_request() with the async=False or call the get_job_result(), the response in a callback function will be a JSON object of the actual result from the service.
```
def requestCompleted(response, error, **kwargs):
    # check error
        
    # walk thru the response
```

## Demo code 1: 

**Call the Entity Extraction API to extract people and places from cnn.com website with a synchronous GET request**
```
from havenondemand.hodclient import *

hodClient = HODClient("your-apikey")

# callback function
def requestCompleted(response,error, **kwargs):
    resp = ""
    if error != None:
        resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        entities = response["entities"]
        for entity in entities:
            if entity["type"] == "companies_eng":
                resp += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                resp += "Place name: " + entity["normalized_text"] + "\n"
            else:
                resp += "People name: " + entity["normalized_text"] + "\n"
    print resp

params = {}
params["url"] = "http://www.cnn.com"
params["unique_entities"] = "true"
params["entity_type"] = ["people_eng","places_eng","companies_eng"]

hodClient.get_request(params, HODApps.ENTITY_EXTRACTION, False, requestCompleted)
```

## Demo code 2:
 
**Call the OCR Document API to scan text from an image with an asynchronous POST request**
```
from havenondemand.hodclient import *

hodClient = HODClient("your-apikey")

# callback function
def asyncRequestCompleted(jobID, error, **context):
    if error != None:
        resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        hodClient.get_job_status(jobID, requestCompleted, **context)

# callback function
def requestCompleted(response, error, **context):
    print context
    resp = ""
    if error != None:
        for err in error.errors:
            if err.error == ErrorCode.QUEUED:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
		print "task is in queue. Retry in 10 secs. jobID: " + err.jobID
                time.sleep(10)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            elif err.error == ErrorCode.IN_PROGRESS:
                # wait for some time then call GetJobStatus or GetJobResult again with the same jobID from err.jobID
                print "task is in progress. Retry in 20 secs. jobID: " + err.jobID
                time.sleep(20)
                hodClient.get_job_status(err.jobID, requestCompleted, **context)
            else:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response != None:
        texts = response["text_block"]
        for text in texts:
            resp += "Recognized text: " + text["text"]
    print resp

params = {}
params["file"] = "testdata/review.jpg"
params["mode"] = "document_photo"

context = {}
context["id"] = "some id"
context["desc"] = "some desc"

hodClient.post_request(params, HODApps.OCR_DOCUMENT, async=True, callback=asyncRequestCompleted, **context)
```
## License
Licensed under the MIT License.