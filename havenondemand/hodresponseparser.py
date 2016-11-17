import json
from havenondemand.errorcodes import *

class HODResponseParser(object):
	errorsList = HODErrors()
	def get_last_error(self):
		return self.errorsList

	def parse_jobid(self, jsonResponse):
		self.errorsList.reset_errors()
		if jsonResponse.get('jobID'):
			return jsonResponse["jobID"]
		else:
			if jsonResponse.get("error"):
				detail = ""
				if "detail" in jsonResponse:
					detail = jsonResponse["detail"]
				self.__create_error_object(jsonResponse["error"], jsonResponse["reason"],detail)
				return None
			else:
				self.__create_error_object(ErrorCode.INVALID_HOD_RESPONSE, "Invalid HOD response","")
				return None

	def parse_payload(self, jsonResponse):
		return self.__parse_hod_response(jsonResponse)

	#internal functions. Not supposed to call from outside classes
	def __parse_hod_response(self,jsonObj):
		self.errorsList.reset_errors()
		if jsonObj.get("actions"): #"actions" in jsonObj:
			actions = jsonObj["actions"]
			status = actions[0]["status"]
			if status == "queued":
				self.__create_error_object(ErrorCode.QUEUED, "Task is queued","", jsonObj["jobID"])
				return None
			elif status == "in progress":
				self.__create_error_object(ErrorCode.IN_PROGRESS, "Task is in progress","", jsonObj["jobID"])
				return None
			elif status == "failed":
				errors = actions[0]["errors"]
				for error in errors:
					detail = ""
					job_id = ""
					if "detail" in error:
						detail = error["detail"]
					if "jobID" in error:
						job_id = error["jobID"]
					elif "jobID" in jsonObj:
						job_id = jsonObj["jobID"]
					self.__create_error_object(error["error"], error["reason"],detail, job_id)

				return None
			else:
				return actions[0]["result"]
		else:
			if jsonObj.get("error"):
				detail = ""
				if "detail" in jsonObj:
					detail = jsonObj["detail"]
				self.__create_error_object(jsonObj["error"], jsonObj["reason"],detail)
				return None
			else:
				return jsonObj

	def __create_error_object(self,code, reason, detail="", jobID=""):
		err = HODErrorObject(code,reason,detail,jobID)
		self.errorsList.add_error(err)
