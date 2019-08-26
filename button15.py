# wire the button on pin 15 -- GPIO22

import RPi.GPIO as GPIO
from time import sleep

print("Press the button")

GPIO.setmode(GPIO.BOARD)

sleepTime = 0.1

buttonPin = 15

# set the default to high, pull up on default
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if (GPIO.input(buttonPin) == False):
        print("PRESSED",end='\r')
    else:
        print("       ",end='\r')
    sleep(sleepTime)
