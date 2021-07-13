import time

from pyb import ADC, Pin
# Import the ADS1x15 module (analog to digital converter).
in_voltage = 5
adc_range = 4095

class EC(object):
    
   def __init__(self, temperature=25, logger=None):
      # SET UP adc and set temp compensation
      self._adc = ADC(Pin.board.X5)
      self._temp = temperature
      self._tempCoeff = self.tempCoeff()

   def get(self):

        volts = ((self._adc.read()/ adc_range) * in_voltage)
        coef_volt = volts/self._tempCoeff
        if coef_volt < 150: # No solution
            return 0
        elif coef_volt > 3300:
            return 0
        
        if coef_volt <= 448:
            ec_cur = 6.84 * coef_volt - 64.32
        elif coef_volt <=1457:
            ec_cur = 6.98 * coef_volt - 127
        else:
            ec_cur = 5.3 * coef_volt + 2278
        ec_cur = ec_cur/1000  # convert us/cm to ms/cm
        return ec_cur
        
   def tempCoeff(self):
       return 1.0 + 0.0185 * (self._temp - 25.0)

def calibrate():
    # collect data to a file for calibrating results
    print("EC Calibration")
    ec = EC()

    turbidity = Turbidity()

    t_header = 'ppm'

    # files to use
    t_dir = '/home/pi/python/PyRock/data/ec.csv'

    # create files
    t_file = open(t_dir,'w')

    # write headers
    t_file.write(t_header)

    while True:
        value = ec.get()
        print("EC", round(value, 2))
        t_file.write(round(value, 2))
        time.sleep(2)

    t_file.close()
    
def run():
    # Test for continuous reading
    print("EC")
    ec = EC()
    while True:
        print("EC", ec.get())
        time.sleep(2)
    
def test():
    # Validation test
    print("Test EC")
    try:
        ec = EC()
        print("EC", ec.get())
    except Exception as e:
        print("ERROR: Failure creating EC and getting reading")
