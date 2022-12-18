#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue

# sensor
import RPi.GPIO as GPIO
import LCD
from gpiozero import InputDevice
import DCmotor

# 먼지센서 모듈
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# transcript_with_exception
import threading
import ctypes
import time


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


sensor_order = 0
is_open = 0



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
    else:
        print("LCD print : no rain")
        LCD.lcd_string("No Rain", LCD_LINE_1)


def dust():
    GPIO.output(LED_Pin, False)
    dustVal=chan0.value
    GPIO.output(LED_Pin,True)

    dust_value = (0.17 * (dustVal * (5.0 / 1024)) - 0.1) * 1000

    return dust_value


class thread_with_exception(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global is_open

        print("창문 상태 :" + str(is_open))  # prints "[31, None, 'send from parent_conn']"

        print("센서 루프 시작")
        no_rain = InputDevice(26)
        rain_value = ""
        dust_value = ""
        DCmotor.init()

        print("센서 켜짐")
        if is_open == 0:
            print("닫혀있음")
        if is_open == 1:
            print("열려있음")

        try:
            while True:
                rain_value = no_rain.is_active
                dust_value = int(dust())

                if not rain_value:
                    result = "rain"
                else:
                    result = "no rain"

                if 600 < dust_value:
                    dust_level = "BAD..T.T"
                elif 400 <= dust_value and dust_value <600:
                    dust_level = "NORMAL"
                elif dust_value < 400:
                    dust_level = "GOOD~>.<"

                lcd(result)  # 빗물감지센서 측정값 출력
                print("LCD print : " + str(dust_value))
                LCD.lcd_string(dust_level, LCD_LINE_2)  # 먼지센서 측정값 출력

                if is_open == 0:  # 창문 닫혀 있는 상태
                    if not rain_value:  # 비가 온 상태
                        print("창문이 닫혀 있는데 비가 옴")
                    else:               # 비가 오지 않는 상태
                        if 500 <= dust_value:  # 미세먼지 많을 때 : 나쁨
                            DCmotor.forward(4.5)  # 창문이 열린다
                            is_open = 1
                        elif 400 <= dust_value and dust_value < 500:
                            is_open = 0
                        elif dust_value < 400:  # 미세먼지 적을 때 : 좋음
                            is_open = 0

                elif is_open == 1:  # 창문 열려 있는 상태
                    if not no_rain.is_active:  # 비가 온 상태
                        DCmotor.reverse(5)  # 창문이 닫힌다.
                        is_open = 0
                    else:                      # 비가 오지 않는 상태
                        if 500 <= dust_value:  # 미세먼지 많을 때 : 나쁨
                            is_open = 1
                        elif 400 <= dust_value and dust_value < 500:
                            is_open = 1
                        elif dust_value < 400:  # 미세먼지 적을 때 : 좋음
                            DCmotor.reverse(5)
                            is_open = 0

                if is_open == 0:
                    print("닫힌 상태")
                else:
                    print("열린 상태")


                time.sleep(1)
        finally:
            print('ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')




# 음성인식 클래스
class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses):
    DCmotor.init()
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0


    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the ext utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        # global transcript
        transcript = result.alternatives[0].transcript



        # Display interim res        # global order
        #         # order = transcriptults, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            global sensor_order
            global is_open

            print(transcript + overwrite_chars)


            if "자동 온" in transcript:
                sensor_order = 1
                print("센서 자동 제어 ON")
                th2 = thread_with_exception('sensor')
                th2.start()

            if "자동 오프" in transcript:
                sensor_order = 0
                th2.raise_exception()
                th2.join()
                print("센서 자동 제어 OFF")
                print("창문 상태 :" + str(is_open))
                lcd(" ")
                LCD.lcd_string("Sensor OFF", LCD_LINE_1)
                LCD.lcd_string(" ", LCD_LINE_2)  # 먼지센서 측정값 출력

            if sensor_order == 0:
                if "닫아" in transcript:
                    if is_open == 1:      # 열려 있는 상태
                        DCmotor.reverse(5)
                        is_open = 0
                        print("닫혔음")


                if "열어" in transcript:
                    if is_open == 0:        # 닫혀 있는 상태
                        DCmotor.forward(4.5)
                        is_open = 1
                        print("열렸음")


                print("창문 상태: " + str(is_open))

            # # Exit recognition if any of the transcribed phrases could be
            # # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "ko-KR"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == "__main__":
    print("스마트 창문 시작!")
    LCD.lcd_string("Sensor OFF", LCD_LINE_1)  # 먼지센서 측정값 출력
    LCD.lcd_string("", LCD_LINE_2)  # 먼지센서 측정값 출력
    main()

# [END speech_transcribe_streaming_mic]
