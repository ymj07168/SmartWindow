# raindrop sensor DO connected to GPIO18
# HIGH = no rain, LOW = rain detected
# Buzzer on GPIO13
from time import sleep
from gpiozero import InputDevice
import DCmotor

no_rain = InputDevice(26)

while True:


    if not no_rain.is_active:
        print("It's raining - get the washing in!")
        print(no_rain.is_active)

    else:
        print("NO rain")
        print(no_rain.is_active)
    sleep(1)