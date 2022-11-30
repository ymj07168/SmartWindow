import DCmotor
from time import sleep
from gpiozero import InputDevice
import RPi.GPIO as gpio
import LCD

no_rain = InputDevice(26)
while True:
    LCD.lcd_init()

    if not no_rain.is_active:
        print("It's raining - get the washing in!")
        print(no_rain.is_active)
        DCmotor.forward(3)
        LCD.lcd_string("RAIN    ", LCD.LCD_LINE_1)
    else:
        print("NO rain")
        print(no_rain.is_active)
        DCmotor.reverse(3)
        LCD.lcd_string("NO RAIN ", LCD.LCD_LINE_2)
    sleep(1)

