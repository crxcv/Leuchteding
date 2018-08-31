from microWebSrv import MicroWebSrv
import _thread
import time, utime
from machine import RTC
import json

srv_run_in_thread = True
date= utime.localtime()#(0, 0, 0, 0, 0)
alarmTime = (date[3], date[4])

#route handler for http-post requests
@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    if formData:
        # send notification value to all threads so they can abort
        # 0 as 1st argument means that notification goes to every thread
        _thread.notify(0, 666)

        #print(formData)
        if "light" in formData:
            _thread.sendmsg(_thread.getReplID(), "light:{}".format(formData["light"]))

    #_thread.notify(0, _thread.SUSPEND)
    #_thread.wait()
    httpResponse.WriteResponseFile(filepath = 'www/index.html', contentType= "text/html", headers = None)
    #_thread.notify(0, _thread.RESUME)


@MicroWebSrv.route('/led')
@MicroWebSrv.route('/led', 'POST')
def _httpHandlerLEDPost(httpClient, httpResponse):
    colors=httpClient.ReadRequestContentAsJSON()#ReadRequestPostedFormData()# #Read JSON color data
    print(colors)
    _thread.notify(0, 666)

    if colors:
        # send notification value to all threads so they can abort
        # 0 as 1st argument means that notification goes to every thread
        red = colors.get('red')
        green = colors.get('green')
        blue= colors.get('blue')
        rgb = tuple((red, green, blue))
        print("rgb {}".format(rgb))
        _thread.sendmsg(_thread.getReplID(), "colors: {}".format(rgb))
    #_thread.notify(0, _thread.SUSPEND)
    httpResponse.WriteResponseFile(filepath = 'www/led.html', contentType= "text/html", headers = None)


@MicroWebSrv.route('/alarm')
@MicroWebSrv.route('/alarm', 'POST')
def _httpHandlerAlarm(httpClient, httpResponse):


    global date
    global alarmTime

    formData = httpClient.ReadRequestPostedFormData()
    print(formData)
    date = utime.localtime()
    if formData:
        # send notification value to all threads so they can abort
        # 0 as 1st argument means that notification goes to every thread
        _thread.notify(0, 666)

        if "time" in formData:
            day =   int(formData["date"].split('.')[0])
            month = int(formData["date"].split('.')[1])
            year =  int(formData["date"].split('.')[2])

            #newTime = int(formData["time"])
            hour =  int(formData["time"].split(':')[0])
            min =   int(formData["time"].split(':')[1])
            #print("time set by srv to {0}:{1} {2}.{3}.{4}".format(hour, min, day, month, year))
            date=(year, month, day, hour, min)
            print("time set to: {}".format(date))
            _thread.sendmsg(_thread.getReplID(), "time:{}".format(date))

        if "setAlarm" in formData:
            hour =  int(formData["alarmTime"].split(':')[0])
            min =   int(formData["alarmTime"].split(':')[1])
            #print("alarm set by srv to {0}:{1}".format(hour, min))
            alarmTime = (hour, min)
            _thread.sendmsg(_thread.getReplID(), "alarm:{}".format(alarmTime))

        if "setSound" in formData:
            song = formData["setSound"]
            _thread.sendmsg(_thread.getReplID(), "song:{}".format(song))
            #print (formData)
    #0: year    1: month 2: mday 3: hour 4: min 5: sec 6: weekday 7: yearday
    #data = RTC.now()
    #time = str("{0}.{1}.{3} {4}:{5} Uhr".format(data[2], data[1], data[0], data[3], data[4]))
    html ="""\
<html lang=de>

<head>
  <title>RainbowWarrior Uhr- und Weckzeiteinstellungen</title>

  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="bootstrap.min.css">
  <link rel="stylesheet" href="style.css">
</head>



<body class="h-100">
  <div class="ground"></div>
  <div class="sky">
    <div class="cloud variant-1"></div>
    <div class="cloud variant-2"></div>
    <div class="cloud variant-3"></div>
    <div class="cloud variant-4"></div>
    <div class="cloud variant-5"></div>
  </div>
  <div class="rainbow-preloader">
    <div class="rainbow-stripe"></div>
    <div class="rainbow-stripe"></div>
    <div class="rainbow-stripe"></div>
    <div class="rainbow-stripe"></div>
    <div class="rainbow-stripe"></div>
    <div class="shadow"></div>
    <div class="shadow"></div>
  </div>
  <div class="container text-white align-items-center d-flex flex-column h-100 justify-content-end pb-md-5">
    <div class="sticky-top" id="id3">
      <a href ="/" class ="btn btn-dark btn-lg" role="button"> Animationen </a>
      <a href ="/alarm" class ="btn btn-dark btn-lg" role="button" disabled> Alarm </a>
      <a href ="/led" class ="btn btn-dark btn-lg" role="button"> Farbe ausw&auml;hlen </a>
    </div>
    <h1 id="id1">RaibowWarrior</h1>
    <h2 id="id3">Uhr- und Weckzeit einstellen</h2>

    <p>
      {0:02.02d}.{1:02.02d}.{2:02.02d} {3:02.02d}:{4:02.02d} Uhr
    </p>
    <div class="row w-100" id="id1">
      <div class="col-md-6">

        <form method="POST" action="/alarm" id="setTime">
          <h2 form="setTime">Systemzeit einstellen</h2>
          <div class="row">
            <div class="col-md-6">
              <label for "year">Datum</label>
              <input class="form-control" type="text" name="date" id="date" value="{0:02.02d}.{1:02.02d}.{2:02.02d}">
            </div>
            <div class="col-md-6">
              <label for "time">Uhrzeit</label>
              <input class="form-control" type="text" name="time" id="time" value="{3:02.02d}:{4:02.02d}">
            </div>
          </div>
          <button class="btn btn-dark" type="submit">absenden</button>
        </form>
        <form method="POST" action="/alarm" id="setAlarm">
          <h2 form="setAlarm">Weckzeit einstellen</h2>
          <div class="row">
            <div class="col-md-6">
              <label for "alarmTime">Uhrzeit</label>
              <input class="form-control" type="text" name="alarmTime" id="alarmTime" value="{5:02.02d}:{6:02.02d}">
            </div>
            <!--<div class="col-md-6">
              <label for "alarmTime">Uhrzeit</label>
              <input type="checkbox" name="dailyAlarm" value="dailyAlarm" checked="checked"> daily Alarm
              </label>
            </div>-->

          </div>
          <button class="btn btn-dark" type="submit" name="setAlarm" value="setAlarm">Eingabe absenden</button>
        </form>
      </div>
      <div class="col-md-6">
        <form method="POST" action="/alarm" id="setSound">
          <h2 form="setSound">Wecksound w&auml;hlen</h2>
          </br>
          <input type="radio" id="MarioMain" name="setSound" value="MarioMain">
          <label for="MarioMain"> Super Mario - Main Theme</label>
          </br>
          <input type="radio" id="MarioTitle" name="setSound" value="MarioTitle">
          <label for="MarioTitle"> Super Mario - Title Music</label>
          </br>
          <input type="radio" id="Looney" name="setSound" value="Looney">
          <label for="Looney"> Looney Tunes Theme</label>
          </br>
          <input type="radio" id="Simpsons" name="setSound" value="Simpsons">
          <label for="Simpsons"> The Simpsons</label>
          </br>
          <input type="radio" id="Indiana" name="setSound" value="Indiana">
          <label for="Indiana"> Indiana Jones</label>
          </br>
          <input type="radio" id="Muppets" name="setSound" value="Muppets">
          <label for="Muppets"> The Muppet Show</label>
          </br>
          <input type="radio" id="Gadget" name="setSound" value="Gadget">
          <label for="Gadget"> Inspector Gadget</label>
          </br>
          <input type="radio" id="StarWars" name="setSound" value="StarWars">
          <label for="StarWars"> Star Wars Theme</label>
          </br>
          <input type="radio" id="Tetris" name="setSound" value="Tetris">
          <label for="Tetris"> Tetris Theme</label>
          </br>
          <button class="btn btn-dark" type="submit" name="setSongButton" value="setSong">Song w&aumlhlen</button>
          <!--<button class="btn btn-dark" type="submit" name="playSongButton" value="playSong">Wecksound w&auml;hlen</button>
          -->

        </form>
      </div>
    </div>
</body>
</html>

    """.format(date[2], date[1], date[0], date[3], date[4], alarmTime[0], alarmTime[1])#.format(0, 1, 2, 3,4, 5)#
    #_thread.notify(0, _thread.SUSPEND)
    httpResponse.WriteResponseOk(   headers         = ({'Cache-Control': 'no-cache'}),
                                    contentType     = 'text/html',
                                    contentCharset  = 'UTF-8',
                                    content =html)
    #_thread.notify(0, _thread.RESUME)

def start():
    '''
    create server instance and start server
    '''
    #global mainThread

    srv = MicroWebSrv(webPath = 'www')
    print("Server...")
    srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
    print("...started")
    #mainThread = _thread.getReplID()
    return srv.threadID()
