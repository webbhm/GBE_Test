"""
schemecolor.com/sunset-tones.php

Value settings for producing the sunset and sunrise

Author: Howard Webb
Date: 2/8/2021
"""

# Maastricht Blue
mb_r = 8
mb_g = 24
mb_b = 58

# Space Cadet
sc_r = 21
sc_g = 40
sc_b = 82

# English Violet
ev_r = 75
ev_g = 61
ev_b = 96

# Sunset Orange
so_r = 253
so_g = 94
so_b = 83

# Sandy Brown
sb_r = 252
sb_g = 156
sb_b = 84

# Shandy Yellow
sy_r = 255
sy_g = 227
sy_b = 115



SUNRISE = True

def transition(x, steps, r1, r2, g1, g2, b1, b2):
    #print(x, f, r1, r2, g1, g2, b1, b2)
    r = calc(x, steps, SUNRISE, r1, r2)
    g = calc(x, steps, SUNRISE, g1, g2)
    b = calc(x, steps, SUNRISE, b1, b2)
    return r, g, b

def calc(x, steps, SUNRISE, c1, c2):
    # calculate pwm value of color based on rgb values
    w = c1 + x*abs(c2 - c1)/steps
    # convert rgb to pwm
    c = round(map(w, 0, 256, 0, 100), 1)
    #print(x, w, c, c1, c2)
    return c   
def map(value, R1_Low, R1_High, R2_Low, R2_High):
    # map one range of numbers to another range
    y = (value-R1_Low)/(R1_High-R1_Low)*(R2_High-R2_Low) + R2_Low
    return y

def astronomical_twilight1(step, steps=20):
    # Maastrich Blue to Space Cadet - Astronomical Twilight    
    return transition(step, steps, mb_r, sc_r, mb_g, sc_g, mb_b, sc_b)
    
def astronomical_twilight2(step, steps=20):
    # Space Cadet to English Violet - Nautical Twilight    
    return transition(step, steps, sc_r, ev_r, sc_g, ev_g, sc_b, ev_b)
    
def nautical_twilight(step, steps=20):
    # English Violet - Sunset Orange - Nautical Twilight    
    return transition(step, steps, ev_r, so_r, ev_g, so_g, ev_b, so_b)
    
def civil_twilight1(step, steps=20):
    # Sunset Orange to Snady Brown - Civil Twilight1    
    return transition(step, steps, so_r, sb_r, so_g, sb_g, so_b, sb_b)
    
def civil_twilight2(step, steps=20):
    # Snady Brown to Shandy Yellow - Civil Twilight2
    return transition(step, steps, sb_r, sy_r, sb_g, sy_g, sb_b, sy_b)
    


def test():
    MAX = 20
    print("\nAstronomical Twilight 1")
    for x in range(0, MAX):
       r, g, b = astronomical_twilight1(x, MAX)
       print(x, r, g, b)

    print('\nAstronomical Twilight 2')
    for x in range(0, MAX):
       r, g, b = astronomical_twilight2(x, MAX)
       print(x, r, g, b)
       
    print('\nNautical Twilight')
    for x in range(0, MAX):
       r, g, b = nautical_twilight(x, MAX)
       print(x, r, g, b)
       
    print('\nCivil Twilight 1')
    for x in range(0, MAX):
       r, g, b = civil_twilight1(x, MAX)
       print(x, r, g, b)

    print('\nCivil Twilight 2')
    for x in range(0, MAX):
       r, g, b = civil_twilight2(x, MAX)
       print(x, r, g, b)
        
if __name__ == "__main__":
    test()        
