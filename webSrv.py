from microWebSrv import MicroWebSrv
import _thread

#html = open('index.html', 'rw')
htmlAlarm = open('www/alarm.html', 'rw')
srv_run_in_thread = True

@MicroWebSrv.route('/')
def _httpHandlerGet(httpClient, httpResponse):
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
            <form action="/TEST" method="post" accept-charset="ISO-8859-1">
                First name: <input type="text" name="firstname"><br />
                Last name: <input type="text" name="lastname"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % httpClient.GetIPAddr()
    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)
    #httpResponse.WriteResponseFileAttachment('www/style.css', 'bootstrap.min.css', headers=None)
    #httpResponse.WriteResponseFileAttachment('www/bootstrap.min.css', 'bootstrap.min.css', headers=None)

    #httpResponse.WriteResponseOk(   headers    = None,                                  contentType = "text/html",
                                    #contentCharset = "UTF-8",
                                    #content = html)

@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname  = formData["lastname"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
    """ % ( MicroWebSrv.HTMLEscape(firstname),
            MicroWebSrv.HTMLEscape(lastname) )

    light = formData["light"]
    if "RainbowCycle" in light:
        lightCase = 4
        #px.rainbowCycle()
    elif "ColorGradient" in light:
        lightCase = 3
        #px.bezier_gradient()
    elif "MeteorRain" in light:
        lightCase = 2
        #px.meteorRain()
    elif "Fire" in light:
        px.fire()
        #lightCase = 1
        #print("Fire")
    elif "Off" in light:
        lightCase = 0
        #px.off()
    startLightThread(lightCase)



    httpResponse.WriteResponseOk(headers        = None,
                                        contentType = "text/html",
                                        contentCharset = "UTF-8",
                                        content = html)
@MicroWebSrv.route('/alarm')
def _httpHandlerGetAlarm(httpClient, httpResponse):
    print("alarm site opened")
    httpResponse.WriteResponseOk( headers   = None,
                                        contentType = "text/html",
                                        contentCharset = "UTF-8",
                                        content = content)

@MicroWebSrv.route('/alarm', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    print("got post request")
    args = httpClient.ReadRequestPostedFormData()
    print(args)
    if 'setTime' in args:
        currTime = RTC()
        currTime.init((args['year'], args['month'], args['day'], args['hour'], args['minute'], 0, 0, 0))

    #if 'setAlarm' in args:

    if 'setSound' in args:
        song = args['setSound']

        if args['btn'] is 'play':
            import piezo as pz
            soundThread = _thread.start_new_thread("playSound", pz.find_song, (song, ))
            print("sound set to {}",format(song))

    httpResponse.WriteResponseOk( headers   = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = content)

@MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
    """
    content += "<h1>EDIT item with {} variable arguments</h1>"\
        .format(len(args))

    if 'index' in args :
        content += "<p>index = {}</p>".format(args['index'])

    if 'foo' in args :
        content += "<p>foo = {}</p>".format(args['foo'])

    content += """
        </body>
    </html>
    """
    httpResponse.WriteResponseOk( headers		 = None,
                                    contentType	 = "text/html",
                                    contentCharset = "UTF-8",
                                    content 		 = content )

    #--------------------------------------------------------------------
def startServer():
    #create server instance and start server
    srv = MicroWebSrv(webPath = 'www')
    srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
    print("started webServer")
