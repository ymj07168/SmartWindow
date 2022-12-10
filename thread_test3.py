from threading import Thread
import RPi.GPIO as GPIO
import LCD
from gpiozero import InputDevice
import time

# 먼지센서 모듈
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0
LCD.lcd_init()


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

def lcd(id, res):
    if res == "rain":
        print("LCD print : rain")
        LCD.lcd_string("Raining", LCD_LINE_1)
        # LCD.lcd_string("", LCD_LINE_2)
    else:
        print("LCD print : no rain")
        LCD.lcd_string("No Rain", LCD_LINE_1)
        # LCD.lcd_string("", LCD_LINE_2)


def dust(id):
    GPIO.output(LED_Pin, False)
    dustVal=chan0.value
    GPIO.output(LED_Pin,True)

    if (dustVal>36.455):
        dust_value = ((dustVal/1024)-0.0356)*120000*0.035
        LCD.lcd_string(str(dust_value), LCD_LINE_2)



if __name__ == "__main__":
    no_rain = InputDevice(26)
    result = ""

    while True:
        if not no_rain.is_active:
            result = "rain"
        else:
            result = "no_rain"

        lcd(1, result)
        dust(2)
        time.sleep(1)
        # lcd = Thread(target=lcd, args=(1, result,))