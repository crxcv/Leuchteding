import time, machine, math, random, _thread

pin = 14
led = 60
strip = machine.Neopixel(machine.Pin(pin), led, 0)
fact_cache = {}
threecolors = {"#00173d", "#f75002", "#01f2f7"}

#for fire function
w, h = 3, int(led/2)
#oldColor = [[ 0x00 for x in range (w)] for y in range(h)]

# ------------converting values
def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]

# def RGB_to_touple(RGB):
#     '''[255,255,255] -> (255,255,255)'''
#     return (RGB[0], RGB[1],RGB[2])


def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB])
# ---------- end conv. values ------------------


# For Rainbow Input a value 0 to 255 to get a color value.
# The colours are a transition r - g - b - back to r.
def Wheel(wheelPos):
    wheelPos = 255 -  wheelPos
    if( wheelPos < 85) :
        return [255 -  wheelPos * 3, 0,  wheelPos * 3]
    elif( wheelPos < 170):
        wheelPos -= 85
        return [0,  wheelPos * 3, 255 -  wheelPos * 3]
    else:
        wheelPos -= 170
        return [wheelPos * 3, 255 -  wheelPos * 3, 0]

# Slightly different, this makes the rainbow equally distributed throughout
def rainbowCycle(wait=0.003):
    _thread.allowsuspend(True)

    print("rainbowCycle")
    while True:
        for j in range (256*5): #5 cycles of all colors on wheel
            ntf = _thread.getnotification()
            if ntf == _thread.EXIT:
                return
            for i in range (0, led):


                val = Wheel((int(i * 256 / led)+j ) & 255 )
                RGB = [int(x) for x in val]
                colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
                #print("got color from wheel")
                strip.set(i, colInt)
            ##strip.show()
            time.sleep(wait)

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
    _thread.allowsuspend(True)
    #print("bezier")
    ''' Returns a "bezier gradient" dictionary
        using a given list of colors as control
        points. Dictionary also contains control
        colors/points. '''
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
    while True:
        ntf = _thread.getnotification()
        if ntf == _thread.EXIT:
            return

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
            strip.set(n,  gradient[n])
            strip.set((led-1-n), gradient[n])

        #strip.show()
        # Return all points requested for gradient
        return {
            "gradient": color_dict(gradient),
            "control": color_dict(RGB_list)
        }
# ---------- end of bezier_gradient-------------

# ------------ fire --------------------
def fire(cooling = 55, sparkling = 120, speedDelay = 0.00000015):
    #w, h = 3, led
    _thread.allowsuspend(True)
    heat = [0x00 for x in range(int(led), 0, -1)]
    cooldown = 0
    while True:
        # Step 1: cool down every cell a little
        ntf = _thread.getnotification()
        if ntf == _thread.EXIT:
            return

        for i in range(int(led)):
            cooldown = random.randint(0, int((cooling * 10) / int(led)) +2)

            if (cooldown > heat[i]):
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown

        # Step 2: Heat from each cell drifts
        for k in range(int(led)-1, 1, -1):
            heat[k] = (heat[k-1] +  heat[k-2] + heat[k-2]) / 3

        # Step 3 randomly ignite new "sparks" near the bottom
        if(random.randint(0,255) < sparkling):
            y = random.randint(0,7)
            heat[y] = heat[y] + random.randint(160, 255)

        # Step 4 convert heat to led colours
        for j in range(int(led)):
            setPixelHeatColor(j, heat[j])
            #setPixelHeatColor(int(led/2)-j, heat[j])
            #setPixelHeatColor(int(led/2)+j, heat[j])
        #strip.show()
        time.sleep(speedDelay/10000)

def setPixelHeatColor(pixel, temp):
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
        val = [255, heatramp, 0]
    else:                       #coolest
        val = [heatramp, 0, 0]
    RGB = [int(x) for x in val]
    colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
    strip.set(pixel, colInt)
# --------------fire - end -----------------------

# --------------- meteorRain -------------------------

def setAll(red, green, blue):
    for i in range (led):
        strip.set(i,RGB_to_hex(red, green, blue))


def fadeToBlack(ledNo, fadeValue):
    oldVal = strip.get(ledNo)
    oldCol = RGB_to_hex(oldVal)
    r = (oldVal[0] | 0x00ff0000) >> 16
    g = (oldVal[1] & 0x0000ff00) >> 8
    b = (oldVal[2] & 0x000000ff)


    r= 0 if (r<=10) else int(r-(r*fadeValue/256))
    g= 0 if (g<=10) else int(g-(g*fadeValue/256))
    b= 0 if (b<=10) else int(b-(b*fadeValue/256))
    strip.set(ledNo, RGB_to_hex(r,g,b))
    #strip.write()

#0xff,0xff,0xff,7, 255, True, 0.00030
def meteorRain(red=0xff, green=0xff, blue=0xff, meteorSize = 7, meteorTrailDecay = 255, meteorRandomDecay = True, speedDelay = 0.00030):
    _thread.allowsuspend(True)

    setAll(0,0,0);

    for i in range (led):
        ntf = _thread.getnotification()
        if ntf == _thread.EXIT:
            return

        for j in range (led):
            if (not meteorRandomDecay) or random.randint(0,10) > 5 :
                fadeToBlack(j, meteorTrailDecay)

        for j in range (meteorSize):
            if i-j < led and i-j >= 0:
                strip.set(i-j, RGB_to_hex(red, green, blue))
        #strip.show()
        time.sleep(speedDelay)
# ------------------ meteor end ----------------------------------

#turn off all pixels
def off():
    for i in range (led):
        strip.set(i, 0x00)
    #strip.show()
