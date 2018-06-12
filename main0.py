from machine import Pin, TouchPad, ADC, DAC, PWM, RTC
from time import sleep_ms
import _thread
import connectSTA_AP
import webSrv as server
import px as px

#connect to wifi or create access point
connectSTA_AP.connect()
oldLightCase = 0
lightCase = 0
lightAnim_thread = 0
lightMax = 5

#_thread.replAcceptMsg(True)

#touch sensor configuration
touchLight = TouchPad(Pin(27))
touchLight.config(600)
touchThreshold = touchLight.read() - 400

#light resistor configuration
ldr = ADC(Pin(36, Pin.IN))

server.start()

def handleLightThread(val):
    global lightAnim_thread
    if lightAnim_thread is not 0:
        _thread.notify(lightAnim_thread, _thread.EXIT)
        sleep_ms(1000)
    lightAnim_thread = px.startAnimThread(val)

def touch():
    global touchLight
    touchval = touchLight.read()
    #print("route: /")
    #ldrVal = ldr.read()
    #server.setLightCase(lightCase)
    #sleep_ms(100)
    #lightCase = server.getLightCase()
    if touchval < touchThreshold and touchval > 100:
        lightCase = [lightCase +1, 0][lightCase+1 >= lightMax]
        sleep_ms(500)

    if lightCase is not oldLightCase:
        oldLightCase = lightCase
        handleLightThread(lightCase)

handleLightThread(0)
