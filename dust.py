import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import RPi.GPIO as GPIO

# from collections import deque

GPIO.setmode(GPIO.BCM)
LED_Pin = 17
GPIO.setup(LED_Pin, GPIO.OUT)
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
# Create single-ended input on channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

while True:
    GPIO.output(LED_Pin, False)
    # time.sleep(0.000280)
    dustVal=chan0.value
    # time.sleep(0.000040)
    GPIO.output(LED_Pin,True)
    # time.sleep(0.009680)
    time.sleep(1)

    print(dustVal)
    if (dustVal>36.455):
        print(((dustVal/1024)-0.0356)*120000*0.035)