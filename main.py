# Begin configuration
TITLE    = "RainbowWarrior"

# End configuration

#import network
#import machine
from microWebSrv import MicroWebSrv
import _thread
import px as px
import connectSTA_AP
#import picoweb

#connect in station mode if possible, else creates access point
#thread_connect = _thread.start_new_thread("thread_wifiConnect", connect, ())
connectSTA_AP.connect()
html = open('www/index.html', 'rb')
srv_run_in_thread = True
light = ""

@MicroWebSrv.route('/')
def _httpHandlerGet(httpClient, httpResponse):
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
            <form action="/TEST" method="post" accept-charset="ISO-8859-1">
                First name: <input type="text" name="firstname"><br />
                Last name: <input type="text" name="lastname"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % httpClient.GetIPAddr()
    httpResponse.WriteResponseOk(   headers    = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = html)

@MicroWebSrv.route('/', 'POST')
def _httpHandlerPost(httpClient, httpResponse) :
    formData = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname  = formData["lastname"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
    """ % ( MicroWebSrv.HTMLEscape(firstname),
            MicroWebSrv.HTMLEscape(lastname) )

    light = formData["light"]
    if "RainbowCycle" in light:
        px.rainbowCycle()
    elif "ColorGradient" in light:
        px.bezier_gradient()
    elif "MeteorRain" in light:
        px.meteorRain()
    elif "Fire" in light:
        px.fire()
        #print("Fire")
    elif "Off" in light:
        px.off()

    httpResponse.WriteResponseOk(headers        = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = html)

srv = MicroWebSrv(webPath = 'www/')
srv.Start(threaded = srv_run_in_thread, stackSize= 8192)
