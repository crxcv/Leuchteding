import network, utime

AP_SSID = "esp32"
AP_PASS = "HuchEinPw"

STA_SSID = "crfb"
STA_PASS = "CS10Ok09"

hostname = "RainbowWarrior"

ap = network.WLAN(network.AP_IF)
sta = network.WLAN(network.STA_IF)

print("\n======== CREATING AP ========\n")
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASS)

timeout = 100
while not ap.isconnected(False):
    utime.sleep_ms(100)
    timeout -= 1
    if timeout <= 0:
        break
print("\n======== AP CONNECTED ========\n")
print(ap.ifconfig())

print("\n========= CONNECTING STA ========\n")
sta.active(True)
networks = sta.scan()
#print(networks)
for nets in networks:
    if nets[0] == STA_SSID.encode('utf-8'):

        sta.connect(STA_SSID, STA_PASS)

        timeout = 100
        while not sta.isconnected():
            utime.sleep_ms(100)
            timeout -= 1
            if timeout <= 0:
                break

        if sta.isconnected():
            print("\n======== STA CONNECTED ========\n")
            print(sta.ifconfig())
        else:
            sta.active(False)
            print("\n======== STA NOT CONNECTED ========\n")


try:
    mdns = network.mDNS()
    mdns.start(hostname, "MicroPython with mDNS")
    mdns.addService('_http', '_tcp', 80, "MicroPython", {"board": "ESP32", "service": "mPy Web server"})
    print("webpage available at {}.local".format(hostname))
except:
    print("mDNS not started")
