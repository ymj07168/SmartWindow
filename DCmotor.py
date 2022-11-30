import RPi.GPIO as gpio
import time

BIN1 = 18
BIN2 = 12

def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(BIN1, gpio.OUT)
    gpio.setup(BIN2, gpio.OUT)


def forward(sec):
    init()
    gpio.output(BIN1, True)
    gpio.output(BIN2, False)
    time.sleep(sec)
    gpio.cleanup()


def reverse(sec):
    init()
    gpio.output(BIN1, False)
    gpio.output(BIN2, True)
    time.sleep(sec)
    gpio.cleanup()


print("forward")
forward(3)
print("reverse")
reverse(3.5)
