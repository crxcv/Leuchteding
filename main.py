# Begin configuration
TITLE    = "RainbowWarrior"

# End configuration

#import network
from machine import Pin, TouchPad, ADC, DAC, PWM, RTC
import connectSTA_AP
import time
#import piezo as pz
import webSrv as server

#pz.find_song('TopGun')

#exception buffer for interrupt handler
#micropython.alloc_memory_exception_buff(100)

#connect in station mode if possible, else creates access point
#thread_connect = _thread.start_new_thread("thread_wifiConnect", connect, ())
connectSTA_AP.connect()
server.startServer()

currTime = None
alarmTime = None
song = "none"

#light = ""
lightMax = 5


touchLight = TouchPad(Pin(27))
touchLight.config(600)
touchThreshold = touchLight.read() - 400


ldr = ADC(Pin(36, Pin.IN))
#ldrVal = ldrPin.read()
#print("ldr value at start: {}".format(ldrVal))
#causes stack overflow :assertion "heap != NULL && "free() target pointer i***ERROR*** A stack overflow in task IDLE has been detected
#px.setBrightness(ldrVal)

#turn off all pixels by setting lightCase to 0 = Off
server.startLightThread(0)



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
        server.startLightThread(lightCase)    #touchLight.irq(trigger=Pin.IRQ_FALLING, handler = lightFunc)
