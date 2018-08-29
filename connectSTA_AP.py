import network, utime
ap_if = False
sta_if = False

def connect():
    global ap_if
    global sta_if
    STA_SSID = "crfb"
    STA_PSK  = "CS10Ok09"
    ssid = "esp32"
    pw = "HuchEinPw"

    ap_if = network.WLAN(network.AP_IF)
    sta_if = network.WLAN(network.STA_IF)

    sta_if.active(True)
    sta_if.connect(STA_SSID, STA_PSK)

    timeout = 50
    while not sta_if.isconnected():
        utime.sleep_ms(100)
        timeout -= 1
        if timeout == 0:
            break
    print("======= STA connected ========")
    print(sta_if.ifconfig())

    print("creating accesspoint")
    ap_if.active(True)
    ap_if.config(essid = ssid, password = pw)

    timeout = 50
    while not ap_if.isconnected():
        utime.sleep_ms(100)
        timeout -= 1
        if timeout == 0:
            return
    print("======= AP connected ========")
    print(ap_if.ifconfig)

    try:
        mdns = network.mDNS()
        mdns.start("RainbowWarrior", "MicroPython with mDNS")
        mdns.addService('_http', '_tcp', 80, "MicroPython", {"board": "ESP32", "service": "mPy Web server"})
    except:
        print("mDNS not started")
