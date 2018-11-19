from microWebSrv import MicroWebSrv
import _thread, utime

srv_run_in_thread = True

file = open("www/index.html")
htmlSite = file.read()
file.close()

f2 = open("www/alarm.html")
alarmSite = f2.read()
f2.close()

datetime = utime.localtime()

# route handler for index.html with method GET
@MicroWebSrv.route('/')
def _httpHandlerPost(httpClient, httpResponse) :

    # get system time and save it t datetime_dict
    datetime = utime.localtime()
    datetime_dict = { "year" : datetime[0], "month" : datetime[1], "mday" : datetime[2],
                    "hour": datetime[3], "minute" : datetime[4], "second" : datetime[5],
                    "weekday" : datetime[6], "yearday" : datetime[7]}

    # insert datetime_dict values in placeholders in htmlSite
    html = htmlSite.format(**datetime_dict)
    # send htmlSite as response to client
    httpResponse.WriteResponseOk(   headers         = ({'Cache-Control': 'no-cache'}),
                                    contentType     = 'text/html',
                                    contentCharset  = 'UTF-8',
                                    content = html)

# route handler for index.html with method POST
@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    # read posted form data. If data (dictionary) received, convert to string and send threadMessage to mainThread
    formData = httpClient.ReadRequestPostedFormData()
    if formData:
        print(formData)
        message = str(formData)
        _thread.sendmsg(_thread.getReplID(), message)

    # get system time and save it t datetime_dict
    datetime = utime.localtime()
    #print(datetime)
    datetime_dict = { "year" : datetime[0], "month" : datetime[1], "mday" : datetime[2],
                    "hour": datetime[3], "minute" : datetime[4], "second" : datetime[5],
                    "weekday" : datetime[6], "yearday" : datetime[7]}

    htmlSite = htmlSite.format(**datetime_dict)
    # send htmlSite as response to client
    httpResponse.WriteResponseOk(   headers         = ({'Cache-Control': 'no-cache'}),
                                    contentType     = 'text/html',
                                    contentCharset  = 'UTF-8',
                                    content = htmlSite)


# create instance of MicroWebSrv and start server
srv = MicroWebSrv(webPath = 'www')
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
