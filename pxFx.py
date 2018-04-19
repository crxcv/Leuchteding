import neopixel, machine, random, time

class Pixels:
    def __init__(self):
        self.pin = 14
        self.led = 60
        self.strip = neopixel.NeoPixel(machine.Pin(self.pin), self.led)
        #for fire function
        self.w, self.h = 3, int(self.strip.n/2)
        self.oldColor = [[ 0x00 for x in range (self.w)] for y in range(self.h)]
        #print("got oldColor array")

    def fire(self):
        #w, h = 3, self.strip.n
        heat = [0x00 for x in range(int(self.strip.n), 0, -1)]
        print("got heat array")

        cooling, sparkling, speedDelay = 180, 120, 0.015
        #cooling = 55, sparkling = 120, speedDelay = 0.015

        cooldown = 0

        # Step 1: cool down every cell a little
        for i in range(int(self.strip.n)):
            cooldown = random.randint(0, int((cooling * 10) / int(self.strip.n)) +2)

            if (cooldown > heat[i]):
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown
        print("got first loop array")


        # Step 2: Heat from each cell drifts
        for k in range(int(self.strip.n/2)-1, 1, -1):
            heat[k] = (heat[k-1] +  heat[k-2] + heat[k-2]) / 3
        print("got 2nd loop array")


        # Step 3 randomly ignite new "sparks" near the bottom
        if(random.randint(0,255) < sparkling):
            y = random.randint(0,7)
            heat[y] = heat[y] + random.randint(160, 255)

        # Step 4 convert heat to led colours
        for j in range(self.strip.n/2):
            self.setPixelHeatColor(j, heat[j])
            #self.setPixelHeatColor(int(self.strip.n/2)-j, heat[j])
        self.strip.write()
        time.sleep(speedDelay)

    def setPixelHeatColor(self, pixel, temp):
        # scale heat down from 0-255 to 0-191
        ht = round((temp/255.0) * 191)

        #calc ramp up from
        heatramp = ht & 0x3f #0..63
        heatramp <<=2  #scale up to 0...252

        #figure out which third of the spectrum we're in
        if (ht > 0x80):             #hottest
            self.strip[pixel] = (255, 255, heatramp)
        elif ( ht > 0x40):          #middle
            self.strip[pixel] = (255, heatramp, 0)
        else:                       #coolest
            self.strip[pixel] = (heatramp, 0, 0)
    ## end of fire

    def fadeToBlack(self, ledNo, fadeValue):
        r = (self.oldColor[ledNo][0] | 0x00ff0000) >> 16
        g = (self.oldColor[ledNo][1] & 0x0000ff00) >> 8
        b  = (self.oldColor[ledNo][2] & 0x000000ff)


        r= 0 if (r<=10) else int(r-(r*fadeValue/256))
        g= 0 if (g<=10) else int(g-(g*fadeValue/256))
        b= 0 if (b<=10) else int(b-(b*fadeValue/256))
        self.oldColor[ledNo] = [r, g, b]
        self.strip[ledNo] = (r,g,b)
        self.strip.write()

    def setAll(self, red, green, blue):
        for i in range (self.strip.n):
            self.strip[i] = (red, green, blue)

    #0xff,0xff,0xff,7, 255, True, 0.00030
    def meteorRain(self, red=0xff, green=0xff, blue=0xff, meteorSize=7, meteorTrailDecay=255, meteorRandomDecay=True, speedDelay=0.0003):
        self.setAll(0,0,0);

        for i in range (self.strip.n):
            for j in range (self.strip.n):
                if (not meteorRandomDecay) or random.randint(0,10) > 5 :
                    self.fadeToBlack(j, meteorTrailDecay)

            for j in range (meteorSize):
                if i-j < self.strip.n and i-j >= 0:
                    self.strip[i-j] = (red, green, blue)
            self.strip.write()
            time.sleep(speedDelay)
