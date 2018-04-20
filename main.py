# Begin configuration
TITLE    = "RainbowWarrior"

# End configuration

#import network
#import machine
import usocket
import px as px
import connectSTA_AP

#connect in station mode if possible, else creates access point
connectSTA_AP.connect()

#px = px.Pixels(pin = 14, numLed = 60)

def start(socket, query):
    socket.write("HTTP/1.1 OK\r\n\r\n")
    html = open('index.html', 'rb')
    socket.write(html.read())


def err(socket, code, message):
    socket.write("HTTP/1.1 "+code+" "+message+"\r\n\r\n")
    socket.write("<h1>"+message+"</h1>")

def handle(socket):
    (method, url, version) = socket.readline().split(b" ")
    if b"?" in url:
        (path, query) = url.split(b"?", 2)
    else:
        (path, query) = (url, b"")

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
            start(socket, query)
        elif path == b"/light":
            start(socket,query)

            if "RainbowCycle" in query:
                px.rainbowCycle()
            elif "ColorGradient" in query:
                px.bezier_gradient()
            elif "MeteorRain" in query:
                px.meteorRain()
            elif "Fire" in query:
                px.fire()
                #print("Fire")
            elif "Off" in query:
                px.off()
        else:
            err(socket, "404", "Not Found")
    else:
        err(socket, "501", "Not Implemented")

server = usocket.socket()
server.bind(('0.0.0.0', 80))
server.listen(1)
#px.off()

while True:
    try:
        (socket, sockaddr) = server.accept()
        handle(socket)
    except:
        socket.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
        socket.write("<h1>Internal Server Error</h1>")
    socket.close()
