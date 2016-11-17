class ErrorCode:
    TIMEOUT = 1600
    IN_PROGRESS = 1610
    QUEUED = 1620
    NONSTANDARD_RESPONSE = 1630
    INVALID_PARAM = 1640
    INVALID_HOD_RESPONSE = 1650
    UNKNOWN_ERROR = 1660
    HTTP_ERROR = 1670
    CONNECTION_ERROR = 1680
    IO_ERROR = 1690
    HOD_CLIENT_BUSY = 1700

class HODErrorObject:
    error = 0
    reason = ""
    detail = ""
    jobID = ""
    def __init__(self, err, rea, det, job):
        self.error = err
        self.reason = rea
        self.detail = det
        self.jobID = job

class HODErrors:
    errors = []
    def __init__(self):
        errors = []
    def add_error(self, error):
        self.errors.append(error)

    def reset_errors(self):
        self.errors = []
