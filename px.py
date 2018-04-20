import time, machine, math, random

class Pixels:
    def __init__(self, pin = 14, numLed = 60):
        self.pin = pin
        self.led = numLed
        self.strip = machine.Neopixel(machine.Pin(self.pin), self.led, 0)
        self.fact_cache = {}
        self.threecolors = {"#00173d", "#f75002", "#01f2f7"}

        #for fire function
        self.w, self.h = 3, int(self.led/2)
        #self.oldColor = [[ 0x00 for x in range (self.w)] for y in range(self.h)]

    # For Rainbow Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    def Wheel(self, wheelPos):
        wheelPos = 255 -  wheelPos
        if( wheelPos < 85) :
            return (255 -  wheelPos * 3, 0,  wheelPos * 3)
        elif( wheelPos < 170):
            wheelPos -= 85
            return (0,  wheelPos * 3, 255 -  wheelPos * 3)
        else:
            wheelPos -= 170
            return ( wheelPos * 3, 255 -  wheelPos * 3, 0)

    # Slightly different, this makes the rainbow equally distributed throughout
    def rainbowCycle(self, wait=0.003):
        while True:
            for j in range (256*5): #5 cycles of all colors on wheel
                for i in range (0, 60):
                    self.strip.set(i, self.Wheel((int(i * 256 / self.led)+j ) & 255))
                self.strip.show()
                time.sleep(wait)

    # --------colorGradient + dependencies -------------
    def color_dict(self, gradient):
        ''' Takes in a list of RGB sub-lists and returns dictionary of
            colors in RGB and hex form for use in a graphing function
            defined later on '''
        return {"hex":[self.RGB_to_hex(RGB) for RGB in gradient],
            "r":[RGB[0] for RGB in gradient],
            "g":[RGB[1] for RGB in gradient],
            "b":[RGB[2] for RGB in gradient]}

    def fact(self, n):
        ''' Memoized factorial function '''
        try:
            return self.fact_cache[n]
        except(KeyError):
            if n == 1 or n == 0:
                result = 1
            else:
                result = n*self.fact(n-1)
            self.fact_cache[n] = result
            return result

    def bernstein(self, t,n,i):
        ''' Bernstein coefficient '''
        binom = self.fact(n)/float(self.fact(i)*self.fact(n - i))
        return binom*((1-t)**(n-i))*(t**i)


    def bezier_gradient(self, colors=None, n_out=None):
        ''' Returns a "bezier gradient" dictionary
            using a given list of colors as control
            points. Dictionary also contains control
            colors/points. '''
        if colors is None:
            colors=self.threecolors
        if n_out is None:
            n_out = self.led

        # RGB vectors for each color, use as control points
        RGB_list = [self.hex_to_RGB(color) for color in colors]
        n = len(RGB_list) - 1

        def bezier_interp( t):
            ''' Define an interpolation function
                for this specific curve'''
            # List of all summands
            summands = [
                list(map(lambda x: int(self.bernstein(t,n,i)*x), c))
                for i, c in enumerate(RGB_list)
                ]
            # Output color
            out = [0,0,0]
            # Add components of each summand together
            for vector in summands:
                for c in range(3):
                    out[c] += vector[c]

            return out

        gradient = [
            bezier_interp(float(t)/(n_out-1))
            for t in range(n_out)
        ]
        for n in range(len(gradient)):
            self.strip.set(n, self.RGB_to_touple(gradient[n]))
            self.strip.set((self.led-1-n), self.RGB_to_touple(gradient[n]))

        self.strip.show()
        # Return all points requested for gradient
        return {
            "gradient": self.color_dict(gradient),
            "control": self.color_dict(RGB_list)
        }
    # ---------- end of bezier_gradient-------------

    # ------------ fire --------------------
    def fire(self):
        #w, h = 3, self.led
        heat = [0x00 for x in range(int(self.led/2), 0, -1)]
        print("got heat array")

        cooling, sparkling, speedDelay = 180, 120, 0.015
        #cooling = 55, sparkling = 120, speedDelay = 0.015

        cooldown = 0

        # Step 1: cool down every cell a little
        for i in range(int(self.led/2)):
            cooldown = random.randint(0, int((cooling * 10) / int(self.led)) +2)

            if (cooldown > heat[i]):
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown
        print("got first loop array")


        # Step 2: Heat from each cell drifts
        for k in range(int(self.led/2)-1, 1, -1):
            heat[k] = (heat[k-1] +  heat[k-2] + heat[k-2]) / 3
        print("got 2nd loop array")


        # Step 3 randomly ignite new "sparks" near the bottom
        if(random.randint(0,255) < sparkling):
            y = random.randint(0,7)
            heat[y] = heat[y] + random.randint(160, 255)

        # Step 4 convert heat to led colours
        for j in range(int(self.led/2)):
            #self.setPixelHeatColor(j, heat[j])
            self.setPixelHeatColor(int(self.led/2)-j, heat[j])
            self.setPixelHeatColor(int(self.led/2)+j, heat[j])
        self.strip.show()
        time.sleep(speedDelay)

    def setPixelHeatColor(self, pixel, temp):
        # scale heat down from 0-255 to 0-191
        ht = round((temp/255.0) * 191)

        #calc ramp up from
        heatramp = ht & 0x3f #0..63
        heatramp <<=2  #scale up to 0...252

        #figure out which third of the spectrum we're in
        if (ht > 0x80):             #hottest
            self.strip.set(pixel,  (255, 255, heatramp))
        elif ( ht > 0x40):          #middle
            self.strip.set(pixel,  (255, heatramp, 0))
        else:                       #coolest
            self.strip.set(pixel,  (heatramp, 0, 0))
    # --------------fire - end -----------------------


    # ------------converting values
    def hex_to_RGB(self, hex):
        ''' "#FFFFFF" -> [255,255,255] '''
        # Pass 16 to the integer function for change of base
        return [int(hex[i:i+2], 16) for i in range(1,6,2)]

    def RGB_to_touple(self, RGB):
        '''[255,255,255] -> (255,255,255)'''
        return (RGB[0], RGB[1],RGB[2])


    def RGB_to_hex(self, RGB):
        ''' [255,255,255] -> "#FFFFFF" '''
        # Components need to be integers for hex to make sense
        RGB = [int(x) for x in RGB]
        return "#"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB])


    #turn off all pixels
    def off(self):
        for i in range (self.led):
            self.strip.set(i, (0,0,0))
        self.strip.show()
