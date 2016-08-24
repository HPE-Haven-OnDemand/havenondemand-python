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
