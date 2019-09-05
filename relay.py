# relay.py

import RPi.GPIO as GPIO
from time import sleep

RELAY_CONTROL_PIN = 18 # BCM format; this is pin 12 physically
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_CONTROL_PIN, GPIO.OUT)

try:
    while True:
        sleep(1)
        print("off")
        GPIO.output(RELAY_CONTROL_PIN, GPIO.LOW)
        sleep(1)
        print("on")
        GPIO.output(RELAY_CONTROL_PIN, GPIO.HIGH)
except:
    print("caught!")

finally:
    print("Goodbye.")
    GPIO.output(RELAY_CONTROL_PIN, GPIO.LOW)
    GPIO.cleanup()
