#led.py
# pin 13 (board number 13)

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
print("LED on")
GPIO.output(13,GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(13,GPIO.LOW)
GPIO.cleanup()  