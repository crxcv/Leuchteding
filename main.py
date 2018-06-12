from machine import Pin, TouchPad, ADC, DAC, PWM, RTC
from time import sleep_ms
import px as px
import _thread
import connectSTA_AP
from microWebSrv import MicroWebSrv
import _thread

#connect to wifi or create access point
connectSTA_AP.connect()
px.blink()
oldLightCase = 0
lightCase = 0
lightAnim_thread = 0
#lightMax = 5

#webServer
srv_run_in_thread = True


#_thread.replAcceptMsg(True)

#touch sensor configuration
#touchLight = TouchPad(Pin(27))
#touchLight.config(600)
#touchThreshold = touchLight.read() - 400

#light resistor configuration
#ldr = ADC(Pin(36, Pin.IN))

#route handler for http-post requests
@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    light = formData["light"]
    global lightCase

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

    print("lightCase: {}".format(lightCase))
    #px.startAnimThread(lightCase)
    #handleLightThread(lightCase)
    #start light animation in a seperate thread

    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)

def handleLightThread(val):
    global lightAnim_thread
    print("handleLightThread")
    #if lightAnim_thread is not 0:
    #    _thread.notify(lightAnim_thread, _thread.EXIT)
    #    sleep_ms(1000)
    #lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    px.startAnimThread(val)


#def touch():
    #global touchLight
    #touchval = touchLight.read()
    #print("route: /")
    #ldrVal = ldr.read()
    #server.setLightCase(lightCase)
    #sleep_ms(100)
    #lightCase = server.getLightCase()
    #if touchval < touchThreshold and touchval > 100:
    #    lightCase = [lightCase +1, 0][lightCase+1 >= lightMax]
    #    sleep_ms(500)

    #if lightCase is not oldLightCase:
    #    oldLightCase = lightCase
    #    handleLightThread(lightCase)

handleLightThread(0)
srv = MicroWebSrv(webPath = 'www')
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
while True:
    #print("mainloop")
    sleep_ms(100)

    if lightCase is not oldLightCase:
        print("lightCase changed: {}".format(lightCase))
        oldLightCase = lightCase
        handleLightThread(lightCase)
