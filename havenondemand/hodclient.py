import requests
import json
import time
from requests.exceptions import ConnectionError
from requests.exceptions import RequestException
from havenondemand.errorcodes import ErrorCode

class HODClient(object):
    hodEndPoint = "http://api.havenondemand.com/1/api/"
    hodJobResult = "http://api.havenondemand.com/1/job/result/"
    hodJobStatus = "http://api.havenondemand.com/1/job/status/"
    hodBatchJob = "http://api.havenondemand.com/1/job"
    hodCombineAsync = "async/executecombination/"
    hodCombineSync = "sync/executecombination/"
    apiVersion = "v1"
    apiKey = None
    proxy = None

    def __init__(self, apikey, apiversion="v1", **proxy):
        self.apiVersion = apiversion
        self.apiKey = apikey
        self.proxy = proxy

    def set_hod_version(self, newVersion):
        self.apiVersion = newVersion

    def set_hod_api_key(self, newApiKey):
        self.apiKey = newApiKey

    def get_job_result(self, jobId, callback=None, **kwargs):
        queryStr = "%s%s?apikey=%s" % (self.hodJobResult, jobId, self.apiKey)
        try:
            response = requests.get(queryStr, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.GetJobResult(jobId, callback, **kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            print (requests.exceptions)
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)


    def get_job_status(self, jobId, callback=None, **kwargs):
        queryStr = "%s%s?apikey=%s" % (self.hodJobStatus, jobId, self.apiKey)
        try:
            response = requests.get(queryStr, proxies=self.proxy,verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.GetJobStatus(jobId, callback, **kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions, jobId)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)

    def post_request(self, params, hodApp, async, callback=None,**kwargs):
        queryStr = self.hodEndPoint
        if async is True:
            queryStr += "async/%s/%s" % (hodApp, self.apiVersion)
        else:
            queryStr += "sync/%s/%s" % (hodApp, self.apiVersion)
        data = list()
        data.append(("apikey", self.apiKey))
        files = list()
        for key, value in params.items():
            if isinstance(value, list):
                if key == "file":
                    for i, vv in enumerate(value):
                        try:
                            f = open(vv, 'rb')
                            files.append((key, f))
                        except IOError:
                            error = self.__create_error_object(ErrorCode.IO_ERROR, "File not found")
                            if callback is None:
                                return error
                            else:
                                callback(error **kwargs)
                                return
                else:
                    for vv in value:
                        data.append((key, vv))
            else:
                if key == "file":
                    try:
                        f = open(value, 'rb')
                        files = {key: f}
                    except IOError:
                        error = self.__create_error_object(ErrorCode.IO_ERROR, "File not found")
                        if callback is None:
                            return error
                        else:
                            callback(error, **kwargs)
                            return
                else:
                    data.append((key, value))
        try:
            response = requests.post(queryStr, data=data, files=files, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.PostRequest(params,hodApp,async,callback,**kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)

    def get_request(self, params, hodApp, async, callback=None, **kwargs):
        queryStr = self.hodEndPoint
        if async is True:
            queryStr += "async/%s/%s" % (hodApp, self.apiVersion)
        else:
            queryStr += "sync/%s/%s" % (hodApp, self.apiVersion)
        queryStr += "?apikey=%s" % (self.apiKey)
        for key, value in params.items():
            if key == "file":
                error = self.__create_error_object(ErrorCode.INVALID_PARAM, "file resource must be uploaded with PostRequest function")
                if callback is None:
                    return error
                else:
                    callback(error, **kwargs)
                    return
            if isinstance(value, list):
                for vv in value:
                    queryStr += "&%s=%s" % (key, vv)
            else:
                queryStr += "&%s=%s" % (key, value)
        try:
            response = requests.get(queryStr, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.GetRequest(params,hodApp,async,callback,**kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)

    def get_request_combination(self, params, apiname, async, callback=None,**kwargs):
        queryStr = self.hodEndPoint
        if async is True:
            queryStr += "%s%s?apikey=%s" % (self.hodCombineAsync,self.apiVersion, self.apiKey)
        else:
            queryStr += "%s%s?apikey=%s" % (self.hodCombineSync,self.apiVersion, self.apiKey)
        queryStr += "&combination=%s" % apiname
        for key, value in params.items():
            if key == "file":
                error = self.__create_error_object(ErrorCode.INVALID_PARAM, "file resource must be uploaded with post_request_combination function")
                if callback is None:
                    return error
                else:
                    callback(error, **kwargs)
                    return
            if self.__is_json(value): # if its a json -> don't quote
                queryStr += '&parameters={"name":"%s","value":%s}' % (key, value)
            else: # if it's a string -> quote it
                queryStr += '&parameters={"name":"%s","value":"%s"}' % (key, value)
        try:
            response = requests.get(queryStr, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.GetRequest(params,hodApp,async,callback,**kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)

    def post_request_combination(self, params, apiname, async, callback=None,**kwargs):
        queryStr = self.hodEndPoint
        if async is True:
            queryStr += "%s%s?" % (self.hodCombineAsync,self.apiVersion)
        else:
            queryStr += "%s%s?" % (self.hodCombineSync,self.apiVersion)
        data = list()
        data.append(("apikey", self.apiKey))
        data.append(("combination", apiname))
        files = list()
        for key, value in params.items():
            if isinstance(value, list):
                if key == "file":
                    for kk, vv in value :
                        try:
                            f = open(vv, 'rb')
                            files.append(('file_parameters',kk))
                            files.append(('file', f))
                        except IOError:
                            error = self.__create_error_object(ErrorCode.IO_ERROR, "File not found")
                            if callback is None:
                                return error
                            else:
                                callback(error **kwargs)
                                return
                else:
                    for vv in value:
                        data.append((key, vv))
            else:
                if self.__is_json(value): # if its a json -> don't quote
                    param = '{"name":"%s","value":%s}' % (key, value)
                else: # if it's a string -> quote it
                    param = '{"name":"%s","value":"%s"}' % (key, value)
                data.append(("parameters", param))
        try:
            response = requests.post(queryStr, data=data, files=files, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.PostRequest(params,hodApp,async,callback,**kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
# just for test purpose
    def post_request_batch(self, params, callback=None,**kwargs):
        queryStr = self.hodBatchJob
        data = list()
        data.append(("apikey", self.apiKey))
        files = list()
        for key, value in params.items():
            if isinstance(value, list):
                if key == "file":
                    for i, vv in enumerate(value):
                        try:
                            f = open(vv, 'rb')
                            files.append((key, f))
                        except IOError:
                            error = self.__create_error_object(ErrorCode.IO_ERROR, "File not found")
                            if callback is None:
                                return error
                            else:
                                callback(error **kwargs)
                                return
                else:
                    for vv in value:
                        data.append((key, vv))
            else:
                if key == "file":
                    try:
                        f = open(value, 'rb')
                        files = {key: f}
                    except IOError:
                        error = self.__create_error_object(ErrorCode.IO_ERROR, "File not found")
                        if callback is None:
                            return error
                        else:
                            callback(error, **kwargs)
                            return
                else:
                    data.append((key, value))
        try:
            response = requests.post(queryStr, data=data, files=files, proxies=self.proxy, verify=False, timeout=600)
            if response.status_code == 429:
                print ("Throttled, Sleeping 2 seconds")
                time.sleep(2)
                self.PostRequest(params,hodApp,async,callback,**kwargs)
            else:
                jsonObj = self.__validateResponse(response)
                if callback is None:
                    return jsonObj
                else:
                    callback(jsonObj, **kwargs)
        except requests.Timeout:
            error = self.__create_error_object(ErrorCode.TIMEOUT, "timeout", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except requests.HTTPError:
            error = self.__create_error_object(ErrorCode.HTTP_ERROR, "HTTP error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
        except ConnectionError:
            error = self.__create_error_object(ErrorCode.CONNECTION_ERROR, "Connection error", requests.exceptions)
            if callback is None:
                return error
            else:
                callback(error, **kwargs)
# internal functions
    def __validateResponse(self,response):
        if response.status_code != 200:
            try:
                jsonObj = json.loads(response.text)
                return jsonObj
            except ValueError:
                return self.__create_error_object(response.status_code, response.reason, response.text, jobId)
        else:
            try:
                jsonObj = json.loads(response.text)
                return jsonObj
            except ValueError:
                return self.__create_error_object(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text)

    def __create_error_object(self,code, reason, detail="", job_id=""):
        err = {}
        err["error"] = code
        err["reason"] = reason
        err["detail"] = detail
        err["jobID"] = job_id
        jsonStr = json.dumps(err)
        jsonObj = json.loads(jsonStr)
        return jsonObj

    def __is_json(self, string):
        try:
            json.loads(string)
        except ValueError:
            return False
        return True

class HODApps:
    RECOGNIZE_SPEECH = "recognizespeech"
    RECOGNIZE_LICENSE_PLATE = "recognizelicenseplates"
    DETECT_SCENE_CHANGES = "detectscenechanges"

    CANCEL_CONNECTOR_SCHEDULE = "cancelconnectorschedule"
    CONNECTOR_HISTORY = "connectorhistory"
    CONNECTOR_STATUS = "connectorstatus"
    CREATE_CONNECTOR = "createconnector"
    DELETE_CONNECTOR = "deleteconnector"
    RETRIEVE_CONFIG = "retrieveconfig"
    START_CONNECTOR = "startconnector"
    STOP_CONNECTOR = "stopconnector"
    UPDATE_CONNECTOR = "updateconnector"

    EXPAND_CONTAINER = "expandcontainer"
    STORE_OBJECT = "storeobject"
    EXTRACT_TEXT = "extracttext"
    VIEW_DOCUMENT = "viewdocument"

    OCR_DOCUMENT = "ocrdocument"
    RECOGNIZE_BARCODES = "recognizebarcodes"
    DETECT_FACES = "detectfaces"
    RECOGNIZE_IMAGES = "recognizeimages"

    GET_COMMON_NEIGHBORS = "getcommonneighbors"
    GET_NEIGHBORS = "getneighbors"
    GET_NODES = "getnodes"
    GET_SHORTEST_PATH = "getshortestpath"
    GET_SUB_GRAPH = "getsubgraph"
    SUGGEST_LINKS = "suggestlinks"
    SUMMARIZE_GRAPH = "summarizegraph"

    MAP_COORDINAETS = "mapcoordinates"

    CREATE_CLASSIFICATION_OBJECTS = "createclassificationobjects"
    CREATE_POLICY_OBJECTS = "createpolicyobjects"
    DELETE_CLASSIFICATION_OBJECTS = "deleteclassificationobjects"
    DELETE_POLICY_OBJECTS = "deletepolicyobjects"
    RETRIEVE_CLASSIFICATION_OBJECTS = "retrieveclassificationobjects"
    RETRIEVE_POLICY_OBJECTS = "retrievepolicyobjects"
    UPDATE_CLASSIFICATION_OBJECTS = "updateclassificationobjects"
    UPDATE_POLICY_OBJECTS = "updatepolicyobjects"

    DELETE_PREDICTION_MODEL = "deletepredictionmodel"
    GET_PREDICTION_MODEL_DETAILS = "getpredictionmodeldetails"
    PREDICT = "predict"
    RECOMMEND = "recommend"
    TRAIN_PREDICTOR = "trainpredictor"

    CREATE_QUERY_PROFILE = "createqueryprofile"
    DELETE_QUERY_PROFILE = "deletequeryprofile"
    RETRIEVE_QUERY_PROFILE = "retrievequeryprofile"
    UPDATE_QUERY_PROFILE = "updatequeryprofile"

    FIND_RELATED_CONCEPTS = "findrelatedconcepts"
    FIND_SIMILAR = "findsimilar"
    GET_CONTENT = "getcontent"
    GET_PARAMETRIC_VALUES = "getparametricvalues"
    QUERY_TEXT_INDEX = "querytextindex"
    RETRIEVE_INDEX_FIELDS = "retrieveindexfields"

    AUTO_COMPLETE = "autocomplete"
    CLASSIFY_DOCUMENT = "classifydocument"
    EXTRACT_CONCEPTS = "extractconcepts"
    CATEGORIZE_DOCUMENT = "categorizedocument"
    ENTITY_EXTRACTION = "extractentities"
    EXPAND_TERMS = "expandterms"
    HIGHLIGHT_TEXT = "highlighttext"
    IDENTIFY_LANGUAGE = "identifylanguage"
    ANALYZE_SENTIMENT = "analyzesentiment"
    GET_TEXT_STATISTICS = "gettextstatistics"
    TOKENIZE_TEXT = "tokenizetext"

    ADD_TO_TEXT_INDEX = "addtotextindex"
    CREATE_TEXT_INDEX = "createtextindex"
    DELETE_TEXT_INDEX = "deletetextindex"
    DELETE_FROM_TEXT_INDEX = "deletefromtextindex"
    INDEX_STATUS = "indexstatus"
    # public const string LIST_INDEXES = "listindexes" REMOVED
    LIST_RESOURCES = "listresources"
    RESTORE_TEXT_INDEX = "restoretextindex"