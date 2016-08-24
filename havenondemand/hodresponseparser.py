import json
from errorcodes import *

class HODResponseParser(object):
	errorsList = HODErrors()
	def get_last_error(self):
		return self.errorsList

	def parse_jobid(self, jsonResponse):
		if jsonResponse.get('jobID'):
			return jsonResponse["jobID"]
		else:
			if jsonResponse.get("error"):
				detail = ""
				if "detail" in jsonResponse:
					detail = jsonResponse["detail"]
				self.__createErrorObject(jsonResponse["error"], jsonResponse["reason"],detail)
				return None
			else:
				self.__createErrorObject(ErrorCode.INVALID_HOD_RESPONSE, "Invalid HOD response","")
				return None

	def parse_payload(self, jsonResponse):
		return self.__parseHODResponse(jsonResponse)

	#internal functions. Not supposed to call from outside classes
	def __parseHODResponse(self,jsonObj):
		self.errorsList.resetErrorList()
		if "actions" in jsonObj:
			actions = jsonObj["actions"]
			status = actions[0]["status"]
			if status == "queued":
				self.__createErrorObject(ErrorCode.QUEUED, "Task is queued","", jsonObj["jobID"])
				return None
			elif status == "in progress":
				self.__createErrorObject(ErrorCode.IN_PROGRESS, "Task is in progress","", jsonObj["jobID"])
				return None
			elif status == "failed":
				errors = actions[0]["errors"]
				for error in errors:
					err = HODErrorObject()
					err.error = error["error"]
					err.reason = error["reason"]
					if "detail" in error:
						err.detail = error["detail"]
					self.errorsList.addError(err)
				return None
			else:
				return actions[0]["result"]
		else:
			if jsonObj.get("error"):
				detail = ""
				if "detail" in jsonObj:
					detail = jsonObj["detail"]
				self.__createErrorObject(jsonObj["error"], jsonObj["reason"],detail)
				return None
			else:
				return jsonObj

	def __createErrorObject(self,code, reason, detail="", jobID=""):
		self.errorsList.resetErrorList()
		err = HODErrorObject()
		err.error = code
		err.reason = reason
		err.detail = detail
		err.jobID = jobID
		self.errorsList.addError(err)
