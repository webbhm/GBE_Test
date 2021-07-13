'''
Run through the rainbow spectrum

Author: Howard Webb
Date: 3/8/2021

'''

from time import sleep
from PWM_Util import map

OFF = 100

class Rainbow(object):
    def __init__(self, light):
        self._light = light
        self.run()
        
    def run(self):
        # purple to blue
        g = 0
        for r, b in zip(range(1280, 0, -10), range(0, 1280, 10)):
            self.set_pwm(r, g, b)
            #sleep(0.25)                                       
        # blue to green
        r = 0
        for b, g in zip(range(1280, 0, -10), range(0, 1280, 10)):
            self.set_pwm(r, g, b)
            #sleep(0.25)                                       
        
        # green to red
        b = 0
        for g, r in zip(range(1280, 0, -10), range(0, 1280, 10)):
            self.set_pwm(r, g, b)
            #sleep(0.25)                           
        
        self._light.off()

    def set_pwm(self, r, g, b):
        # input is RGB value
        # map to 1000-0
        r = round(map(r, 1280,0, 1000, 0)/1000, 4)
        g = round(map(g, 1280,0, 1000, 0)/1000, 4)
        b = round(map(b, 1280,0, 1000, 0)/1000, 4)

        #print(r, g, b)
        self._light.set_pwm(r, g, b, 1)
        sleep(0.05)            
        
        
def test():
    from GrowLight import GrowLight
    gl = GrowLight()
    r = Rainbow(gl)
    
if __name__ == "__main__":
    test()
        