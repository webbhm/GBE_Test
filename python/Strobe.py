'''
Something to play around with the lights

Author: Howard Webb
Date: 2/8/2021
'''

OFF = 100
# helper class to strobe the lights
class Strobe(object):
    
    def __init__(self, light_setting):
        self.func = light_set
        self.run()
        
    def run(self):
        for x in range(0 10):
            for y in range(0, 3):
                if y == 0:
                    self.func(R, OFF, OFF, OFF)
                if y == 1:
                    self.func(OFF, G, OFF, OFF)
                if y == 2:
                    self.func(OFF, OFF, B, OFF)