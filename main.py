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

#_thread.replAcceptMsg(True)

#interruptHandler for touchLight pin
def touchLightCallback(touchLight):
    global lightCase
    global touchThreshold
    lightCase = lightCase +1

#touch sensor configuration
touchLight = TouchPad(Pin(27))
#thresholdLight=[]
#for i in range(6):
#    thresholdLight.append(touchLight.read())
#    sleep_ms(100)
touchThreshold = touchLight.read()#sum(thresholdLight)//len(thresholdLight)
touchLight.config(600)

#interruptRequest for touchLight Pin
#touchLight.irq(trigger=Pin.IRQ_FALLING, handler=touchLightCallback)


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

    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)

def handleLightThread(val):
    global lightAnim_thread
    print("handleLightThread")
    #if lightAnim_thread is not 0:
    #    _thread.notify(lightAnim_thread, _thread.EXIT)
    #    sleep_ms(1000)
    #lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    px.startAnimThread(val)


handleLightThread(0)

#start server in thread
srv_run_in_thread = True
srv = MicroWebSrv(webPath = 'www')
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)

while True:
    touchval = touchLight.read()
    touchLightRatio = touchval / touchThreshold
    if .40 < touchLightRatio < .8:
        lightCase =lightCase +1
        sleep_ms(200)


    if lightCase is not oldLightCase:
        print("lightCase changed: {}".format(lightCase))
        oldLightCase = lightCase
        handleLightThread(lightCase)
