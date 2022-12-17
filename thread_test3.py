from threading import Thread
import RPi.GPIO as GPIO
import LCD
from gpiozero import InputDevice
import time
import DCmotor

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

def lcd(res):
    if res == "rain":
        print("LCD print : rain")
        LCD.lcd_string("Raining", LCD_LINE_1)
        # LCD.lcd_string("", LCD_LINE_2)
    else:
        print("LCD print : no rain")
        LCD.lcd_string("No Rain", LCD_LINE_1)
        # LCD.lcd_string("", LCD_LINE_2)


def dust():
    GPIO.output(LED_Pin, False)
    dustVal=chan0.value
    GPIO.output(LED_Pin,True)

    # if (dustVal>36.455):
    dust_value = ((dustVal/1024)-0.0356)*120000*0.035
    # print("LCD print" + dust_value)
    # LCD.lcd_string(str(dust_value), LCD_LINE_2)

    return dust_value




if __name__ == "__main__":
    no_rain = InputDevice(26)
    result = ""
    dust_value = ""
    DCmotor.init()
    is_open = 0 # 닫힌 상태
    print("닫혀있음")

    while True:
        dust_value = dust()

        lcd(result)                                 # 빗물감지센서 측정값 출력
        print("LCD print" + str(dust_value))
        LCD.lcd_string(str(dust_value), LCD_LINE_2) # 먼지센서 측정값 출력

        if is_open == 0:                # 창문 닫혀 있는 상태
            if not no_rain.is_active:   # 비가 온 상태
                result = "rain"
            else:
                result = "no_rain"      # 비가 오지 않은 상태
                if dust() > 300:     # 미세먼지 많을 때
                    DCmotor.reverse(3)  # 창문이 열린다
                    is_open = 1


        elif is_open == 1:              # 창문 열려 있는 상태
            if not no_rain.is_active:   # 비가 온 상태
                result = "rain"
                DCmotor.forward(3)      # 창문이 닫힌다.
                is_open = 0
            else:
                result = "no_rain"      # 비가 오지 않은 상태
                if dust() <= 300:    # 미세먼지 적을 때
                    DCmotor.forward(3)  # 창문이 닫힌다.
                    is_open = 0


        if is_open == 0:
            print("닫혔음")
        else:
            print("열렸음")
        time.sleep(1)
        # lcd = Thread(target=lcd, args=(1, result,))