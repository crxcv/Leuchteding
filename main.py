# Begin configuration
TITLE    = "RainbowWarrior"

# End configuration

#import network
from machine import Pin, TouchPad, ADC, DAC, PWM
from microWebSrv import MicroWebSrv
import _thread
import px as px
import connectSTA_AP
#import micropython
import time
import piezo as pz

#pz.find_song('TopGun')

#exception buffer for interrupt handler
#micropython.alloc_memory_exception_buff(100)

#connect in station mode if possible, else creates access point
#thread_connect = _thread.start_new_thread("thread_wifiConnect", connect, ())
#connectSTA_AP.connect()
html = open('www/index.html', 'r')
srv_run_in_thread = True
light = ""

touchLight = TouchPad(Pin(27))
touchLight.config(600)
touchThreshold = touchLight.read() - 400
lightCase = 0
lightMax = 5

ldr = ADC(Pin(36, Pin.IN))
#set attenuation range from 0-3.6V
#ldr.atten(ADC.ATTN_11DB)
#set capture width
#ldrPin.width(ldrPin.WIDTH_10BIT)
#ldrVal = ldrPin.read()
#print("ldr value at start: {}".format(ldrVal))
#causes stack overflow :assertion "heap != NULL && "free() target pointer i***ERROR*** A stack overflow in task IDLE has been detected
#px.setBrightness(ldrVal)


oldLightVal = 0

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
        lightCase = 4
        #px.rainbowCycle()
    elif "ColorGradient" in light:
        lightCase = 3
        #px.bezier_gradient()
    elif "MeteorRain" in light:
        lightCase = 2
        #px.meteorRain()
    elif "Fire" in light:
        px.fire()
        #lightCase = 1
        #print("Fire")
    elif "Off" in light:
        lightCase = 0
        #px.off()
    startLightThread(lightCase)


    httpResponse.WriteResponseOk(headers        = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = html)

#srv = MicroWebSrv(webPath = 'www/')
#srv.Start(threaded = srv_run_in_thread, stackSize= 8192)

def lightFunc(lightVal):
    #elif ntf == _thread.SUSPEND

    if lightVal is 0:
        print("turning pixels off")
        px.off();
    elif lightVal is 1:
        print("starting fire anim")
        px.fire();
    elif lightVal is 2:
        print("starting meteor anim")
        px.meteorRain();
    elif lightVal is 3:
        print("starting bezier anim")
        px.bezier_gradient();
    elif lightVal is 4:
        print("starting rainbow anim")
        px.rainbowCycle();

def theremin():
    piezo=PWM(26)
    piezo.duty(50)
    while True:
        print(ldr.read())
        piezo.freq(ldr.read())
        time.sleep_ms(200)


def startLightThread(lightCase):
    _thread.notify(lightAnim_thread, _thread.EXIT)
    time.sleep_ms(300)

    _thread.stop(lightAnim_thread)
    time.sleep_ms(300)

    lightAnim_thread = _thread.start_new_thread("lightAnim", lightFunc, (lightCase,))



lightAnim_thread = _thread.start_new_thread("lightAnim", lightFunc, (lightCase, ))


while True:
    #ntf = _thread.getnotification()
    #ldrVal = ldrPin.readraw()
    #print("ldr value: {}".format(ldrPin.read()))
    time.sleep_ms(300)
    #piezo.freq(ldrVal)
    touchval = touchLight.read()
    val = ldr.read()
    print("ldr: {}".format(val))

    if touchval < 400 and touchval > 100:
        #print("got triggered\nlightCase: ")
        lightCase = [lightCase +1, 0][lightCase+1 >= lightMax]
        print(lightCase)
        print("touchVal: {}".format(touchval))
        _thread.notify(lightAnim_thread, _thread.EXIT)
        time.sleep_ms(300)

        _thread.stop(lightAnim_thread)
        time.sleep_ms(300)
        try:
            lightAnim_thread = _thread.start_new_thread("lightAnim", lightFunc, (lightCase,))

        except Exception as e:
            print("some error occured: {}".format(e))
        time.sleep_ms(500)
    #touchLight.irq(trigger=Pin.IRQ_FALLING, handler = lightFunc)
