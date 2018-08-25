from machine import Pin, TouchPad, ADC, DAC, PWM, RTC, Timer, resetWDT
import px as px
import _thread, gc, utime
import connectSTA_AP, songs
import webSrv as srv

newAlarm = False
newTime = False
newSong = False
alarm = False
lightOn = False
alarmTime = (0,0)
currMs = 0
lastMs = 0
lastMsAlarm = 0
timeCounterSecnds = 0
millisToAlarm = 0
#gets true if new AlarmTime was set, to print seconds to alarm in terminal
countTime = False

oldLightCase = 0
alarmLightCase = 3
lightCase = 0
light = "None"
lightAnim_thread = 0
brightnessVal = 0
oldBrightnessVal = 0
song = "None"
alarmSong = "Tetris"
music_thread = 0
ledColor = (245, 242, 22)

#set to true to be able to send notifications to main thread
_thread.replAcceptMsg(True)
#connect to wifi or create access point
connectSTA_AP.connect()
utime.sleep_ms(200)
#create realTimeClock instance and synchronize with online clock if possible
clock= RTC()
date = clock.now()
timer = Timer(0)

def readTouchPin():
    touchv = 1
    try:
        touchv = touchLight.read()
    except ValueError:
        print("TouchPad read error")
    return touchv

#touch sensor configuration
touchLight = TouchPad(Pin(4))
touchThreshold = readTouchPin() #touchLight.read()#sum(thresholdLight)//len(thresholdLight)
#touchLight.config(600)

#light resistor configuration
ldr = ADC(Pin(36, Pin.IN)) #SVP-Pin
ldrVal = ldr.read()
px.setBrightness(50)
#blink once at startup to signalize that device has started and turn off all led
px.blink(count=1)

#interruptHandler for touchLight pin
def touchLightCallback(touchLight):
    global lightCase
    global touchThreshold
    lightCase = lightCase +1

def handleLightThread(val):
    '''stops current running light animation and starts new one with given value
    '''
    global lightAnim_thread
    print("handleLightThread")
    #print("server thread suspended")
    if lightAnim_thread != 0:
        #utime.sleep_ms(500)
        _thread.wait(500)
        status = _thread.status(lightAnim_thread)
        #if status == _thread.RUNNING:
        print("stopping lightThread")
        _thread.stop(lightAnim_thread)
        #_thread.notify(lightAnim_thread, _thread.EXIT)
        #utime.sleep_ms(500)
        _thread.wait(500)
        lightAnim_thread = 0
    #if lights should be turned off, return. turning off is done by thread.stop()
    if val is 0:
        return

    _thread.stack_size(22*1024)
    lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    utime.sleep_ms(1000)
    #px.thread(val)

def handleMusicThread(val):
    '''stops current musicThread if runing and starts a new one with given value
    '''
    global music_thread
    if music_thread is not 0:
        print("stopping musicThread")
        _thread.notify(music_thread, _thread.EXIT)
        utime.sleep_ms(200)
        music_thread = 0
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    #utime.sleep_ms(500)

def _handleTimer(timer):
    '''timerhandler to start thread(s) if alarmTime is now
    '''
    global countTime
    global alarm
    global lastMsAlarm
    print("ALARM!")
    alarm = True
    countTime = False
    lastMsAlarm = utime.ticks_ms()
    handleLightThread(alarmLightCase)
    utime.sleep_ms(50)
    handleMusicThread(alarmSong)

def setAlarmTime(h, m):
    '''
    calculates millis to next alarm and creates timer instance
    '''
    print("setting alarm time ")
    global clock
    global alarmTime
    global timer
    global countTime

    countTime = True
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

    return alarm_ms

def mainLoop():
    global alarm
    global lightCase
    global oldLightCase
    global lastMs

    while True:
        #resetWDT()
        lastMsLoop = utime.ticks_ms()
        touchval = readTouchPin()
        #read the touch sensor and check if it was touched
        touchLightRatio = touchval / touchThreshold
        if .40 < touchLightRatio < .8:
            print("touched! touchLightRatio: {}".format(touchLightRatio))
            #if alarm is set to True it means alarm is currently running
            #touchSensor disables alarm
            #IMPORTANT!!! add snooze function by counting how many seconds sensor was touched
            if alarm: #newAlarm:
                print("aborting alarm")
                handleLightThread(0)
                handleMusicThread(0)
                timer.deinit()
                alarm = False
                utime.sleep_ms(300)
            #if lightThread or musicThread is running, abort the thread and turn off sound or light
            elif _thread.status(lightAnim_thread) == _thread.RUNNING:
                handleLightThread(0)
            elif _thread.status(music_thread) == _thread.RUNNING:
                handleMusicThread(0)
            #if no alarm is currently running, increase lightCase by one to toggle through lightAnimations
            else:
                lightCase += 1
                utime.sleep_ms(100)

        #if alarm is running let the LEDs blink twice per second
        if alarm:
            currMs = utime.ticks_ms
            if utime.ticks_diff(utime.ticks_ms(), lastMsAlarm) >500:
                if lightOn:
                    px.off()
                    lightOn = False
                else:
                    px.setAll(ledColor[0], ledColor[1], ledColor[2], 255)
                    lightOn = True
                lastMsAlarm = utime.ticks_ms()

        #check if lightAnim was set on website. returns "None" if none was set
        #light = srv.getLight()
        msg = _thread.getmsg()
        if (msg[0] == 2 and msg[1] == srv_thread):
            values = msg[2].split(":")
            if values[0] is "light":
            #if light is not "None":
                print("light changed by webserver: {}".format(light))
                _thread.lock()
                if "Wave" in values[1]:
                    lightCase = 9
                elif "Ripple" in values[1]:
                    lightCase = 8
                elif "Sparkle" in values[1]:
                    lightCase = 7
                elif "MeteorRain" in values[1]:
                    lightCase = 6
                elif "RainbowCycle" in values[1]:
                    lightCase = 5
                elif "ColorGradient" in values[1]:
                    lightCase = 4
                elif "Fire" in values[1]:
                    lightCase = 2
                elif "Rainbow" in values[1]:
                    lightCase = 1
                elif "Off" in values[1]:
                    lightCase = 0
                _thread.unlock()

            #check if a new song was set on website, gets "None" if not
            elif values[0] is "song":
                alarmSong = values[1]
                print("song set to: {}".format(song))
                utime.sleep_ms(3000)
                handleMusicThread(song)
                utime.sleep_ms(2000)

            #check if systemTime was changed on website
            elif values[0] is "time":
                date = tuple(map(int, values[1][1:-1].split(',')))
                clock.init(newTime)
                print("initialized new time: {}".format(newTime))
                newTime = False
            #check if alarmTime was set on website
            elif values[0] is "alarm":
                newAlarm = tuple(map(int, values[1][1:-1].split(',')))
                millisToAlarm = setAlarmTime(int(newAlarm[0]), int(newAlarm[1]))
                newAlarm = False
            #utime.sleep_ms(400)

            #check if LED colors were set on website
            if values[0] is "colors":
                ledColor = tuple(map(int, values[1][1:-1].split(',')))
                print("new color from srv: {}".format(ledColor))
                px.setAll(ledColor[0], ledColor[1], ledColor[2], 255)
                utime.sleep_ms(300)

            #utime.sleep for more than one second is important, else system will crash
            _thread.wait(2000)
            #utime.sleep_ms(2000)

        #check if lightCase has changed to know if new lightAnim should be started
        if lightCase is not oldLightCase:
            print("lightCase changed: {}".format(lightCase))
            oldLightCase = lightCase
            handleLightThread(lightCase)
            _thread.wait(1000)
            #utime.sleep_ms(1000)


        #get current systemTime in milliseconds
        currMs = utime.ticks_ms()
        #execute containing code only once per second
        if utime.ticks_diff(utime.ticks_ms(), lastMs) >=1000:
            lastMs = utime.ticks_ms()
            #_thread.list()
            #print(ldrVal)
            #show countdown to alarm on terminal
            if countTime:
                print("{} seconds to alarm".format(int(millisToAlarm/1000)))
                millisToAlarm = millisToAlarm -1000
        utime.sleep_ms(150)


#start server in thread
srv_thread = srv.start()
mainLoop()
#main_thread = _thread.start_new_thread("main", mainLoop, ())
