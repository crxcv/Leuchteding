import machine, _thread
import utime, random, math

led_pin = machine.Pin(14, machine.Pin.OUT)
num_pixels = 14

strip = machine.Neopixel(pin=led_pin, pixels=num_pixels, type=1)

def set_brightness(brightness_val):
    strip.brightness(brightness_val)


def waitForExitNotification(timeout):
    """ waitForExitNotification(timeout)
    uses _thread.wait(timeout) to sleep for amount of ms saved in timeout and
    checks notfication for _thread.EXIT notification. Returns True if
    _thread.EXIT notification is recieved, else returns False

    timeout: (ms) time in ms used for _thread.wait()
    return: (boolean) True if _thread.EXIT is recieved, else False.
    """
    notification = _thread.wait(timeout)
    if notification == _thread.EXIT:
        strip.set(0, 0x00, num=num_pixels)
        print("stopping animation")
        return True
    else:
        return False

def blink(color = random.randint(0, 0xffffff), count = 3, time_on = 200, time_off = 100):
    print("blink")
    for i in range(count):
        strip.set(0, color, num=num_pixels)
        utime.sleep_ms(time_on)
        strip.set(0, 0x00, num=num_pixels)
        utime.sleep_ms(time_off)

def running_dot(color = 0x00FFFF, time_on=50):
    print("running_dot")
    while True:
        for i in range(num_pixels):
            pos1 = (i-1) % num_pixels
            pos2 = (i-2) % num_pixels
            pos3 = (i-3) % num_pixels

            positions = (i, pos1, pos2, pos3)
            white_level = 0
            for j in positions:
                strip.set(j+1, color, white=white_level, update = False)
                white_level += 50
            strip.show()
            if waitForExitNotification(time_on):
                return

            for j in positions:
                strip.set(j+1, 0x00, update=False)
            strip.show()
            if waitForExitNotification(1):
                return

def crossing_dots(color1= 0xFFFF00, color2 = 0xff00ff, time_on = 50):
    print("crossing_dots")
    while True:
        col1 = random.randint(0, 16777214)
        col2 = random.randint(0, 16777214)
        for i in range(1, num_pixels+1):
            strip.set(i, col1, update=False)
            strip.set(num_pixels+1-i, col2, update=False)
            strip.show()
            exit = waitForExitNotification(time_on)
            if exit:
                return
            strip.set(i, 0x00, update=False)
            strip.set(num_pixels+1-i, 0x00, update=False)
            strip.show()
            exit = waitForExitNotification(1)
            if exit:
                return

def Wheel(wheelPos):
    """# For  Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r

    returns: list (int) of color values - rgb
    """
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


def v_shape(time_on = 50):
    print("v_shape")
    j = 0
    while True:
        for i in range(0, num_pixels):
            val = Wheel((int(i * 256 / num_pixels/9)+j ) & 255 )
            colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in val]))
            color = random.randint(0, 16777214)
            strip.set(i+1, colInt, update=False)
            #strip.set(num_pixels-i, colInt, update=False)
        strip.show()
        j +=6
        exit = waitForExitNotification(time_on)
        if exit:
            return

# ------------ fire -------------------- (55, 120, 15)-orig. (70,140,20)-custom
def fire(cooling = 70, sparkling = 140, speedDelay = 100):
    #w, h = 3, num_pixels

    print("fire")
    heat = [0x00 for x in range(num_pixels, 0, -1)]
    cooldown = 0
    while True:
    #for l in range(30):
        # Step 1: cool down every cell a little
        for i in range(num_pixels):
            cooldown = random.randint(0, int((cooling * 10) / num_pixels) +2)

            if (cooldown > heat[i]):
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown
            # gc.collect()
        # Step 2: Heat from each cell drifts
        #for k in range(int(num_pixels/2)-1, 1, -1):
        for k in range(num_pixels-1, 2, -1):
            #print("heat: k= {}".format(k))
            heat[k] = (heat[k-1] +  heat[k-2] + heat[k-2]) / 3

        # Step 3 randomly ignite new "sparks" near the bottom
        if(random.randint(0,255) < sparkling):
            y = random.randint(0,int(num_pixels/4))
            #list index out of range!!
            heat[y] = heat[y] + random.randint(160, 255)
        # gc.collect()
        # Step 4 convert heat to num_pixels colours
        for j in range(num_pixels):
            setPixelHeatColor(j, heat[j])
            #setPixelHeatColor(int(num_pixels/2)-j, heat[j])
            #setPixelHeatColor(int(num_pixels/2)+j, heat[j])
        strip.show()
        #check if thread got notificatio to exit and exit if it is so
        if waitForExitNotification(speedDelay):
            # off()
            return
        #sleep_ms(speedDelay)
        # gc.collect()

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
        val = [heatramp, 0,  0]
    RGB = []
    RGB = [int(x) for x in val]
    colInt = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
    strip.set(pixel, colInt, update=False)
    # gc.collect()
# --------------fire - end -----------------------


#-------------------------wave-----------------------------------
def wave():
    print("wave")
    MAX_INT_VALUE = 65536
    frame = 0
    hue    = 180

    #for l in range(20):
    while True:
        #strip.clear()
        for i in range(num_pixels):
            deg = float(frame + ((MAX_INT_VALUE / num_pixels ) * i ))/ (float(MAX_INT_VALUE))*360
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
            # gc.collect()
        strip.show()
        frame += 1000
        # gc.collect()
        if waitForExitNotification(1000):
            # off()
            return
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
            return num_pixels + step
        if(step > num_pixels - 1):
            return step - num_pixels
        return step

    #for r in range(20):
    while True:
        if currBg is nextBg:
            nextBg = random.randint(0, 256)
        elif nextBg > currBg:
            currBg+= 1
        else:
            currBg-=1

        for i in range(num_pixels):
            strip.setHSB(i, currBg, 255, 50, update=False)
        # gc.collect()
        if step is -1:
            center = random.randint(0, num_pixels)
            color = random.randint(0, 256)
            step = 0

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
        if waitForExitNotification(100):
            #off()
            return
#------------------end of ripple--------------------------

#-------------------sparkle----------------------------------
def sparkle():
    print("sparkle")

    #for l in range(20):
    while True:
        for i in range(1, num_pixels+1):
            val = Wheel(random.randint(0,255))
            RGB = []
            RGB = [int(x) for x in val]
            color = int("0x"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB]))
            # gc.collect()
            if random.randint(0,10)<4:
                strip.set(i, color, update=False)
            else:
                strip.set(i, 0x00, update = False)
        strip.show()
        if waitForExitNotification(200):
            # off()
            return
        strip.clear
#---------------------end of sparkle-------------------------

def running_dot(color = 0x00FFFF, time_on=50):
    while True:
        for i in range(1, num_pixels+1):
            pos1 = (i-1) % num_pixels +1
            pos2 = (i-2) % num_pixels +1
            pos3 = (i-3) % num_pixels +1

            if pos1  == 0:
                pos1 = num_pixels
            if pos2 == 0:
                pos2 = num_pixels
            if pos3 == 0:
                pos3 = num_pixels

            strip.set(i, color, update=False)
            strip.set(pos1, color, white=100, update=False)
            strip.set(pos2, color, white=150, update=False)
            strip.set(pos3, color, white=200, update=False)
            strip.show()
            utime.sleep_ms(time_on)
            strip.set(i, 0x00, update=False)
            strip.set(pos1, 0x00, update=False)
            strip.set(pos2, 0x00, update=False)
            strip.set(pos3, 0x00, update=False)
            strip.show()
            utime.sleep_ms(1)

def leds_off():
    """ turns off all LEDs of strip
    """
    strip.set(0, 0x00, num=num_pixels)



# saves all animations in a dictionary
animation_dict = {"blink":blink, "running_dot":running_dot, "crossing_dots":crossing_dots,
"v_shape":v_shape, "fire": fire, "wave":wave, "ripple":ripple, "sparkle":sparkle, "off": leds_off}

anim_iterator = iter(animation_dict.items())
def next():
    """ iterates through anim_iterator (global value) and starts next Animation
    On exception (StopIteration) creates new Iterator object in anim_iterator

    """
    global anim_iterator
    try:
        running_function = anim_iterator.__next__()[1]
        print(running_function)
        running_function()
    except StopIteration:
        anim_iterator = iter(animation_dict.items())
        next()

def start(animation_name):
    """ starts new animation saved in animation_dict by key argument given by animation_name

    animation_name: (String) name of animation keyword to start
    """
    animation_dict[animation_name]()
