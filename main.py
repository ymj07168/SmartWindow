import DCmotor
import LCD

import raindrop
import time

from time import sleep
from gpiozero import InputDevice

LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0


no_rain = InputDevice(6)

is_open = 0

# if __name__ == '__main__':
#     while True:
#     # Send some test
#         lcd_string("HI    ", LCD_LINE_1)
#         lcd_string("HYOWON", LCD_LINE_2)
#
#         time.sleep(3)

while True:
    LCD.lcd_init()

    if not no_rain.is_active:
        print("It's raining - get the washing in!")
        LCD.lcd_string("raining", LCD_LINE_1)
        DCmotor.forward(3)
    else:
        print("NO rain")
        LCD.lcd_string("no rain", LCD_LINE_2)
        DCmotor.reverse(3)

        is_open = 0
    sleep(1)