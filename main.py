# Begin configuration
TITLE    = "RainbowWarrior"
GPIO_NUM = 5
STA_SSID = "crfb"
STA_PSK  = "CS10Ok09"
# End configuration

import network
import machine
import ujson, usocket#, px
#import #pxFx as #pxFx



ap_if = network.WLAN(network.AP_IF)
if ap_if.active(): ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
if not ap_if.active(): sta_if.active(True)
if not sta_if.isconnected(): sta_if.connect(STA_SSID, STA_PSK)

ip=ap_if.ifconfig()
print(ip[0])

#px = px.Pixels()
#pxFx = #pxFx.Pixels()
#px.off()

pin = machine.Pin(GPIO_NUM)
pin.init(pin.OUT)
pin.value(0)

def ok(socket, query):
    socket.write("HTTP/1.1 OK\r\n\r\n")
    socket.write("<!DOCTYPE html><title>"+TITLE+"</title><body>")
    socket.write("<h1>"+TITLE+"</h1>")
    socket.write("<br>")
    socket.write("<p>"+
                "<form method='GET' >"+
                "<h2>Select Color Pattern:</h2></br>"
                "<input type='radio' id='light1' name='lights' value='RainbowCycle'>RainbowCycle</br>"+
                "<input type='radio' id='light2' name='lights' value='Rainbow'>Rainbow</br>"+
                "<input type='radio' id='light3' name='lights' value='meteorRain'>MeteorRain</br>"+
                "<input type='radio' id='light4' name='lights' value='ColorGradient'>ColorGradient</br></br>"+
                "<input type='radio' id='light4' name='lights' value='fire'>Fire</br></br>"+
                "<input type='radio' id='light4' name='lights' value='ColorGradient'>ColorGradient</br></br>"+
                "<input type='submit' name='light' value='Submit form'></br>"+
                "</form>"+
                "</p>")


    if pin.value():
        socket.write("<span style='color:green'>ON</span>")
    else:
        socket.write("<span style='color:red'>OFF</span>")
    socket.write("<br>")
    if pin.value():
        socket.write("<form method='POST' action='/off?"+query.decode()+"'>"+
                     "<input type='submit' value='turn OFF'>"+
                     "</form>")
    else:
        socket.write("<form method='POST' action='/on?"+query.decode()+"'>"+
                     "<input type='submit' value='turn ON'>"+
                     "</form>")

def err(socket, code, message):
    socket.write("HTTP/1.1 "+code+" "+message+"\r\n\r\n")
    socket.write("<h1>"+message+"</h1>")

def handle(socket):
    (method, url, version) = socket.readline().split(b" ")
    if b"?" in url:
        (path, query) = url.split(b"?", 2)
    else:
        (path, query) = (url, b"")
    #print(path)
    #print(query)
    parsed = ujson.loads(path)

    while True:
        header = socket.readline()
        if header == b"":
            return
        if header == b"\r\n":
            break

    if version != b"HTTP/1.0\r\n" and version != b"HTTP/1.1\r\n":
        err(socket, "505", "Version Not Supported")
    elif method == b"GET":
        if path == b"/":
            ok(socket, query)
        #elif path == b"/light":
            #ok(socket, query)
            #if parsed["lights"] == "RainbowCycle":
            #    px.rainbowCycle()
            #elif parsed["lights"] == "meteorRain":
                #pxFx.meteorRain()
            #elif parsed["lights"] == "ColorGradient":
            #    px.ColorGradient()
            #elif parsed["lights"] == "fire":
                #pxFx.fire()

        else:
            err(socket, "404", "Not Found")
    elif method == b"POST":
        if path == b"/on":
            pin.high()
            ok(socket, query)
        elif path == b"/off":
            pin.low()
            ok(socket, query)
        #elif path == b"/light":
        #    ok(socket, query)
        else:
            err(socket, "404", "Not Found")
    else:
        err(socket, "501", "Not Implemented")

server = usocket.socket()
server.bind(('0.0.0.0', 80))
server.listen(1)
while True:
    try:
        (socket, sockaddr) = server.accept()
        handle(socket)
    except:
        socket.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
        socket.write("<h1>Internal Server Error</h1>")
    socket.close()
