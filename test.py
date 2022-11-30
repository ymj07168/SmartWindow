import RPi.GPIO as gpio
import DCmotor
from LCD import *
# import raindrop
import time

from time import sleep
from gpiozero import InputDevice

# Define some device parameters
I2C_ADDR = 0x27     # I2C device address, if any error, change this address to 0x3f
LCD_WIDTH = 16      # Maximum characters per line

# Define some device constants
LCD_CHR = 1     # Mode - Sending data
LCD_CMD = 0     # Mode - Sending command

LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0   # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94   # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4   # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08  # On

ENABLE = 0b00000100     # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
# bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1)

no_rain = InputDevice(26)

is_open = 0

while True:
    lcd_init()

    if not no_rain.is_active:
        print("It's raining - get the washing in!")
        lcd_string("raining", LCD_LINE_1)
        DCmotor.forward(3)
    else:
        print("NO rain")
        lcd_string("no rain", LCD_LINE_2)
        DCmotor.reverse(3)

        is_open = 0
    sleep(1)