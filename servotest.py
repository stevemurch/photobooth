from gpiozero import Servo
from time import sleep
 
myGPIO=17 #GPIO numbering system
 
servo = Servo(myGPIO)
 
while True:
    servo.mid()
    print("mid")
    sleep(1)
    servo.min()
    print("min")
    sleep(2)
    servo.mid()
    print("mid")
    sleep(1)
    servo.max()
    print("max")
    sleep(2)