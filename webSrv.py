from microWebSrv import MicroWebSrv
import _thread
import time
srv_run_in_thread = True
song = "None"
lightPattern = "None"
date= (0, 0, 0, 0, 0)
alarmTime = (0, 0)
newTime = False
newAlarm = False
newSong = False

newLightPattern = False

def light():
    global newLightPattern
    global lightPattern

    if newLightPattern:
        newLightPattern = False
        return lightPattern
    else:
        return "None"

def song():
    global newSong
    global song
    if newSong:
        #print(song)
        newSong = False
        return song
    else:
        return "None"


def time():
    global newTime
    global date

    if newTime:
        newTime = False
        return date
    else:
        return "None"

def alarm():
    global newAlarm
    global alarmTime

    if newAlarm:
        newAlarm = False
        return alarmTime
    else:
        return "None"

#route handler for http-post requests
@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    global lightPattern
    global newLightPattern
    newLightPattern = True

    formData = httpClient.ReadRequestPostedFormData()
    print(formData)
    lightPattern = formData["light"]

    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)



@MicroWebSrv.route('/alarm')
@MicroWebSrv.route('/alarm', 'POST')
def _httpHandlerAlarm(httpClient, httpResponse):
    #global clock
    global date
    global song
    global newSong
    global newAlarm
    global alarmTime
    global newDate
    global newTime
    formData = httpClient.ReadRequestPostedFormData()
    print(formData)
    if "time" in formData:
        #string formatting:
        # >>> '%0.2d' %(3)
        #'03'
        #>>> '%0.2d' %(10)
        #'10'
        newTime = True
        #newDate=formData["date"])
        day =   int(formData["date"].split('.')[0])
        month = int(formData["date"].split('.')[1])
        year =  int(formData["date"].split('.')[2])

        #newTime = int(formData["time"])
        hour =  int(formData["time"].split(':')[0])
        min =   int(formData["time"].split(':')[1])
        #print("time set by srv to {0}:{1} {2}.{3}.{4}".format(hour, min, day, month, year))
        date=(year, month, day, hour, min)
        print("time set to: {}".format(date))

    if "setAlarm" in formData:
        newAlarm = True

        hour =  int(formData["alarmTime"].split(':')[0])
        min =   int(formData["alarmTime"].split(':')[1])
        #print("alarm set by srv to {0}:{1}".format(hour, min))
        alarmTime = (hour ,min)

    if "setSound" in formData:
        newSong = True
        song = formData["setSound"]
        #print (formData)

    #0: year    1: month 2: mday 3: hour 4: min 5: sec 6: weekday 7: yearday
    #data = RTC.now()
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
                {0:02.02d}.{1:02.02d}.{2:02.02d} {3:02.02d}:{4:02.02d} Uhr
            </p>
            <form method="POST" action="/alarm" id="setTime">
              <label form="setTime">Systemzeit einstellen</label></br>
              <label for"year">Datum</label>
              <input type="text" name="date" id="date" value = "{0:02.02d}.{1:02.02d}.{2:02.02d}">
              <label for"time">Uhrzeit</label>
              <input type="text" name="time" id="time" value="{3:02.02d}:{4:02.02d}">
            </br>
              <button type="reset">Eingabe zur&uuml;cksetzen</button>
              </br>
              <button type="submit">absenden</button>
            </form>
            </br>
            </br>
            <form method="POST" action="/alarm" id="setAlarm">
              <label form="setAlarm">Weckzeit einstellen</label>
              </br>
              <label for"alarmTime">Uhrzeit</label>
              <input type="text" name="alarmTime" id="alarmTime" value="{3}:{4}" >
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
          <input type="radio" id="MarioMain" name="setSound" value="MarioMain">
            <label for="MarioMain"> Super Mario - Main Theme</label> </br>
            <input type="radio" id="MarioTitle" name="setSound" value="MarioTitle">
              <label for="MarioTitle"> Super Mario - Title Music</label> </br>
            <input type="radio" id="Looney" name="setSound" value="Looney">
              <label for="Looney"> Looney Tunes Theme</label> </br>
            <input type="radio" id="Simpsons" name="setSound" value="Simpsons">
              <label for="Simpsons"> The Simpsons</label> </br>
            <input type="radio" id="Indiana" name="setSound" value="Indiana">
              <label for="Indiana"> Indiana Jones</label> </br>
            <input type="radio" id="Muppets" name="setSound" value="Muppets">
              <label for="Muppets"> The Muppet Show</label> </br>
            <input type="radio" id="Gadget" name="setSound" value="Gadget">
              <label for="Gadget"> Inspector Gadget</label> </br>
            <input type="radio" id="StarWars" name="setSound" value="StarWars">
              <label for="StarWars"> Star Wars Theme</label> </br>
            <input type="radio" id="Tetris" name="setSound" value="Tetris">
              <label for="Tetris"> Tetris Theme</label> </br>
            <button type="submit" id="setSongButton" value="setSong">Song abspielen</button>
            <button type="submit" id="playSongButton" value="playSong">Wecksound w&auml;hlen</button>
          </form>
        </body>
        </html>""".format(date[2], date[1], date[0], date[3], date[4])#.format(0, 1, 2, 3,4, 5)#
    httpResponse.WriteResponseOk(   headers         = ({'Cache-Control': 'no-cache'}),
                                    contentType     = 'text/html',
                                    contentCharset  = 'UTF-8',
                                    content =html)
def start():
    '''
    create server instance and start server
    '''
    srv = MicroWebSrv(webPath = 'www')
    print("Server...")
    srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
    print("...started")
