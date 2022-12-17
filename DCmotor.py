import RPi.GPIO as gpio
import time

BIN1 = 18
BIN2 = 12

def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(BIN1, gpio.OUT)
    gpio.setup(BIN2, gpio.OUT)


def forward(sec):
    # init()
    gpio.output(BIN1, True)
    gpio.output(BIN2, False)
    time.sleep(sec)
    gpio.output(BIN1, False)
    # gpio.cleanup()


def reverse(sec):
    # init()
    gpio.output(BIN1, False)
    gpio.output(BIN2, True)
    time.sleep(sec)
    gpio.output(BIN2, False)
    # gpio.cleanup()

#
# init()
# while True:
#     print("forward")
#     forward(1)
#     print("reverse")
#     reverse(1)