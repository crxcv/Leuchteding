import machine, _thread, gc, utime

#gc.enable()
import connectSTA_AP, songs, px
import webSrv as srv

# gets True when alarm is running, so the touch sensor will stop alarm instead of toggeling animations
is_alarm_running = False
is_light_on = False
# for timing functions
curr_ms = 0
last_ms = 0
last_ms_ldr = 0
last_ms_alarm = 0
ms_to_alarm = 0
#gets true if new AlarmTime was set, to print seconds to is_alarm_running in terminal
count_time = False

wait_before_start_thread = 3000
wait_after_stop_thread = 500
#TODO: use constants for light_val
last_light_val = 0
alarm_light_val = 3
light_val = 0
lightAnim_thread = 0
led_color = (245, 242, 22)
#brightness_val = 0
#old_brightness_val = 0
alarm_song = "StarWars"
music_thread = 0

# touch pins: 4, 0, 2, 15, 13, 12, 14, 27, 33, 32
# value error on 0, 2. 4: 50%
touchPin = 4
ldr_pin = 36 #SVP Pin

ldr_val = 0
last_ldr_val = 0


#light resistor configuration
ldr = machine.ADC(machine.Pin(ldr_pin, machine.Pin.IN)) #SVP-Pin
ldr_val = ldr.read()
px.set_brightness(ldr_val)


#set to true to be able to get messages
_thread.replAcceptMsg(True)

#blink once at startup to signalize that device has started and turn off all led
_thread.stack_size(8*1024)
lightAnim_thread= _thread.start_new_thread("lightThread", px.thread, (3,))

#connect to wifi or create access point
connectSTA_AP.connect()

#create realTimeClock instance and synchronize with online clock if possible
clock= machine.RTC()
date = clock.now()
timer = machine.Timer(0)

def readTouchPin():
    touchv = 1
    try:
        touchv = touch.read()
    except ValueError:
        print("TouchPad read error")
    return touchv

#touch sensor configuration
touch = machine.TouchPad(machine.Pin(touchPin))
#touch.config(600)
touchThreshold = readTouchPin() #touch.read()#sum(thresholdLight)//len(thresholdLight)

#interruptHandler for touch pin
# def touchLightCallback(touch):
#     global light_val
#     global touchThreshold
#     light_val = light_val +1

def handleLightThread(val):
    '''stops current running light animation and starts new one with given value
    '''
    global lightAnim_thread
    #print("handleLightThread")

    # terminate thread if it is running
    if  _thread.status(lightAnim_thread) != _thread.TERMINATED:
        print("stopping lightThread")
        _thread.notify(lightAnim_thread, _thread.EXIT)
        _thread.wait(wait_after_stop_thread)

    else:
        px.off()

    #if lights should be turned off, return. turning off is done by thread.EXIT
    if val is 0:
        return

    _thread.wait(wait_before_start_thread)
    _thread.stack_size(8*1024)
    lightAnim_thread = _thread.start_new_thread("lightThread", px.thread, (val,))

def handleMusicThread(val):
    '''stops current musicThread if runing and starts a new one with given value
    '''
    global music_thread
    if _thread.status(music_thread) != _thread.TERMINATED:
        print("stopping musicThread")
        _thread.notify(music_thread, _thread.EXIT)
        utime.sleep_ms(wait_after_stop_thread)

    _thread.wait(wait_before_start_thread)
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    #utime.sleep_ms(500)

# handler for alarm timer. if time's up, music_thread starts
# is_alarm_running is set to True so main loop lets the LEDs blink
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
    handleMusicThread(alarm_song)
    #handleLightThread(light_val)

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
    #substract alarm_sec from currTime_sec. if result equals or is more than 0,
    # is_alarm_running must be now or in the past so we need to add secondsPerDay
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

#start server in thread
srv_thread = srv.start()
px.blink(1)

while True:
    touchval = readTouchPin()
    # TODO: this one makes no sense:
    #read the touch sensor and check if it was touched
    touchLightRatio = touchval / touchThreshold
    if .35 < touchLightRatio < .6:
        print("touched! touchLightRatio: {}".format(touchLightRatio))

        #if is_alarm_running is set to True it means is_alarm_running is currently running
        #touchSensor disables is_alarm_running
        #IMPORTANT!!! add snooze function by counting how many seconds sensor was touched
        if is_alarm_running:
            print("aborting alarm")
            handleLightThread(0)
            handleMusicThread(0)
            timer.deinit()
            is_alarm_running = False

        # if no alarm is currently running,
        # increase light_val by one to toggle through lightAnimations
        else:
            light_val += 1
            #utime.sleep_ms(100)

    # check if lightAnim was set on website. returns "None" if none was set
    # light = srv.getLight()
    msg = _thread.getmsg()
    if (msg[0] == 2 and msg[1] == srv_thread):
        values = msg[2].split(":")
        if values[0] is "light":
        # if light is not "None":
            print("light changed by webserver: {}".format(values[1]))
            elif "Ripple" in values[1]:
                light_val = 8
            elif "Wave" in values[1]:
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

        #check if a new song was set on website, gets "None" if not
        elif values[0] is "song":
            alarm_song = values[1]
            print("song set to: {}".format(alarm_song))
            handleMusicThread(alarm_song)

        #check if systemTime was set on website
        elif values[0] is "time":
            date = tuple(map(int, values[1][1:-1].split(',')))
            _thread.wait(300)
            clock.init(date)
            print("initialized new time: {}".format(date))

        #check if alarm_time was set on website
        elif values[0] is "alarm":
            new_alarm = tuple(map(int, values[1][1:-1].split(',')))
            _thread.wait(300)
            ms_to_alarm = setAlarmTime(int(new_alarm[0]), int(new_alarm[1]))

        #check if LED colors were set on website
        elif values[0] is "colors":
            led_color = tuple(map(int, values[1][1:-1].split(',')))
            #print("new color from srv: {}".format(led_color))
            _thread.wait(300)
            px.setAll(led_color[0], led_color[1], led_color[2], 255)


    #check if light_val has changed to know if new lightAnim should be started
    if light_val is not last_light_val:
        print("light_val changed: {}".format(light_val))
        last_light_val = light_val
        handleLightThread(light_val)
        #utime.sleep_ms(1000)

    #get current systemTime in milliseconds
    curr_ms = utime.ticks_ms()
    #execute containing code only once per second
    if utime.ticks_diff(utime.ticks_ms(), last_ms) >=1000:
        last_ms = utime.ticks_ms()
        #show countdown to is_alarm_running on terminal
        if count_time:
            print("{} seconds to alarm".format(int(ms_to_alarm/1000)))
            ms_to_alarm = ms_to_alarm -1000

    # read light resistor once per minute and set brightness of led according to value
    curr_ms = utime.ticks_ms()
    if utime.ticks_diff(utime.ticks_ms(), last_ms_ldr) >= (1000 * 60):
        last_ms_ldr = curr_ms
        ldr_val = ldr.read()
        px.set_brightness(ldr_val)

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
        if _thread.status(music_thread) == _thread.TERMINATED:
            _thread.start_new_thread("musicThread", songs.find_song(alarm_song))


    utime.sleep_ms(150)
