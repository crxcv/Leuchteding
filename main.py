from microWebSrv import MicroWebSrv
from machine import Pin, TouchPad, ADC, DAC, PWM, RTC
import connectSTA_AP
import time

import _thread
import px as px

#connect to wifi or create access point
connectSTA_AP.connect()

srv_run_in_thread = True
lightCase = 0
oldLightVal = 0
lightCase = 0
lightMax = 5
lightAnim_thread = 0
_thread.replAcceptMsg(True)

#touch sensor configuration
touchLight = TouchPad(Pin(27))
touchLight.config(600)
touchThreshold = touchLight.read() - 400

#light resistor configuration
ldr = ADC(Pin(36, Pin.IN))

def handleLightThread(val):
    global lightAnim_thread
    print("lightAnim thread No: {}".format(lightAnim_thread))
    if lightAnim_thread is not 0:
        print("notifying light thread about abortion")
        _thread.notify(lightAnim_thread, _thread.EXIT)
        time.sleep_ms(300)
    lightAnim_thread = px.startAnimThread(lightCase)


@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    print(formData)
    light = formData["light"]

    if "RainbowCycle" in light:
        lightCase = 4
    elif "ColorGradient" in light:
        lightCase = 3
    elif "MeteorRain" in light:
        lightCase = 2
    elif "Fire" in light:
        lightCase = 1
    else:
        lightCase = 0
    print(lightCase)
    handleLightThread(lightCase)
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

    #-----------------------------------------------------------------

#create server instance and start server
srv = MicroWebSrv(webPath = 'www')
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
print("started webServer\nstarting 1st lightAnim = Off")
#lightAnim_thread = px.startAnimThread(0)
handleLightThread(0)

while True:
    #ntf = _thread.getnotification()
    #ldrVal = ldrPin.readraw()
    #print("ldr value: {}".format(ldrPin.read()))
    time.sleep_ms(300)
    #piezo.freq(ldrVal)
    touchval = touchLight.read()
    val = ldr.read()
    #print("ldr: {}".format(val))

    if touchval < 400 and touchval > 100:
        #print("got triggered\nlightCase: ")
        lightCase = [lightCase +1, 0][lightCase+1 >= lightMax]
        print(lightCase)
        print("touchVal: {}".format(touchval))
        #server.startLightThread(lightCase)    #touchLight.irq(trigger=Pin.IRQ_FALLING, handler = lightFunc)
