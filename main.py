from machine import Pin, TouchPad, ADC, DAC, PWM, RTC
import webSrv as server
import _thread
import connectSTA_AP
import time

import px as px

#connect to wifi or create access point
connectSTA_AP.connect()

#start webServer
server.start()

oldLightCase = 0
lightCase = 0
lightAnim_thread = 0
lightMax = 5

_thread.replAcceptMsg(True)

#touch sensor configuration
touchLight = TouchPad(Pin(27))
touchLight.config(600)
touchThreshold = touchLight.read() - 400

#light resistor configuration
ldr = ADC(Pin(36, Pin.IN))

def handleLightThread(val):
    global lightAnim_thread
    #("lightAnim thread No: {}".format(lightAnim_thread))
    if lightAnim_thread is not 0:
        #print("notifying light thread about abortion")
        _thread.notify(lightAnim_thread, _thread.EXIT)
        _thread.stop(lightAnim_thread)
        time.sleep_ms(300)
    lightAnim_thread = px.startAnimThread(val)



#lightAnim_thread = px.startAnimThread(0)
handleLightThread(0)

while True:

    touchval = touchLight.read()
    #print(touchval)
    #ldrVal = ldr.read()
    #print("ldr: {}".format(ldrVal))
    server.setLightCase(lightCase)
    time.sleep_ms(100)
    lightCase = server.getLightCase()
    if touchval < touchThreshold and touchval > 100:
        print("got touched ")
        print("lc before touch: {}".format(lightCase))
        lightCase = [lightCase +1, 0][lightCase+1 >= lightMax]
        print("lc after touch: {}".format(lightCase))
        time.sleep_ms(500)

    #    handleLightThread(lightCase)
    if lightCase is not oldLightCase:
        print("anim no {}".format(lightCase))
        oldLightCase = lightCase
        handleLightThread(lightCase)
