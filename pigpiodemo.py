import pigpio
from time import sleep

# connect to the 
pi = pigpio.pi()

# loop forever
for i in range(0,3):
    
    pi.set_servo_pulsewidth(17, 0)    # off
    sleep(1)
    pi.set_servo_pulsewidth(17, 1000) # position anti-clockwise
    sleep(1)
    pi.set_servo_pulsewidth(17, 1500) # middle
    sleep(1)
    pi.set_servo_pulsewidth(17, 2000) # position clockwise
    sleep(1)
    pi.set_servo_pulsewidth(17, 0)  