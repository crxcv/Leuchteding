from microWebSrv import MicroWebSrv
import _thread

srv_run_in_thread = True
lightC = 0

def getLightCase():
    return lightC

def setLightCase(lCase):
    global lightC
    lightC = lCase

@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    #print(formData)
    light = formData["light"]
    global lightC

    if "RainbowCycle" in light:
        lightC = 4
    elif "ColorGradient" in light:
        lightC = 3
    elif "MeteorRain" in light:
        lightC = 2
    elif "Fire" in light:
        lightC = 1
    else:
        lightC = 0
    #print(lightC)
    #handleLightThread(lightC)
    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)

@MicroWebSrv.route('/alarm')
def _httpHandlerGetAlarm(httpClient, httpResponse):
    #print("alarm site opened")
    httpResponse.WriteResponseOk( headers   = None,
                                        contentType = "text/html",
                                        contentCharset = "UTF-8",
                                        content = content)

@MicroWebSrv.route('/alarm', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    args = httpClient.ReadRequestPostedFormData()
    #print(args)
    if 'setTime' in args:
        currTime = RTC()
        currTime.init((args['year'], args['month'], args['day'], args['hour'], args['minute'], 0, 0, 0))

    #if 'setAlarm' in args:

    if 'setSound' in args:
        song = args['setSound']

        if args['btn'] is 'play':
            import piezo as pz
            soundThread = _thread.start_new_thread("playSound", pz.find_song, (song, ))
            #print("sound set to {}",format(song))

    httpResponse.WriteResponseOk( headers   = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = content)

    #-----------------------------------------------------------------
def start():
    #create server instance and start server
    srv = MicroWebSrv(webPath = 'www')
    srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
