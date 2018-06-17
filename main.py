from machine import Pin, TouchPad, ADC, DAC, PWM, RTC, Timer, resetWDT
from time import sleep_ms
import px as px
import _thread, gc, utime
import connectSTA_AP, songs
from microWebSrv import MicroWebSrv


#blink once at startup to signalize that device has started and turn off all led
px.blink(count=1)

#connect to wifi or create access point
connectSTA_AP.connect()
sleep_ms(200)
#create realTimeClock instance and synchronize with online clock if possible
clock= RTC()
date = clock.now()

timer = Timer(0)
setAlarm = False
setByServer = False
alarmTime = (0,0)
currMillis = 0
lastMillis = 0
timerCounterMillis = 0
millisToAlarm = 0


oldLightCase = 0
lightCase = 0
lightAnim_thread = 0
#lightMax = 5
music_thread = 0

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
#touchLight.config(600)

#interruptRequest for touchLight Pin
#touchLight.irq(trigger=Pin.IRQ_FALLING, handler=touchLightCallback)


#light resistor configuration
#ldr = ADC(Pin(36, Pin.IN))

@MicroWebSrv.route('/')
def _httpHandler(httpClient, httpResponse):
    gc.collect()
    before = gc.mem_free()
    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)
    after = gc.mem_free()
    print("server uses {} bytes".format(after-before))
    gc.collect()


#route handler for http-post requests
@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    #gc.collect()
    #before = gc.mem_free()
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
    #after = gc.mem_free()
    #print("server uses {} bytes".format(after-before))
    #gc.collect()


@MicroWebSrv.route('/alarm')
@MicroWebSrv.route('/alarm', 'POST')
def _httpHandlerAlarm(httpClient, httpResponse):
    global clock
    global date
    global setAlarm
    global alarmTime
    global setByServer
    formData = httpClient.ReadRequestPostedFormData()
    print(formData)
    if "setTime" in formData:
        setByServer = True
        print("time set by srv")
        date=(int(formData["year"]), int(formData["month"]), int(formData["hour"]), int(formData["minute"]))

    if "setAlarm" in formData:
        setAlarm = True
        print("alarm set by srv")
        alarmTime = (int(formData["minute"]) ,int(formData["hour"]))
    #0: year    1: month 2: mday 3: hour 4: min 5: sec 6: weekday 7: yearday
    data = clock.now()
    #time = str("{0}.{1}.{3} {4}:{5} Uhr".format(data[2], data[1], data[0], data[3], data[4]))
    html ="""\
        <html lang=de>
          <head>
            <title>RainbowWarrior Alarm Settings</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

          </head>
          <body>
            <h1>time and alarm config</h1>
            <p>
                {0}.{1}.{2} {3}:{4} Uhr
            </p>
            <form method="POST" action="/alarm" id="setTime">
              <label form="setTime">set current system time</label></br>
              <label for"year">Year</label>
              <input type="text" name="year" id="year" maxlength="4">

              <label for"month">Month</label>
              <input type="text" name="month" id="month" maxlength="2">

              <label for"hour">Hour</label>
              <input type="text" name="hour" id="hour" maxlength="2">

              <label for"minute">minute</label>
              <input type="text" name="minute" id="minute" maxlength="2">
            </br>
              <button type="reset">Eingabe zur&uuml;cksetzen</button>
              <button type="submit">Eingabe absenden</button>
            </form>
            </br>
            </br>
            <form method="POST" action="alarm" id="setAlarm">
              <label form="setAlarm">set Alarm time</label>
              </br>
              <label for"hour">Hour</label>
              <input type="text" name="hour" id="hour" maxlength="2">

              <label for"minute">minute</label>
              <input type="text" name="minute" id="minute" maxlength="2">
              </br>
              <label >
                <input type="checkbox" name="dailyAlarm" value="dailyAlarm" checked="checked">
                daily Alarm
              </label>

              </br>
              <button type="submit" name = "setAlarm" value ="setAlarm">Eingabe absenden</button>
            </form>
          </br></br>

          <form method="POST" action="/alarm" id="setSound">
            <label form="setSound">Wecksound w&auml;hlen</label>
          </br>
          <input type="radio" id="Super Mario - Main Theme" name="setSound" value="MarioMain">
            <label for="Super Mario - Main Theme"> Super Mario - Main Theme</label> </br>

            <input type="radio" id="Super Mario - Title Music" name="setSound" value="MarioTitle">
              <label for="Super Mario - Title Music"> Super Mario - Title Music</label> </br>

            <input type="radio" id="Looney" name="setSound" value="Looney">
              <label for="Looney"> Looney Tunes Theme</label> </br>

            <input type="radio" id="The Simpsons" name="setSound" value="Simpsons">
              <label for="The Simpsons"> The Simpsons</label> </br>

            <input type="radio" id="Indiana" name="setSound" value="Indiana">
              <label for="Indiana"> Indiana Jones</label> </br>

            <input type="radio" id="muppets" name="setSound" value="Muppets">
              <label for="muppets"> The Muppet Show</label> </br>

            <input type="radio" id="Gadget" name="setSound" value="Gadget">
              <label for="Gadget"> Inspector Gadget</label> </br>

            <input type="radio" id="StarWars" name="setSound" value="StarWars">
              <label for="StarWars"> Star Wars Theme</label> </br>

            <input type="radio" id="Tetris" name="setSound" value="Tetris">
              <label for="Tetris"> Tetris Theme</label> </br>

            <button type="button">Song abspielen</button>
            <button type="submit">Wecksound w&auml;hlen</button>
          </form>

        </body>
        </html>""".format(data[2], data[1], data[0], data[3], data[4])   #httpResponse.WriteResponseFile( filepath = "www/alarm".append(.format(data)), contentType = 'text/event-stream')
    httpResponse.WriteResponseOk(   headers         = ({'Cache-Control': 'no-cache'}),   contentType     = 'text/html',contentCharset  = 'UTF-8',content =html)


def handleLightThread(val):
    global lightAnim_thread
    global threadID
    print("handleLightThread")

    #print("server thread suspended")
    if lightAnim_thread is not 0:
        _thread.notify(lightAnim_thread, _thread.EXIT)

    lightAnim_thread = _thread.start_new_thread("lightAnim", px.thread, (val,))
    sleep_ms(500)
    #px.thread(val)

def handleMusicThread(val):
    global music_thread
    if music_thread is not 0:
        thread.notify(music_thread, _thread.EXIT)
    music_thread = _thread.start_new_thread("musicThread", songs.find_song, (val,))
    sleep_ms(500)



def _handleTimer(timer):
    print("timer triggered")
    handleLightThread(3)
    handleMusicThread("Tetris")

def setAlarmTime(m, h):
    print("setting alarm time ")
    global clock
    global alarmTime
    #global setAlarm
    global timer

    secondsPerDay = 86400
    secondsPerHour = 3600
    secondsPerMin = 60
    msPerSec = 1000
    #get actual time as touple
    currTime_touple = utime.localtime()
    #convert tuple to sec
    currTime_sec = utime.mktime(currTime_touple)
    print("utime.mktime(currentTouple): {}".format(currTime_sec))
    alarm_touple = (currTime_touple[0], currTime_touple[1],currTime_touple[2], h, m,  currTime_touple[5], currTime_touple[6], currTime_touple[7])
    #touple:
    #0: year    1: month 2: mday 3: hour 4: min 5: sec 6: weekday 7: yearday
    #replace values of current time with hour and min from alarm time & get seconds to this time
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
    return alarm_sec



#start server in thread
srv_run_in_thread = True
srv = MicroWebSrv(webPath = 'www')

print("Server...")
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
print("...started")


while True:
    resetWDT()

    #sync clock online if it's not done yet and if esp's in station mode
    if not clock.synced():
        clock.ntp_sync(server="hr.pool.ntp.org", tz="CET-1CEST")
        print("current time: {}".format(clock.now()))


    if setByServer:
        clock.init(date)
        setByServer = False
    if setAlarm:
        print("alarm: {}".format(setAlarm))
        millisToAlarm = setAlarmTime(alarmTime[0], alarmTime[1])
        setAlarm = False
    utime.sleep_ms(200)

    #get current millis and check if 300ms passed since last call
    currMillis = utime.time()
    if (currMillis - lastMillis) >= 500:
        lastMillis = currMillis

    #print("reading touchpad")
        touchval = touchLight.read()
        #print("...done")
        #sleep_ms(200)
        touchLightRatio = touchval / touchThreshold
        if .40 < touchLightRatio < .8:
            if setAlarm:
                handleLightThread(0)
                timer.deinit()

            lightCase =lightCase +1
            #sleep_ms(200)

        #sleep_ms(300)

        if lightCase is not oldLightCase:
            print("lightCase changed: {}".format(lightCase))
            oldLightCase = lightCase
            handleLightThread(lightCase)

    currMillis = utime.time()
    if (currMillis - timerCounterMillis) >=1000:
        timerCounterMillis = currMillis
        print("{} seconds to alarm".format(int(millisToAlarm/1000)))
