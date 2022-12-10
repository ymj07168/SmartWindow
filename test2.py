import RPi.GPIO as gpio
from threading import Thread
import DCmotor
import dust
import LCD
from gpiozero import InputDevice
import time

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
# LCD_LINE_2 = 0xC0
# LCD.lcd_init()

gpio.setmode(gpio.BCM)
LED_Pin = 17
gpio.setup(LED_Pin, gpio.OUT)
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
# Create single-ended input on channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

def motor(no_rain):
    if not no_rain:
        print("forward")
        DCmotor.forward(3)
    else:
        print("reverse")
        DCmotor.reverse(3)

def lcd(id, res):
    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0
    LCD.lcd_init()

    if res == "rain":
        print("LCD print : rain")
        LCD.lcd_string("Raining", LCD_LINE_1)
    else:
        print("LCD print : no rain")
        LCD.lcd_string("No Rain", LCD_LINE_1)

def dust(id):
    gpio.output(LED_Pin, False)
    time.sleep(0.000280)
    dustVal = chan0.value
    time.sleep(0.000040)
    gpio.output(LED_Pin, True)
    time.sleep(0.009680)
    time.sleep(1)

    dust_value = ((dustVal / 1024) - 0.0356) * 120000 * 0.035
    print("DUST print : " + dust_value)
    LCD.lcd_string(str(dust_value), LCD_LINE_2)


if __name__ == "__main__":
    no_rain = InputDevice(26)
    result = ""

    while True:
        if not no_rain.is_active:
            result = "no_rain"
        else:
            result = "rain"

        lcd = Thread(target=lcd, args=(1, result,))
        # motor = Thread(target=motor, args=(no_rain.is_active))
        # dust = Thread(target=dust, args=(2,))

        lcd.start()
        lcd.join()


