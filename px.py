import neopixel, time, machine, math, random

class Pixels:
    def __init__(self):
        self.pin = 14
        self.led = 60
        self.strip = neopixel.NeoPixel(machine.Pin(self.pin), self.led)
        self.fact_cache = {}
        self.threecolors = {"#00173d", "#f75002", "#01f2f7"}

    # Input a value 0 to 255 to get a color value.
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
        for j in range (256*5): #5 cycles of all colors on wheel
            for i in range (0, 60):
                self.strip[i] = self.Wheel((int(i * 256 / self.strip.n)+j ) & 255)
            self.strip.write()
            time.sleep(wait)

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
            n_out = self.strip.n

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
            self.strip[n] = self.RGB_to_touple(gradient[n])
            self.strip[(self.strip.n-1-n)] = self.RGB_to_touple(gradient[n])

        self.strip.write()
        # Return all points requested for gradient
        return {
            "gradient": self.color_dict(gradient),
            "control": self.color_dict(RGB_list)
        }


    #turn off all pixels
    def off(self):
        for i in range (self.strip.n):
            self.strip[i] = (0,0,0)
        self.strip.write()
