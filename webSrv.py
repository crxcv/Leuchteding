from microWebSrv import MicroWebSrv
import _thread
import px as px

srv_run_in_thread = True
lightCase = 0
oldLightVal = 0
lightCase = 0
lightAnim_thread = 0


def lightFunc(lightVal):
    #elif ntf == _thread.SUSPEND

    if lightVal is 0:
        print("turning pixels off")
        px.off();
    elif lightVal is 1:
        print("starting fire anim")
        px.fire();
    elif lightVal is 2:
        print("starting meteor anim")
        px.meteorRain();
    elif lightVal is 3:
        print("starting bezier anim")
        px.bezier_gradient();
    elif lightVal is 4:
        print("starting rainbow anim")
        px.rainbowCycle();



def startLightThread(lightCase):
    #if lightAnim_thread:
    #    _thread.notify(lightAnim_thread, _thread.EXIT)
    #    time.sleep_ms(300)
    #
    #    _thread.stop(lightAnim_thread)
    #    time.sleep_ms(300)
    print("started lightThread")
    try:
        lightAnim_thread = _thread.start_new_thread("lightAnim", lightFunc, (lightCase,))

    except Exception as e:
        print("some error occured: {}".format(e))


@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    print("got post request")
    formData = httpClient.ReadRequestPostedFormData()
    print(formData)

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
        #px.off()    print("lightCase: {}".format(lightCase))
    print(lightCase)
    startLightThread(lightCase)

    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)

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

    #--------------------------------------------------------------------
def startServer():
    #create server instance and start server
    srv = MicroWebSrv(webPath = 'www')
    srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
    print("started webServer")
