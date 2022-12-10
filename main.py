import RPi.GPIO as gpio
import DCmotor
import LCD

from time import sleep
from gpiozero import InputDevice

LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0



is_open = 0

while True:
    LCD.lcd_init()
    gpio.setmode(gpio.BCM)
    no_rain = InputDevice(26)

    if not no_rain.is_active:
        print("It's raining - get the washing in!")
        LCD.lcd_string("raining", LCD_LINE_1)
        # DCmotor.forward(1)
    else:
        print("NO rain")
        LCD.lcd_string("no rain", LCD_LINE_2)
        # DCmotor.reverse(1)

        is_open = 0
    sleep(1)