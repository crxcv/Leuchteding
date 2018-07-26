
import  machine, math, random, gc
import _thread
from time import sleep, sleep_ms
pin = 14
led = 16#12
strip = machine.Neopixel(pin=machine.Pin(pin), pixels=led, type=1)
brightness = 255
strip.color_order("RGBW")

strip.brightness(255, update=True)
fact_cache = {}
threecolors = {"0xff0000", "0x00ff00", "0x00ffff"}

lightAnim_thread = 0
_thread.allowsuspend(True)

#for fire function
w, h = 3, led
#oldColor = [[ 0x00 for x in range (w)] for y in range(h)]

def checkNotification():
    """#check for thread notifications
    if exit notfication exists, turn off all led and return True
    else return False"""
    ntf = _thread.getnotification()
    if ntf == _thread.EXIT:
        print("exiting lightThread")
        strip.clear()
        return True
    return False

#set brightness
def setBrightness(ldrVal):
    """setBrightnes(ldrVal)
    maps the ldrVal (between 0 and 1024) to the brightness value (between 0 and 255)
    ldrVal: value read by ldr sensor
    """
    global brightness
    brightness = ldrVal/1050 * 255
    strip.brightness(int(brightness), update=True)
# ------------converting values
def hex_to_RGB(hexInput):
    '''
    hex_to_RGB(hexInput)
    converts the hexadecimal value to list of rgb values
    hexInput: hexadecimal value  ("FFFFFF" / "0xFFFFFF")
    return value: list containing integer value for red, green and blue -> [255,255,255] '''
    hexVal = hexInput
    if hexInput == 0:
        return (0, 0, 0)
    if isinstance(hexVal, int):
        hexVal = hex(hexInput)
    #print("hexVal: {}".format(hexVal))
    # Pass 16 to the integer function for change of base
    return [int(hexVal[i:i+2],16) for i in range(2,7,2)]
    #return tuple(map(ord,hex[1:].decode('hex')))

# def RGB_to_touple(RGB):
#     '''[255,255,255] -> (255,255,255)'''
#     return (RGB[0], RGB[1],RGB[2])

def RGB_to_hex(RGBin):
    '''RGB_to_hex(RGBin)
    converts list of containing values for red, green and blue to integers and then
    to one hexadecimal value and returns it as integer
    RGBin: List containing RGB Values
    return value: hexadecimal value as integer
     [255,255,255] -> "0xFFFFFF" '''
    # Components need to be integers for hex to make sense
    #RGB = [int(x) for x in RGBin]
    #tprint(RGBin)
    return int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGBin]))
# ---------- end conv. values ------------------

def setAll(red, green, blue, brightness, wait = 0.0):
    """setAll(red, green, blue, brightness, wait=0.0)
    sets all pixels in color defined by red, green, blue"""
    RGB =[str(red), str(green), str(blue)] #[int(red, 16), int(green, 16), int(blue, 16)]
    #RGB = [int(x) for x in val]
    colInt = RGB_to_hex([green, red, blue])#int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
    strip.set(0, colInt, num=led, update=False )
    strip.show()
    sleep(wait)
#'''
#let all led blink for count times
#@val count: how many times the leds blink. default= 2
#'''
def blink(count = 2):
    print("blink")
    for i in range(count):
        strip.set(0, 0xfff216, num=led)
        sleep(0.3)
        strip.set(0, 0x00, num=led)
        sleep(0.2)

def Wheel(wheelPos):
    """# For  Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r"""
    #print("wheel")
    wheelPos = 255 -  wheelPos
    if( wheelPos < 85) :
        return [255 -  wheelPos * 3, 0,  wheelPos * 3]
    elif( wheelPos < 170):
        wheelPos -= 85
        return [0,  wheelPos * 3, 255 -  wheelPos * 3]
    else:
        wheelPos -= 170
        return [wheelPos * 3, 255 -  wheelPos * 3, 0]

def rainbow(wait = 0.00):
    global brightness
    print("rainbow")
    for i in range (1, led+1):
        val = Wheel(int(i * 256 / led ) & 255 )
        RGB = [int(x) for x in val]
        colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
        strip.set(i, colInt, update=False)
        gc.collect()
    strip.show()
    sleep(wait)

# Slightly different, this makes the rainbow equally distributed throughout
def rainbowCycle(wait=0.00):
    global brightness

    print("rainbowCycle")
    for j in range (256): #5 cycles of all colors on wheel
        machine.resetWDT()

        #check if thread got notificatio to exit and exit if it is so
        if checkNotification():
            return

        #set all pixel in rainbow colors
        for i in range (0, led):
            val = Wheel((int(i * 256 / led)+j ) & 255 )
            RGB = [int(x) for x in val]
            colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
            strip.set(i, colInt, update=False)

        strip.show()
        gc.collect()
        sleep(wait)

    print("all cycles done")

# --------colorGradient + dependencies -------------
def color_dict(gradient):
    ''' Takes in a list of RGB sub-lists and returns dictionary of
        colors in RGB and hex form for use in a graphing function
        defined later on '''
    return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
        "r":[RGB[0] for RGB in gradient],
        "g":[RGB[1] for RGB in gradient],
        "b":[RGB[2] for RGB in gradient]}

def fact(n):
    ''' Memoized factorial function '''
    try:
        return fact_cache[n]
    except(KeyError):
        if n == 1 or n == 0:
            result = 1
        else:
            result = n*fact(n-1)
        fact_cache[n] = result
        return result

def bernstein(t,n,i):
    ''' Bernstein coefficient '''
    binom = fact(n)/float(fact(i)*fact(n - i))
    return binom*((1-t)**(n-i))*(t**i)


def bezier_gradient(colors=None, n_out=None):
    ''' Returns a "bezier gradient" dictionary
        using a given list of colors as control
        points. Dictionary also contains control
        colors/points. '''

    print("gradient")
    def bezier_interp( t):
        ''' Define an interpolation function
            for this specific curve'''
        # List of all summands
        summands = [
            list(map(lambda x: int(bernstein(t,n,i)*x), c))
            for i, c in enumerate(RGB_list)
            ]
        # Output color
        out = [0,0,0]
        # Add components of each summand together
        for vector in summands:
            for c in range(3):
                out[c] += vector[c]

        return int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in out]))


    if colors is None:
        colors=threecolors
    if n_out is None:
        n_out = led

    # RGB vectors for each color, use as control points
    RGB_list = [hex_to_RGB(color) for color in colors]
    n = len(RGB_list) - 1
    gradient = [
        bezier_interp(float(t)/(n_out-1))
        for t in range(n_out)
    ]
    for n in range(len(gradient)):
        strip.set(n,  gradient[n], update=False)
        #strip.set((led-n), gradient[n], update=False)
    strip.show()
    gc.collect()

    #{"#00173d", "#f75002", "#01f2f7"}
    #for col in colors:
    #strip.show()
    # Return all points requested for gradient
    #return {
        #"gradient": color_dict(gradient),
        #"control": color_dict(RGB_list)
    #}
# ---------- end of bezier_gradient-------------

# ------------ fire --------------------
def fire(cooling = 70, sparkling = 140, speedDelay = 0.0):
    #w, h = 3, led

    print("fire")
    heat = [0x00 for x in range(led, 0, -1)]
    cooldown = 0
    while True:
    #for i in range(20):
        #check if thread got notificatio to exit and exit if it is so
        if checkNotification():
            return

        # Step 1: cool down every cell a little
        for i in range(led):
            cooldown = random.randint(0, int((cooling * 10) / led) +2)

            if (cooldown > heat[i]):
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown

        # Step 2: Heat from each cell drifts
        #for k in range(int(led/2)-1, 1, -1):
        for k in range(led-1, 2, -1):
            #print("heat: k= {}".format(k))
            heat[k] = (heat[k-1] +  heat[k-2] + heat[k-2]) / 3

        # Step 3 randomly ignite new "sparks" near the bottom
        if(random.randint(0,255) < sparkling):
            y = random.randint(0,int(led/4))
            #list index out of range!!
            heat[y] = heat[y] + random.randint(160, 255)

        # Step 4 convert heat to led colours
        for j in range(led):
            setPixelHeatColor(j, heat[j])
            #setPixelHeatColor(int(led/2)-j, heat[j])
            #setPixelHeatColor(int(led/2)+j, heat[j])
        strip.show()
        gc.collect()

def setPixelHeatColor(pixel, temp):
    global brightness
    # scale heat down from 0-255 to 0-191
    ht = round((temp/255.0) * 191)

    #calc ramp up from
    heatramp = ht & 0x3f #0..63
    heatramp <<=2  #scale up to 0...252
    val = 0
    #figure out which third of the spectrum we're in
    if (ht > 0x80):             #hottest
        val =[255, 255, heatramp]

    elif ( ht > 0x40):          #middle
        val = [heatramp,255,  0]
    else:                       #coolest
        val = [0, heatramp, 0]
    RGB = [int(x) for x in val]
    colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
    strip.set(pixel, colInt, update=False)
# --------------fire - end -----------------------


# --------------- meteorRain -------------------------
def fadeToBlack(ledNo, fadeValue):
    global brightness
    oldVal = strip.get(ledNo)
    #print("strip.get: {}".format(oldVal))
    oldCol = hex_to_RGB(oldVal[0])
    r = (oldCol[0] | 0x00ff0000) >> 16
    g = (oldCol[1] & 0x0000ff00) >> 8
    b = (oldCol[2] & 0x000000ff)
    w = oldVal[1]

    r= 0 if (r<=10) else int(r-(r*fadeValue/256))
    g= 0 if (g<=10) else int(g-(g*fadeValue/256))
    b= 0 if (b<=10) else int(b-(b*fadeValue/256))
    strip.set(ledNo, int(RGB_to_hex([r,g,b])), update=False)

#0xff,0xff,0xff,7, 255, True, 0.00030
def meteorRain(red=0xff, green=0xff, blue=0xff, meteorSize = 7, meteorTrailDecay = 255, meteorRandomDecay = True, speedDelay = 0.003):
    global brightness
    print("meteorRain")
    setAll(0x00, 0x00, 0x00, 0xFF)

    while True:
        for i in range (led):
            #check if thread got notificatio to exit and exit if it is so
            if checkNotification():
                return

            for j in range (led):
                if (not meteorRandomDecay) or random.randint(0,10) > 5 :
                    fadeToBlack(j, meteorTrailDecay)
            strip.show()

            for j in range (meteorSize):
                if i-j < led and i-j >= 0:
                    strip.set(i-j, int(RGB_to_hex((red, green, blue))), update=False)
            strip.show()
            gc.collect()
            sleep(speedDelay)
# ------------------ meteor end ----------------------------------

#-------------------sparkle----------------------------------
def sparkle():
    print("sparkle")
    speed = 1000

    while True:
        if checkNotification():
            return

        for i in range(1, led+1):
            val = Wheel(random.randint(0,255))
            RGB = [int(x) for x in val]
            color = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))

            if random.randint(0,10)<4:
                strip.set(i, color, update=False)
            else:
                strip.set(i, 0x00, update = False)
        strip.show()
        sleep_ms(10)
        strip.clear
        gc.collect()
#---------------------end of sparkle-------------------------

#-------------------------wave-----------------------------------
def wave():
    print("wave")
    MAX_INT_VALUE = 65536
    frame = 0
    hue    = 180

    while True:
        #strip.clear()
        if checkNotification():
            return

        for i in range(led):
            deg = float(frame + ((MAX_INT_VALUE / led ) * i ))/ (float(MAX_INT_VALUE))*360
            val = math.pow(math.sin(math.radians(deg)), 8)

            if (val>=0):
                col=strip.get(i)
                #print(col)
                #colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in col]))
                old = strip.RGBtoHSB(col[0] )
                h = old[0] + hue
                s = old[1] + 255
                b=old[2] + val*256
                strip.setHSB(i, h, 255, b, num=1, update=False)
            else:
                strip.set(i, 0x00, num=1, update=False)
        strip.show()
        frame += 1000
        gc.collect()
        sleep_ms(1000)
#-----------------end of wave-------------------------

#------------------ripple-----------------------------
def ripple():
    print("ripple")
    currBg = random.randint(0, 256)
    nextBg = currBg
    step = -1
    maxSteps = 16
    center = 0
    fadeRate = 0.8

    def wrap( step):
        if(step < 0):
            return led + step
        if(step > led - 1):
            return step - led
        return step

    while True:
        if checkNotification():
            return

        if currBg is nextBg:
            nextBg = random.randint(0, 256)
        elif nextBg > currBg:
            currBg+= 1
        else:
            currBg-=1

        for i in range(led):
            strip.setHSB(i, currBg, 255, 50, update=False)

        if step is -1:
            center = random.randint(0, led)
            color = random.randint(0, 256)
            steop = 0

        if step is 0:
            strip.setHSB(center,color, 255, 255, update=False)
            step+=1

        else:
            if step < maxSteps:
                strip.setHSB(wrap(center + step), color, 255, pow(fadeRate, step)*255, update=False)
                if step > 3:
                    strip.setHSB(wrap(center + step - 3),color, 255, pow(fadeRate, step - 2)*255, update=False)
                    strip.setHSB(wrap(center - step + 3),color, 255, pow(fadeRate, step - 2)*255, update=False)
                step +=1
            else:
                step = -1
        strip.show()
        gc.collect()
        sleep_ms(100)
#------------------end of ripple--------------------------

#turn off all pixels
def off():
    """off()
    turns off all pixels"""
    print("off")
    strip.set(0, 0x00, num=led)



#def thread(val, threadID):
def thread(val):
    val = val % 11
    print("started thread {}".format(val))
    #_thread.lock()
    gc.collect()
    before = gc.mem_free()
    #_thread.suspend(threadID)
    #while True:
    if val is 10:
        wave()
    if val is 8:
        ripple()
    if val is 7:
        sparkle()
    if val is 6:
        meteorRain()
    if val is 5:
        rainbowCycle()
    elif val is 4:
        bezier_gradient()
    elif val is 3:
        blink()
    elif val is 2:
        fire()
    elif val is 1:
        rainbow()
    elif val is 0:
        off()
    else:
        setAll(23, 230, 180, 255)
    after = gc.mem_free()
    gc.collect()
    #_thread.unlock()
    #_thread.resume(threadID)

    print("thread takes {} bytes".format(before-after))
