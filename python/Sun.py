'''
Light Helper for producing sunrises and sunsets
Sunset (and sunrise) is defined as five phases
  Astronomical (1 & 2) - affects viewing of stars
  Nautical - accounts for reflection on water
  Civil (1 & 2) - what we are familiar with in most land locations, when the sun appears

May not be accurate, but is fun to play with

Pass a light object to the function for it to run

Author: Howard Webb
Date: 2/8/2021
'''
# source for sunset specifications
import Sunset as s
from time import sleep
from PWM_Util import map

OFF = 1000

def sunrise(light):
    print("Sunrise")
    start = 0
    step_size = 1
    steps = 200
    astronomical_twilight_1(light, start, steps, step_size)
    astronomical_twilight_2(light, start, steps, step_size)
    nautical_twilight(light, start, steps, step_size)
    civil_twilight_1(light, start, steps, step_size)    
    civil_twilight_2(light, start, steps, step_size)
    
def sunset(light):
    print("Sunset")
    start = 200
    step_size = -10
    steps = 10
    civil_twilight_2(light, start, steps, step_size)
    civil_twilight_1(light, start, steps, step_size)
    nautical_twilight(light, start, steps, step_size)
    astronomical_twilight_2(light, start, steps, step_size)    
    astronomical_twilight_1(light, start, steps, step_size)
    # end with lights off
    light.set_pwm(1, 1, 1, 1)    
    # astronomical twilight
    
def astronomical_twilight_1(light, start, steps, step_size):    
    print("Astronomical Twilight 1")
    for step in range(start, steps, step_size):
        r, g, b = s.astronomical_twilight1(step, steps)
        r = round(map(r, 0, 256, OFF, 0)/1000, 4)
        g = round(map(g, 0, 256, OFF, 0)/1000, 4)
        b = round(map(b, 0, 256, OFF, 0)/1000, 4)
        light.set_pwm(r, g, b)
        sleep(0.05)

def astronomical_twilight_2(light, start, steps, step_size):         
    print("Astronomical Twilight 2")
    for step in range(start, steps, step_size):
        r, g, b = s.astronomical_twilight2(step, steps)
        r = round(map(r, 0, 256, OFF, 0)/1000, 4)
        g = round(map(g, 0, 256, OFF, 0)/1000, 4)
        b = round(map(b, 0, 256, OFF, 0)/1000, 4)
        light.set_pwm(r, g, b)
        sleep(0.25)

def nautical_twilight(light, start, steps, step_size): 
    # nautical twilight
    print("Nautical Twilight")
    for step in range(start, steps, step_size):
        r, g, b = s.nautical_twilight(step, steps)
        r = round(map(r, 0, 256, OFF, 0)/1000, 4)
        g = round(map(g, 0, 256, OFF, 0)/1000, 4)
        b = round(map(b, 0, 256, OFF, 0)/1000, 4)
        light.set_pwm(r, g, b)
        sleep(0.25)
        
def civil_twilight_1(light, start, steps, step_size): 
    print("Civil Twilight 1")
    for step in range(start, steps, step_size):
        r, g, b = s.civil_twilight1(step, steps)
        r = round(map(r, 0, 256, OFF, 0)/1000, 4)
        g = round(map(g, 0, 256, OFF, 0)/1000, 4)
        b = round(map(b, 0, 256, OFF, 0)/1000, 4)
        light.set_pwm(r, g, b, 1)
        sleep(0.25)

def civil_twilight_2(light, start, steps, step_size): 
    print("Civil Twilight 2")
    for step in range(start, steps, step_size):
        r, g, b = s.civil_twilight2(step, steps)
        r = round(map(r, 0, 256, OFF, 0)/1000, 4)
        g = round(map(g, 0, 256, OFF, 0)/1000, 4)
        b = round(map(b, 0, 256, OFF, 0)/1000, 4)
        light.set_pwm(r, g, b, 1)
        sleep(0.25)
        
def test():
    from GrowLight import GrowLight
    gl = GrowLight()
    #sunrise(gl)
    sunset(gl)
    print("Done")
        
if __name__ == "__main__":
    test()        
    
