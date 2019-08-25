# kill images from camera
# while (read buttons)
# if button pressed:
#    count down 3..2..1
#    move servo to snap photo
#    move servo back to neutral
#    download image to rPi
#    display it
#    choose KEEP or RETAKE
#    when KEEP
#        tweet it out
#        give people message
#    kill images from camera
# cycle through kiosk display

from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
pwm=GPIO.PWM(11,50)
pwm.start(7)
for i in range(0,20):
    desiredPosition=input("Where do you want the Servo?")
    sleep(0.5)
    pwm.start(7) 
    DC=1./18.*(desiredPosition)+2
    pwm.ChangeDutyCycle(DC)
    sleep(2)
    pwm.stop()
 
GPIO.cleanup()


