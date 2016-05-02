# Python client library for Haven OnDemand

Official Python client library to help with calling [Haven OnDemand APIs](http://havenondemand.com).

## What is Haven OnDemand?
Haven OnDemand is a set of over 70 APIs for handling all sorts of unstructured data. Here are just some of our APIs' capabilities:
* Speech to text
* OCR
* Text extraction
* Indexing documents
* Smart search
* Language identification
* Concept extraction
* Sentiment analysis
* Web crawlers
* Machine learning

For a full list of all the APIs and to try them out, check out https://www.havenondemand.com/developer/apis

## Installation
To install, run the following command
```
pip install havenondemand
```

To install the latest version from this github repo

```
pip install git+https://github.com/HPE-Haven-OnDemand/havenondemand-python
```

## Importing into your app and initializing the client
Place the following where you are including libraries
```python
from havenondemand.hodclient import *
client = HODClient("API_KEY", version="v1")
```
where you replace "API_KEY" with your API key found [here](https://www.havenondemand.com/account/api-keys.html). `version` is an *optional* parameter which can be either `"v1"` or `"v2"`, but defaults to `"v1"` if not specified.

## Sending requests to the API - POST and GET
You can send requests to the API with either a POST or GET request, where POST requests are required for uploading files and recommended for larger size queries and GET requests are recommended for smaller size queries.

### POST request
```python
client.post_request(params, hodApp, async, callback, **kwargs)
```
* `params` is a dictionary of parameters passed to the API
* `hodApp` is the endpoint of the API you are calling (see this [list]() for available endpoints and our [documentation](https://dev.havenondemand.com/apis) for descriptions of each of the APIs)
* `async` specifies if you are calling the API asynchronously or synchronously, which is either `True` or `False`, respectively
* `callback` *optional* which is a callback function which is executed when the response from the API is received
* `**kwargs` *optional* a dictionary that holds any custom parameters which is sent back through the provided callback function

### GET request
```python
client.get_request(params, hodApp, async, callback, **kwargs)
```
* `params` is a dictionary of parameters passed to the API
* `hodApp` is the endpoint of the API you are calling (see this [list]() for available endpoints and our [documentation](https://dev.havenondemand.com/apis) for descriptions of each of the APIs)
* `async` specifies if you are calling the API asynchronously or synchronously, which is either `True` or `False`, respectively
* `callback` *optional* which is a callback function which is executed when the response from the API is received
* `**kwargs` *optional* a dictionary that holds any custom parameters which is sent back through the provided callback function

## Synchronous vs Asynchronous
Haven OnDemand's API can be called either synchronously or asynchronously. Users are encouraged to call asynchronously if they are POSTing large files that may require a lot of time to process. If not, calling them synchronously should suffice. For more information on the two, see [here](https://dev.havenondemand.com/docs/AsynchronousAPI.htm).

### Synchronous
To make a synchronous GET request to our Sentiment Analysis API
```python
response = client.get_request({'text': 'I love Haven OnDemand!'}, HODApps.ANALYZE_SENTIMENT, async=False)
```
where the response will be in the `response` dictionary.

### Asynchronous
To make an asynchronous POST request to our Sentiment Analysis API
```python
response_async = post_request({'text': 'I love Haven OnDemand!'}, HODApps.ANALYZE_SENTIMENT, async=True)
jobID = response_async['jobID']
```
which will return back the job ID of your call.

#### Getting the results of an asynchronous request - Status API and Result API

##### Status API
The Status API checks to see the status of your job request. If it is finished processing, it will return the result. If not, it will return you the status of the job.

```python
client.get_job_status(jobID, callback, **kwargs)
```
* `jobID` is the job ID of request returned after performing an asynchronous request
* `callback` *optional* which is a callback function which is executed when the response from the API is received
* `**kwargs` *optional* a dictionary that holds any custom parameters which is sent back through the provided callback function

To get the status, or job result if the job is complete
```python
response = client.get_job_status(jobID)
```

##### Result API
The Result API checks the result of your job request. If it is finished processing, it will return the result. If it not, the call the wait until the result is returned or until it times out. **It is recommended to use the Status API over the Result API to avoid time outs**

```python
client.get_job_result(jobID, callback, **kwargs)
```
* `jobID` is the job ID of request returned after performing an asynchronous request
* `callback` *optional* which is a callback function which is executed when the response from the API is received
* `**kwargs` *optional* a dictionary that holds any custom parameters which is sent back through the provided callback function

To get the result
```python
response = client.get_job_result(jobID)
```

## Using a callback function
Most methods allow optional callback functions which are executed when the response of the API is received.
```python
def requestCompleted(response, error, **kwargs):
  print response

client.post_request({'text': 'I love Haven OnDemand!'}, HODApps.ANALYZE_SENTIMENT, async=False, requestCompleted)
```

## POSTing files
POSTing files is just as easy. Simply include the path to the file you're POSTing in the parameters
```python
response = hodClient.post_request({'file': 'path/to/file.jpg'}, HODApps.OCR_DOCUMENT, async=False)
```

## Examples

### Synchronous Sentiment Analysis GET request
```python
params = {'text': 'I love Haven OnDemand!'}
response = client.get_request(params, HODApps.ANALYZE_SENTIMENT, async=False)
print response
```

### Asynchronous Sentiment Analysis POST request checking response with Result API
```python
params = {'text': 'I love Haven OnDemand!'}
response_async = client.post_request(params, HODApps.ANALYZE_SENTIMENT, async=True)
jobID = response_async['jobID']
response = client.get_job_result(jobID)
print response
```

### Asynchronous Speech Recognition POST request checking response with Status API
*Note: Larger files POSTed to the APIs take some time to process, so if you call the* `get_job_status` *API immediately afterwards, it will respond back with a* `Processing` *result. Allow the API enough time for the completed response.*

```python
params = {'file': 'path/to/file.mp3'}
response_async = client.post_request(params, HODApps.RECOGNIZE_SPEECH, async=True)
jobID = response_async['jobID']
response = client.get_job_status(jobID)
print response
```

### Synchronous OCR Document GET request with callback function
```python
def requestCompleted(response, error, **kwargs):
  print response

params = {'url': 'https://www.havenondemand.com/sample-content/images/bowers.jpg'}
client.get_request(params, HODApps.OCR_DOCUMENT, async=False, requestCompleted)
```

## License
Licensed under the MIT License.
