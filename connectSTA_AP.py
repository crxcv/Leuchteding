import network
ap_if = False
sta_if = False

def connect():
    global ap_if
    global sta_if
    STA_SSID = "deineSSID"
    STA_PSK  = "deinPasswort"
    ssid = "esp32"
    pw = "HuchEinPw"
    tries = 0


    #STA_SSID = home.getSsid()
    #STA_PSK = home.getPass()

    ap_if = network.WLAN(network.AP_IF)
    sta_if = network.WLAN(network.STA_IF)
    if ap_if.active(): ap_if.active(False)
    if not ap_if.active():
        sta_if.active(True)
        sta_if.connect(STA_SSID, STA_PSK)
    if not sta_if.isconnected():
        ap_if.active(True)
        sta_if.connect(STA_SSID, STA_PSK)
        print("creating accesspoint")
        # if not sta_if.isconnected():
        ap_if.config(essid = ssid)
        ap_if.config(password = pw)

    try:
        mdns = networkself.mDNS()
        mdns.start("RainbowWarrior", "MicroPython with mDNS")
        mdns.addService('_http', '_tcp', 80, "MicroPython", {"board": "ESP32", "service": "mPy Web server"})
    except:
        print("mDNS not started")

def station_activated():
    print("stationMode activated: {}".format(sta_if))
    return sta_if
