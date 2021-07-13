'''
Utility function for the light

'''

def map(value, R1_Low, R1_High, R2_Low, R2_High):
    # map one range of numbers to another range
    # Used for RGB to PWM conversion (0-255, 100-0)
    # Used for Specturm to RGB (0-1, 0-255)
    y = (value-R1_Low)/(R1_High-R1_Low)*(R2_High-R2_Low) + R2_Low
    return y