import machine, _thread, gc, utime

gc.enable()
import connectSTA_AP, songs, px
## gc.collect()
import webSrv as srv
# gc.collect()

# gets True when alarm is running, so the touch sensor will stop alarm instead of toggeling animations
is_alarm_running = False
is_light_on = False
# for printing seconds to alarm to terminal
curr_ms = 0
last_ms = 0

last_ms_alarm = 0
ms_to_alarm = 0
#gets true if new AlarmTime was set, to print seconds to is_alarm_running in terminal
count_time = False

#TODO: use constants for light_val
last_light_val = 0
alarm_light_val = 3
light_val = 0
lightAnim_thread = 0
led_color = (245, 242, 22)
#brightness_val = 0
#old_brightness_val = 0
alarm_song = "Tetris"
music_thread = 0

#set to true to be able to send notifications to main thread
_thread.replAcceptMsg(True)
# gc.collect()
_thread.stack_size(400)
lightAnim_thread= _thread.start_new_thread("lightThread", px.thread, (3,1))
#blink once at startup to signalize that device has started and turn off all led
# try:
#     _thread.stack_size(8*1024)
#     lightAnim_thread= _thread.start_new_thread("lightThread", px.thread, (3,1))
# except:
#     print("was not able to start animation")
# gc.collect()
#print("started 1st lightThread")
#_thread.stack_size(256)
#music_thread = _thread.start_new_thread("musicThread", songs.find_song, (0,))

#connect to wifi or create access point
connectSTA_AP.connect()
utime.sleep_ms(200)
#create realTimeClock instance and synchronize with online clock if possible
clock= machine.RTC()
date = clock.now()
timer = machine.Timer(0)

def readTouchPin():
    touchv = 1
    try:
        touchv = touchLight.read()
    except ValueError:
        print("TouchPad read error")
    return touchv

#touch sensor configuration
touchPin = 4
touchLight = machine.TouchPad(machine.Pin(touchPin))
touchThreshold = readTouchPin() #touchLight.read()#sum(thresholdLight)//len(thresholdLight)
#touchLight.config(600)

#light resistor configuration
ldrPin = 36 #SVP Pin
ldr = machine.ADC(machine.Pin(ldrPin, machine.Pin.IN)) #SVP-Pin
ldrVal = ldr.read()
px.setBrightness(50)
# gc.collect()
#interruptHandler for touchLight pin
def touchLightCallback(touchLight):
    global light_val
    global touchThreshold
    light_val = light_val +1

def handleLightThread(val):
    '''stops current running light animation and starts new one with given value
    '''
    global lightAnim_thread
    print("handleLightThread")
    #print("server thread suspended")
    if lightAnim_thread != 0:
        utime.sleep_ms(500)
        print("stopping lightThread")
        _thread.sendmsg(lightAnim_thread, _thread.EXIT)
        #_thread.notify(lightAnim_thread, _thread.EXIT)
        utime.sleep_ms(500)
        lightAnim_thread = 0
        # gc.collect()
    #if lights should be turned off, return. turning off is done by thread.stop()
    if val is 0:
        return

    _thread.stack_size(8*1024)
    lightAnim_thread = _thread.start_new_thread("lightThread", px.thread, (val,))
    utime.sleep_ms(1000)
    # gc.collect()

def handleMusicThread(val):
    '''stops current musicThread if runing and starts a new one with given value
    '''
    global music_thread
    if music_thread is not 0:
        print("stopping musicThread")
        _thread.sendmsg(music_thread, _thread.EXIT)
        utime.sleep_ms(200)
        music_thread = 0
    # gc.collect()
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    #utime.sleep_ms(500)

def _handleTimer(timer):
    '''timerhandler to start thread(s) if alarm_time is now
    '''
    global count_time
    global is_alarm_running
    global last_ms_alarm
    print("ALARM!")
    is_alarm_running = True
    count_time = False
    last_ms_alarm = utime.ticks_ms()
    # gc.collect()
    handleLightThread(alarm_light_val)
    utime.sleep_ms(50)
    handleMusicThread(alarm_song)

def setAlarmTime(h, m):
    '''
    calculates millis to next is_alarm_running and creates timer instance
    '''
    print("setting is_alarm_running time ")
    global count_time

    count_time = True
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
    #replace values of current time with hour and min from is_alarm_running time & get seconds to this time
    alarm_touple = ()
    alarm_touple = (currTime_touple[0], currTime_touple[1],currTime_touple[2], h, m,  currTime_touple[5], currTime_touple[6], currTime_touple[7])
    alarm_sec= utime.mktime(alarm_touple)
    print("alarm_sec:{}".format(alarm_sec))

    #check if alarm_time is on this day or not
    #substract alarm_sec from currTime_sec. if result equals or is more than 0, is_alarm_running must be now or in the past so we need to add secondsPerDay
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
    print("ms to is_alarm_running: {}".format(alarm_ms))
    # gc.collect()
    #initialize timer
    timer.init(period=alarm_ms, mode= timer.ONE_SHOT, callback= _handleTimer )

    return alarm_ms

def mainLoop():
    global is_alarm_running
    global light_val
    global last_light_val
    global last_ms

    while True:
        # gc.collect()
        touchval = readTouchPin()
        # TODO: this one makes no sense:
        #read the touch sensor and check if it was touched
        touchLightRatio = touchval / touchThreshold
        if .35 < touchLightRatio < .6:
            print("touched! touchLightRatio: {}".format(touchLightRatio))

            # if lightThread or musicThread is running, abort the thread and turn off sound or light
            # to prevent system from crash if webserver is used
            if (_thread.status(lightAnim_thread) != _thread.TERMINATED or _thread.status(music_thread) != _thread.TERMINATED):
                handleLightThread(0)
                handleMusicThread(0)

            #if is_alarm_running is set to True it means is_alarm_running is currently running
            #touchSensor disables is_alarm_running
            #IMPORTANT!!! add snooze function by counting how many seconds sensor was touched
            elif is_alarm_running: #is_new_alarm:
                print("aborting is_alarm_running")
                handleLightThread(0)
                handleMusicThread(0)
                timer.deinit()
                is_alarm_running = False
                utime.sleep_ms(300)

            # if no is_alarm_running is currently running,
            # increase light_val by one to toggle through lightAnimations
            else:
                light_val += 1
                utime.sleep_ms(100)

        # gc.collect()
        # if is_alarm_running is running let the LEDs blink twice per second
        if is_alarm_running:
            curr_ms = utime.ticks_ms
            if utime.ticks_diff(utime.ticks_ms(), last_ms_alarm) >500:
                if is_light_on:
                    px.off()
                    is_light_on = False
                else:
                    px.setAll(led_color[0], led_color[1], led_color[2], 255)
                    is_light_on = True
                last_ms_alarm = utime.ticks_ms()

        # gc.collect()
        # check if lightAnim was set on website. returns "None" if none was set
        # light = srv.getLight()
        msg = _thread.getmsg()
        if (msg[0] == 2 and msg[1] == srv_thread):
            values = msg[2].split(":")
            if values[0] is "light":
            # if light is not "None":
                print("light changed by webserver: {}".format(values[1]))
                #_thread.lock()
                if "Wave" in values[1]:
                    light_val = 9
                elif "Ripple" in values[1]:
                    light_val = 8
                elif "Sparkle" in values[1]:
                    light_val = 7
                elif "MeteorRain" in values[1]:
                    light_val = 6
                elif "RainbowCycle" in values[1]:
                    light_val = 5
                elif "ColorGradient" in values[1]:
                    light_val = 4
                elif "Fire" in values[1]:
                    light_val = 2
                elif "Rainbow" in values[1]:
                    light_val = 1
                elif "Off" in values[1]:
                    light_val = 0
                utime.sleep_ms(1000)

            #check if a new song was set on website, gets "None" if not
            elif values[0] is "song":
                alarm_song = values[1]
                print("song set to: {}".format(song))
                utime.sleep_ms(3000)
                handleMusicThread(song)
                utime.sleep_ms(2000)

            #check if systemTime was changed on website
            elif values[0] is "time":
                date = tuple(map(int, values[1][1:-1].split(',')))
                clock.init(date)
                print("initialized new time: {}".format(date))
            #check if alarm_time was set on website
            elif values[0] is "is_alarm_running":
                new_alarm = tuple(map(int, values[1][1:-1].split(',')))
                ms_to_alarm = setAlarmTime(int(new_alarm[0]), int(new_alarm[1]))
            #utime.sleep_ms(400)

            #check if LED colors were set on website
            elif values[0] is "colors":
                led_color = tuple(map(int, values[1][1:-1].split(',')))
                print("new color from srv: {}".format(led_color))
                px.setAll(led_color[0], led_color[1], led_color[2], 255)
                utime.sleep_ms(300)

            #utime.sleep for more than one second is important, else system will crash
            utime.sleep_ms(2000)
            #utime.sleep_ms(2000)

        # gc.collect()
        #check if light_val has changed to know if new lightAnim should be started
        if light_val is not last_light_val:
            print("light_val changed: {}".format(light_val))
            last_light_val = light_val
            handleLightThread(light_val)
            utime.sleep_ms(1000)

        #get current systemTime in milliseconds
        curr_ms = utime.ticks_ms()
        #execute containing code only once per second
        if utime.ticks_diff(utime.ticks_ms(), last_ms) >=1000:
            last_ms = utime.ticks_ms()
            #show countdown to is_alarm_running on terminal
            if count_time:
                print("{} seconds to is_alarm_running".format(int(ms_to_alarm/1000)))
                ms_to_alarm = ms_to_alarm -1000
        utime.sleep_ms(250)

# gc.collect()
#start server in thread
srv_thread = srv.start()
mainLoop()
#main_thread = _thread.start_new_thread("main", mainLoop, ())
