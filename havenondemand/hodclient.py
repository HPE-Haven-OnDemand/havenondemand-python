import requests
import json
import time
from requests.exceptions import ConnectionError

proxyDict = {
	# "http"  : http_proxy,
	# "https" : https_proxy,
	# "ftp"   : ftp_proxy
}
class ErrorCode:
	TIMEOUT = 1600
	IN_PROGRESS = 1610
	QUEUED = 1620
	HTTP_ERROR = 1630
	CONNECTION_ERROR = 1640
	IO_ERROR = 1650
	INVALID_PARAM = 1660
	INVALID_HOD_RESPONSE = 1680

class HODErrorObject:
	error = 0
	reason = ""
	detail = ""
	jobID = ""

class HODErrors:
	errors = []
	def addError(self, error):
		self.errors.append(error)

	def resetErrorList(self):
		self.errors = []

class HODClient(object):
	hodEndPoint = "http://api.havenondemand.com/1/api/"
	hodJobResult = "http://api.havenondemand.com/1/job/result/"
	hodJobStatus = "http://api.havenondemand.com/1/job/status/"
	apiVersion = "v1"
	apiKey = None
	proxy = None
	errorsList = HODErrors()

	def __init__(self, apikey, apiversion="v1", **proxy):
		self.apiVersion = apiversion
		self.apiKey = apikey
		self.proxy = proxy

	def get_last_error(self):
		return self.errorsList;

	def get_job_result(self, jobId, callback=None, **kwargs):
		queryStr = "%s%s?apikey=%s" % (self.hodJobResult, jobId, self.apiKey)
		try:
			response = requests.get(queryStr, self.proxy, verify=False, timeout=600)
			if response.status_code == 429:
				print ("Throttled, Sleeping 2 seconds")
				time.sleep(2)
				self.GetJobResult(jobId, callback, **kwargs)
			elif response.status_code != 200:
				try:
					jsonObj = json.loads(response.text)
					self.__parseHODResponse(jsonObj)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList, **kwargs)
				except ValueError:
					self.__createErrorObject(response.status_code, response.reason, response.text, jobId)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
			else:
				try:
					jsonObj = json.loads(response.text)
					resp = self.__parseHODResponse(jsonObj)
					# these statuses won't happen in get result request. But the code is for just in case.
					if resp == "queued" or resp == "inprogress" or resp == "errors":
						if callback is None:
							return None
						else:
							callback(None, self.errorsList, **kwargs)
					else:
						if callback is None:
							return resp
						else:
							callback(resp, None, **kwargs)
				except ValueError:
					self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text, jobId)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "timeout", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except requests.HTTPError:
			self.__createErrorObject(ErrorCode.HTTP_ERROR, "HTTP error", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)


	def get_job_status(self, jobId, callback=None, **kwargs):
		queryStr = "%s%s?apikey=%s" % (self.hodJobStatus, jobId, self.apiKey)
		try:
			response = requests.get(queryStr, self.proxy, verify=False, timeout=600)
			if response.status_code == 429:
				print ("Throttled, Sleeping 2 seconds")
				time.sleep(2)
				self.GetJobStatus(jobId, callback, **kwargs)
			elif response.status_code != 200:
				try:
					jsonObj = json.loads(response.text)
					self.__parseHODResponse(jsonObj)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList, **kwargs)
				except ValueError:
					self.__createErrorObject(response.status_code, response.reason, response.text, jobId)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
			else:
				try:
					jsonObj = json.loads(response.text)
					resp = self.__parseHODResponse(jsonObj)
					if resp == "queued" or resp == "inprogress" or resp == "errors":
						if callback is None:
							return None
						else:
							callback(None, self.errorsList, **kwargs)
					else:
						if callback is None:
							return resp
						else:
							callback(resp, None, **kwargs)
				except ValueError:
					self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text, jobId)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "timeout", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except requests.HTTPError:
			self.__createErrorObject(ErrorCode.HTTP_ERROR, "HTTP error", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error", "", jobId)
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)


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
							self.__createErrorObject(ErrorCode.IO_ERROR, "File not found")
							if callback == None:
								return None
							else:
								callback(None, self.errorsList, **kwargs)
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
						self.__createErrorObject(ErrorCode.IO_ERROR, "File not found")
						if callback is None:
							return None
						else:
							callback(None, self.errorsList, **kwargs)
							return
				else:
					data.append((key, value))
		try:
			response = requests.post(queryStr, data=data, files=files, proxies=self.proxy, verify=False, timeout=600)
			if response.status_code == 429:
				print ("Throttled, Sleeping 2 seconds")
				time.sleep(2)
				self.PostRequest(params,hodApp,async,callback,**kwargs)
			elif response.status_code != 200:
				try:
					jsonObj = json.loads(response.text)
					self.__parseHODResponse(jsonObj)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList, **kwargs)
				except ValueError:
					self.__createErrorObject(response.status_code, response.reason)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
			else:
				if async is False:
					try:
						jsonObj = json.loads(response.text)
						resp = self.__parseHODResponse(jsonObj)
						if resp == "queued" or resp == "inprogress" or resp == "errors":
							if callback is None:
								return None
							else:
								callback(None, self.errorsList,**kwargs)
						else:
							if callback is None:
								return resp
							else:
								callback(resp, None,**kwargs)
					except ValueError:
						self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text)
						if callback is None:
							return None
						else:
							callback(None, self.errorsList,**kwargs)
				else:
					try:
						jsonObj = json.loads(response.text)
						jobID = self.__parseJobId(jsonObj)
						if jobID == "errors":
							if callback is None:
								return None
							else:
								callback(None, self.errorsList,**kwargs)
						else:
							if callback is None:
								return jsonObj #jobID
							else:
								callback(jobID, None,**kwargs)
					except ValueError:
						self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text)
						if callback is None:
							return None
						else:
							callback(None, self.errorsList,**kwargs)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "Request timeout")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except requests.HTTPError:
			self.__createErrorObject(ErrorCode.HTTP_ERROR, "HTTP error")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)
		except requests.ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList, **kwargs)


	def get_request(self, params, hodApp, async, callback=None, **kwargs):
		queryStr = self.hodEndPoint
		if async is True:
			queryStr += "async/%s/%s" % (hodApp, self.apiVersion)
		else:
			queryStr += "sync/%s/%s" % (hodApp, self.apiVersion)
		queryStr += "?apikey=%s" % (self.apiKey)
		for key, value in params.items():
			if key == "file":
				self.__createErrorObject(ErrorCode.INVALID_PARAM, "file resource must be uploaded with PostRequest function")
				if callback is None:
					return None
				else:
					callback(None, self.errorsList, **kwargs)
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
			elif response.status_code != 200:
				try:
					jsonObj = json.loads(response.text)
					self.__parseHODResponse(jsonObj)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList, **kwargs)
				except ValueError:
					self.__createErrorObject(response.status_code, response.reason)
					if callback is None:
						return None
					else:
						callback(None, self.errorsList,**kwargs)
			else:
				if async is False:
					try:
						jsonObj = json.loads(response.text)
						resp = self.__parseHODResponse(jsonObj)
						if resp == "queued" or resp == "inprogress" or resp == "errors":
							if callback is None:
								return None
							else:
								callback(None, self.errorsList,**kwargs)
						else:
							if callback is None:
								return resp
							else:
								callback(resp, None,**kwargs)
					except ValueError:
						self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text)
						if callback is None:
							return None
						else:
							callback(None, self.errorsList,**kwargs)
				else:
					try:
						jsonObj = json.loads(response.text)
						jobID = self.__parseJobId(jsonObj)
						if jobID == "errors":
							if callback is None:
								return None
							else:
								callback(None, self.errorsList,**kwargs)
						else:
							if callback is None:
								return jsonObj #jobID
							else:
								callback(jobID, None,**kwargs)
					except ValueError:
						self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Response is not a json string.", response.text)
						if callback is None:
							return None
						else:
							callback(None, self.errorsList,**kwargs)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "Request timeout")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList,**kwargs)
		except requests.HTTPError:
			self.__createErrorObject(ErrorCode.HTTP_ERROR, "HTTP error")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList,**kwargs)
		except requests.ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error")
			if callback is None:
				return None
			else:
				callback(None, self.errorsList,**kwargs)

	def __createErrorObject(self,code, reason, detail="", jobID=""):
		self.errorsList.resetErrorList()
		err = HODErrorObject()
		err.error = code
		err.reason = reason
		err.detail = detail
		err.jobID = jobID
		self.errorsList.addError(err)

	def __parseHODResponse(self,jsonObj):
		self.errorsList.resetErrorList()
		if "actions" in jsonObj:
			actions = jsonObj["actions"]
			status = actions[0]["status"]
			if status == "queued":
				self.__createErrorObject(ErrorCode.QUEUED, "Task is queued","", jsonObj["jobID"])
				return "queued"
			elif status == "in progress":
				self.__createErrorObject(ErrorCode.IN_PROGRESS, "Task is in progress","", jsonObj["jobID"])
				return "inprogress"
			elif status == "failed":
				errors = actions[0]["errors"]
				for error in errors:
					err = HODErrorObject()
					err.error = error["error"]
					err.reason = error["reason"]
					if "detail" in error:
						err.detail = error["detail"]
					self.errorsList.addError(err)
				return "errors"
			else:
				return actions[0]["result"]
		else:
			if "error" in jsonObj:
				detail = ""
				if "detail" in jsonObj:
					detail = jsonObj["detail"]
				self.__createErrorObject(jsonObj["error"], jsonObj["reason"],detail)
				return "errors"
			else:
				return jsonObj

	def __parseJobId(self, jsonObj):
		if "error" in jsonObj:
			detail = ""
			if "detail" in jsonObj:
				detail = jsonObj["detail"]
			self.__createErrorObject(jsonObj["error"], jsonObj["reason"],detail)
			return "errors"
		else:
			return jsonObj["jobID"]

class HODApps:
	RECOGNIZE_SPEECH = "recognizespeech"

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

	ANOMALY_DETECTION = "anomalydetection"
	TREND_ANALYSIS = "trendanalysis"

	CREATE_CLASSIFICATION_OBJECTS = "createclassificationobjects"
	CREATE_POLICY_OBJECTS = "createpolicyobjects"
	DELETE_CLASSIFICATION_OBJECTS = "deleteclassificationobjects"
	DELETE_POLICY_OBJECTS = "deletepolicyobjects"
	RETRIEVE_CLASSIFICATION_OBJECTS = "retrieveclassificationobjects"
	RETRIEVE_POLICY_OBJECTS = "retrievepolicyobjects"
	UPDATE_CLASSIFICATION_OBJECTS = "updateclassificationobjects"
	UPDATE_POLICY_OBJECTS = "updatepolicyobjects"

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
	TOKENIZE_TEXT = "tokenizetext"

	ADD_TO_TEXT_INDEX = "addtotextindex"
	CREATE_TEXT_INDEX = "createtextindex"
	DELETE_TEXT_INDEX = "deletetextindex"
	DELETE_FROM_TEXT_INDEX = "deletefromtextindex"
	INDEX_STATUS = "indexstatus"
	# public const string LIST_INDEXES = "listindexes" REMOVED
	LIST_RESOURCES = "listresources"
	RESTORE_TEXT_INDEX = "restoretextindex"