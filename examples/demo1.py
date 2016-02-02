from havenondemand.hodclient import *

hodClient = HODClient("your-apikey", "v1")

# callback function
def requestCompleted(response,error, **kwargs):
    resp = ""
    if error is not None:
        resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    elif response is not None:
        entities = response["entities"]
        for entity in entities:
            if entity["type"] == "companies_eng":
                resp += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                resp += "Place name: " + entity["normalized_text"] + "\n"
            else:
                resp += "People name: " + entity["normalized_text"] + "\n"
    print (resp)

params = dict()
params["url"] = "http://www.cnn.com"
params["unique_entities"] = "true"
params["entity_type"] = ["people_eng","places_eng","companies_eng"]

hodClient.get_request(params, HODApps.ENTITY_EXTRACTION, False, requestCompleted)