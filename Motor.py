# import RPi.GPIO as gpio
import time
from gpiozero import Motor

BIN1 = 18
BIN2 = 12

motor = Motor(forward=18, backward=12)

print("forward")
motor.forward()
# print("backward")
# motor.backward()
