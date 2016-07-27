from havenondemand.hodclient import *
import sys

hodClient = HODClient("YOUR-API-KEY")

def main(argv):
    hodApp = ""
    if argv[0] == "createindex":
        hodApp = HODApps.CREATE_TEXT_INDEX
    elif argv[0] == "createconnector":
        hodApp = HODApps.CREATE_CONNECTOR
    elif argv[0] == "startconnector":
        hodApp = HODApps.START_CONNECTOR
    elif argv[0] == "connectorstatus":
        hodApp = HODApps.CONNECTOR_STATUS
    elif argv[0] == "search":
        hodApp = HODApps.QUERY_TEXT_INDEX


    if hodApp is HODApps.CREATE_TEXT_INDEX:
        params = dict()
        params['index'] = argv[1]
        params['description'] = "index for dropbox"
        params['flavor'] = "explorer"

        response = hodClient.post_request(params, hodApp, False)
        if response is None:
            errors = hodClient.get_last_error()
            for err in errors.errors:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            print ("INDEX NAME: %s" % response['index'])
            print ("MESSAGE: %s" % response['message'])

    elif hodApp is HODApps.CREATE_CONNECTOR:
        params = dict()
        params['connector'] = argv[1]
        params['description'] = "connector for dropbox app"
        params['flavor'] = "dropbox_cloud"
        params['config'] = """
        {
           "full_dropbox_access": false
        } """
        params['credentials'] = """
        {
            "app_key":"your-app-key",
            "access_token":"your-access-token"
        } """
        params['credentials_policy'] = """
        {
	        "notification_email": "valid email address"
        } """
        params['destination'] = """
        {
	        "action": "addtotextindex",
	        "index": "dropboxindex"
        } """        
		#params['schedule'] = """
        #{
	    #    "occurrences": NUMBER,
	    #    "start_date": "DD/MM/YYYY HH:MM:SS",
	    #    "end_date": "DD/MM/YYYY HH:MM:SS",
	    #    "frequency": {
		#        "frequency_type": "seconds",
		#        "interval": NUMBER
	    #    }
        #} """

        response = hodClient.post_request(params, hodApp, False)
        if response is None:
            errors = hodClient.get_last_error()
            for err in errors.errors:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            print ("CONNECTOR NAME: %s" % response['connector'])
            print ("MESSAGE: %s" % response['message'])

    elif hodApp is HODApps.START_CONNECTOR:
        params = dict()
        params['connector'] = argv[1]
        response = hodClient.get_request(params, hodApp, False)
        if response is None:
            errors = hodClient.get_last_error()
            for err in errors.errors:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            print ("CONNECTOR NAME: %s" % response['connector'])
            print ("TOKEN: %s" % response['token'])

    elif hodApp is HODApps.CONNECTOR_STATUS:
        params = dict()
        params['connector'] = argv[1]
        response = hodClient.get_request(params, hodApp, False)
        if response is None:
            errors = hodClient.get_last_error()
            for err in errors.errors:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            print ("CONNECTOR NAME: %s" % response['connector'])
            print ("CONNECTOR STATUS: %s" % response['status'])

    elif hodApp is HODApps.QUERY_TEXT_INDEX:
        params = dict()
        params['indexes'] = argv[1]
        params['text'] = argv[2]
        params['print_fields'] = "dropbox_link,author"
        params['summary'] = "quick"
        response = hodClient.get_request(params, hodApp, False)
        if response is None:
            errors = hodClient.get_last_error()
            for err in errors.errors:
                print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            res = ""
            for doc in response['documents']:
                res += '\n-----------DOCUMENT ITEM------------\n'
                res +=  ('SUMMARY: %s\n\n' % (doc['summary']))
                res +=  ('DROPBOX LINK: %s \n\n' % (doc['dropbox_link'][0]))
                if 'author' in doc:
                    res += ('AUTHOR: %s\n' % (doc['author'][0]))
                res += '=============ITEM END=============='
            if len(res) > 0:
                print (res)
            else:
                print ("Not found.")

main(sys.argv[1:])