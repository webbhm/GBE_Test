'''
Class for the physical grow light
Manages PWM via the GPIO pins
Experiment settings are managed through the Light_Setting import
Author: Howard Webb
Date: 12/20/2020
3/16/2021 modified to work with pi-blaster
  no longer need to have GrowLight running 7/24 as service since pi-blaster is a service
  this really just becomes a utility wrapper of pi-blaster
'''

#import RPi.GPIO as GPIO
from time import sleep
from PWM_Util import map
import os
from exp import exp

# Assignments of Raspberry Pi pins to color chanels
# BCM numbering
pin_R = 12 # Red
pin_B = 20 # Blue
pin_G = 16 # Green
pin_W = 21  # White

state = False


# Values are dimming.  0 = Full power, 100 = off, going from max power up to 100
OFF = 100

# Range of the visible spectrum - used for one of the tests
SPEC_LOW = 380
SPEC_HIGH = 750


class GrowLight(object):
    ''' Representation of the grow light panel
    '''

    def __init__(self):
        
        # maximum safe settings
        self.R_MAX = 0
        self.G_MAX = 50
        self.B_MAX = 5
        self.W_MAX = 0        
        
        self.set_lights(OFF, OFF, OFF, OFF)
            
    def set_lights(self, r, g, b, w=OFF):
        # for legacy that works with 0-100
        # change the duty cycle of the RGBW light
        #print("Set", r, g, b, w)
        # don't accept setting with numeric value lower than MAX
        if r < self.R_MAX:
            r = self.R_MAX
        if g < self.G_MAX:
            g = self.G_MAX
        if b < self.B_MAX:
            b = self.B_MAX
        if w < self.W_MAX:
            w = self.W_MAX
        #print("Safe Set", r, g, b, w)
        # PWM is normally 0-100, but pi-blaster uses 0-1
        r = round(r/100, 3)
        g = round(g/100, 3)
        b = round(b/100, 3)
        w = round(w/100, 3)
        self.set_pwm(r, g, b, w)
        cmd = 'echo "12={} 16={} 20={} 21={}" > /dev/pi-blaster'.format(r, g, b, w)
        print(cmd)
        os.system(cmd)        
        
    def set_pwm(self, r, g, b, w=1):
        if (r > 1) or (g > 1) or (b > 1) or (w > 1):
            print("Invalid value", r, g, b, w)
            return
        cmd = 'echo "12={} 16={} 20={} 21={}" > /dev/pi-blaster'.format(r, g, b, w)
        print(cmd)
        os.system(cmd)        
        
    def end(self):
        # turn off all the leds
        #self.set_lights(OFF, OFF, OFF, OFF)
        #self.pwm_R.stop()
        #self.pwm_G.stop()
        #self.pwm_B.stop()
        #self.pwm_W.stop()
        #GPIO.cleanup()
        pass
        
    def on(self):
        # call on action from experiment settings
        self.switch_light("on")
        
    def off(self):
        # call off action from experiment settings
        self.switch_light("off")
        
    def camera(self):
        # setting for camera
        self.set_pwm(1, 1, 1, 0)
        
        
    def switch_light(self, action):
        # get exp info and perform
        setting = "setting"
        function = "function"
        lights = exp["phases"][exp["current_phase"]]["lights"][action]
        if setting in lights:
            # have a light setting
            ls = lights[setting]
            R = ls["R"]
            G = ls["G"]
            B = ls["B"]
            W = ls["W"]
            self.set_lights(R, G, B, W)
        elif function in lights:
            #have dynamic function
            mod = lights[function]["module"]
            print("Module:", mod)
            module = __import__(mod)
            cls = lights[function]["class"]
            print("Class:", cls)
            class_ = getattr(module, cls)
            # build object and pass in Grow_Light
            instance = class_(self._light)            
    
  
def test():
    gl = GrowLight()
    print("On")
    gl.on()
    sleep(10)
    print("Red")
    gl.set_lights(50, OFF, OFF)
    sleep(10)
    print("Green")
    gl.set_lights(OFF, 50, OFF)
    sleep(10)
    print("Blue")
    gl.set_lights(OFF, OFF, 50)
    sleep(10)
    print("White")
    gl.set_lights(OFF, OFF, OFF, 50)
    sleep(10)
    #print("Red")
    #gl.set_lights(50, OFF, OFF)
    #sleep(100 )    
    print("Off")
    
    gl.off()
    sleep(2)

if __name__ == "__main__":
        test()
