from machine import Pin, TouchPad, ADC, DAC, PWM, RTC, Timer, resetWDT
import time
import px as px
import _thread, gc, utime
import connectSTA_AP, songs
import webSrv as srv

#blink once at startup to signalize that device has started and turn off all led
px.blink(count=1)

#connect to wifi or create access point
connectSTA_AP.connect()
time.sleep_ms(200)
#create realTimeClock instance and synchronize with online clock if possible
clock= RTC()
date = clock.now()

timer = Timer(0)
newAlarm = False
newTime = False
newSong = False
alarm = False
alarmTime = (0,0)
currMs = 0
lastMs = 0
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

touchThreshold = touchLight.read()#sum(thresholdLight)//len(thresholdLight)
#touchLight.config(600)


#light resistor configuration
#ldr = ADC(Pin(36, Pin.IN))

def handleLightThread(val):
    '''stops current running light animation and starts new one with given value
    '''
    global lightAnim_thread
    global threadID
    print("handleLightThread")

    #print("server thread suspended")
    if lightAnim_thread is not 0:
        _thread.notify(lightAnim_thread, _thread.EXIT)
        time.sleep_ms(1000)
    lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    time.sleep_ms(500)
    #px.thread(val)

def handleMusicThread(val):
    '''stops current musicThread if runing and starts a new one with given value
    '''
    global music_thread
    if (val is 0 or music_thread is not 0):
        _thread.notify(music_thread, _thread.EXIT)
        time.sleep_ms(1000)
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    #time.sleep_ms(500)

def _handleTimer(timer):
    '''timerhandler to starts thread(s) if alarmTime is now
    '''
    global countTime
    global alarm
    print("ALARM!")
    alarm = False
    countTime = False
    handleLightThread(4)
    handleMusicThread("Tetris")

def setAlarmTime(h, m):
    '''
    calculates millis to next alarm and creates timer instance
    '''
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

    return alarm_ms



#start server in thread
srv.start()

while True:
    resetWDT()

    touchval = touchLight.read()
    #print("...done")
    #time.sleep_ms(200)
    #read the touch sensor and check if it was touched
    touchLightRatio = touchval / touchThreshold
    if .40 < touchLightRatio < .8:
        print("touched!")
        #if alarm is set to True it means alarm is currently running
        #touchSensor disables alarm
        #IMPORTANT!!! add snooze function by counting how many seconds sensor was touched
        if alarm: #newAlarm:
            print("aborting alarm")
            handleLightThread(0)
            handleMusicThread(0)
            timer.deinit()
            time.sleep_ms(300)
        #if no alarm is currently running, increase lightCase by one to toggle through lightAnimations
        else:
            lightCase += 1
        #time.sleep_ms(200)

    #check if lightAnim was set on website. returns "None" if none was set
    light = srv.getLight()
    if light is not "None":
        print("light changed by webserver: {}".format(light))
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
        #time.sleep for more than one second is important, else system will crash
        time.sleep_ms(2000)

    #check if lightCase has changed to know if new lightAnim should be started
    if lightCase is not oldLightCase:
        print("lightCase changed: {}".format(lightCase))
        oldLightCase = lightCase
        handleLightThread(lightCase)
        time.sleep_ms(1000)

    #synch systemTime online if not done yet.
#    if not clock.synced():
#        clock.ntp_sync(server="hr.pool.ntp.org", tz="CET-1CEST")
#        print("current time: {}".format(clock.now()))
#        time.sleep_ms(400)


    #check if a new song was set on website, gets "None" if not
    song = srv.getSong()
    if song is not "None":
        print("song set to: {}".format(song))
        time.sleep_ms(300)
        handleMusicThread(song)


    #check if systemTime was changed on website
    newTime = srv.getTime()
    if newTime is not "None":
        clock.init(newTime)
        print("initialized new time: {}".format(newTime))
        newTime = False

    #check if alarmTime was set on website
    newAlarm = srv.getAlarm()
    if newAlarm is not "None":
        millisToAlarm = setAlarmTime(int(newAlarm[0]), int(newAlarm[1]))
        newAlarm = False
    #time.sleep_ms(400)

    #get current systemTime in milliseconds
    currMs = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), lastMs) >=1000:
        lastMs = time.ticks_ms()
        if alarm:
            print("{} seconds to alarm".format(int(millisToAlarm/1000)))
            millisToAlarm = millisToAlarm -1000
    time.sleep_ms(300)
