from machine import Pin, TouchPad, ADC, DAC, PWM, RTC, Timer, resetWDT
from time import sleep_ms
import px as px
import _thread, gc, utime
import connectSTA_AP, songs
import webSrv as srv

#blink once at startup to signalize that device has started and turn off all led
px.blink(count=1)

#connect to wifi or create access point
connectSTA_AP.connect()
sleep_ms(200)
#create realTimeClock instance and synchronize with online clock if possible
clock= RTC()
date = clock.now()

timer = Timer(0)
newAlarm = False
newTime = False
newSong = False
alarm = False
alarmTime = (0,0)
currSecnds = 0
lastSecnds = 0
timeCounterSecnds = 0
millisToAlarm = 0
countTime = True



oldLightCase = 0
lightCase = 0
light = "None"
lightAnim_thread = 0
#lightMax = 5
song = "None"
music_thread = 0

#_thread.replAcceptMsg(True)

#interruptHandler for touchLight pin
def touchLightCallback(touchLight):
    global lightCase
    global touchThreshold
    lightCase = lightCase +1

#touch sensor configuration
touchLight = TouchPad(Pin(4))



#thresholdLight=[]
#for i in range(6):
#    thresholdLight.append(touchLight.read())
#    sleep_ms(100)
touchThreshold = touchLight.read()#sum(thresholdLight)//len(thresholdLight)
#touchLight.config(600)

#interruptRequest for touchLight Pin
#touchLight.irq(trigger=Pin.IRQ_FALLING, handler=touchLightCallback)


#light resistor configuration
#ldr = ADC(Pin(36, Pin.IN))






def handleLightThread(val):
    global lightAnim_thread
    global threadID
    print("handleLightThread")

    #print("server thread suspended")
    if lightAnim_thread is not 0:
        _thread.notify(lightAnim_thread, _thread.EXIT)
        sleep_ms(1000)
    lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    #sleep_ms(500)
    #px.thread(val)

def handleMusicThread(val):
    global music_thread
    if music_thread is not 0:
        _thread.notify(music_thread, _thread.EXIT)
        sleep_ms(1000)
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    #sleep_ms(500)



def _handleTimer(timer):
    global countTime
    global alarm
    alarm = False
    countTime = False
    handleLightThread(3)
    handleMusicThread("Tetris")

def setAlarmTime(h, m):
    print("setting alarm time ")
    global clock
    global alarmTime
    global timer
    global alarm

    alarm = True

    secondsPerDay = 86400
    secondsPerHour = 3600
    secondsPerMin = 60
    msPerSec = 1000
    #get actual time as touple
    currTime_touple = utime.localtime()
    #convert tuple to sec
    currTime_sec = utime.mktime(currTime_touple)
    print("utime.mktime(currentTouple): {}".format(currTime_sec))
    #touple:
    #0: year    1: month 2: mday 3: hour 4: min 5: sec 6: weekday 7: yearday
    #replace values of current time with hour and min from alarm time & get seconds to this time
    alarm_touple = (currTime_touple[0], currTime_touple[1],currTime_touple[2], h, m,  currTime_touple[5], currTime_touple[6], currTime_touple[7])
    alarm_sec= utime.mktime(alarm_touple)
    print("alarm_sec:{}".format(alarm_sec))

    #check if alarmTime is on this day or not

    #substract alarm_sec from currTime_sec. if result equals or is more than 0, alarm must be now or in the past so we need to add secondsPerDay
    alarm_sec = currTime_sec - alarm_sec
    #print("currTime_sec - alarm_sec: {} ".format(alarm_sec))

    if alarm_sec >= 0:
        alarm_sec = alarm_sec + secondsPerDay
        print("alarm_sec >= 0: {}".format(alarm_sec))
    else:
        alarm_sec = alarm_sec *-1
        print("alarm_sec < 0: {}".format(alarm_sec))
    #calculate ms from sec
    alarm_ms = int(alarm_sec * msPerSec)
    print("ms to alarm: {}".format(alarm_ms))
    #initialize timer
    timer.init(period=alarm_ms, mode= timer.ONE_SHOT, callback= _handleTimer )
    global countTime
    countTime = True

    return alarm_sec



#start server in thread
srv.start()

while True:
    resetWDT()

    touchval = touchLight.read()
    #print("...done")
    #sleep_ms(200)
    touchLightRatio = touchval / touchThreshold
    if .40 < touchLightRatio < .8:
        print("touched!")
        if alarm: #newAlarm:
            handleLightThread(0)
            timer.deinit()

        lightCase =lightCase +1
        sleep_ms(200)
    light = srv.light()
    if light is not "None":
        if "RainbowCycle" in light:
            lightCase = 5
        elif "ColorGradient" in light:
            lightCase = 4
        elif "MeteorRain" in light:
            lightCase = 3
        elif "Fire" in light:
            lightCase = 2
        elif "Off" in light:
            lightCase = 0
        else:
            lightCase = 1
        sleep_ms(2500)

    if lightCase is not oldLightCase:
        print("lightCase changed: {}".format(lightCase))
        oldLightCase = lightCase
        handleLightThread(lightCase)
        sleep_ms(200)


    if not clock.synced():
        clock.ntp_sync(server="hr.pool.ntp.org", tz="CET-1CEST")
        print("current time: {}".format(clock.now()))
        sleep_ms(400)

    song = srv.song()
    if song is not "None":
        print("song set to: {}".format(song))
        handleMusicThread(song)
        sleep_ms(200)

    newTime = srv.time()
    if newTime:
        clock.init(newTime)
        newTime = False

    newAlarm = srv.alarm()
    if newAlarm:
        millisToAlarm = setAlarmTime(int(newAlarm[0]), int(newAlarm[1]))
        newAlarm = False
    #sleep_ms(400)

    currSecnds = utime.mktime(clock.now())
    #print(currSecnds)
    if (currSecnds - timeCounterSecnds) >=1:
        timeCounterSecnds = currSecnds

        if alarm:
            print("{} seconds to alarm".format(int(millisToAlarm/1000)))
    sleep_ms(100)
