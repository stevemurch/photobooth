# transistor.py
# control LED with NPN transistor

import RPi.GPIO as GPIO
from time import sleep

CONTROL_PIN = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(CONTROL_PIN, GPIO.OUT)

for i in range(1,10):
    GPIO.output(CONTROL_PIN, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(CONTROL_PIN, GPIO.LOW)
    sleep(0.1)

GPIO.cleanup()
