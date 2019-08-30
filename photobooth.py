# PhotoBooth

# Wiring: Button, LED, Servo Motor (for shutter release), or webcam.

# Camera: Set Connection mode to USB Auto
# gphoto2 --capture-image-and-download
# CAMERA CANNOT BE IN "MENU" Mode.

# TO DO -- need to delete all images from camera at startup
# OTHERWISE gphoto2 --capture-image-and-download might prompt for overwrite
# which would stall this program

# LED on BOARD PIN 13
# SERVO on GPIO 17 which is board pin 11
# servo ground to arduino ground
# servo red power, ground to battery (and ground also to rpi ground)
# 
# wait for button press
#     count down 3..2..1
#     turn on LED
#     snap photo
#          move servo
#          move servo back
#          turn off LED 
#          download image from camera
#     display image on screen
#     show QR code 
#     resize to 3Mb or less
#     tweet it
#     upload to Google Photos
#     delete image(s) from camera
#     delete image(s) from rPi

# Terrific gphoto2 updater: https://github.com/gonzalo/gphoto2-updater

# USBReset because gphoto2 is flaky
# https://raspberrypi.stackexchange.com/questions/9264/how-do-i-reset-a-usb-device-using-a-script
# reset device between sessions?
# do a lsusb
# then do:
# sudo ./usbreset /dev/bus/usb/001/027 or whatever it is

# arcade wait mode
#     

from takepictures import detectCamera, snapPhotoReliably, setupPhotoShoot
from tkinter import *
import time 
from time import sleep
import subprocess
from subprocess import check_output
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import pigpio
import os, glob
from postimage import send_data_to_server, update_status

GPIO.setmode(GPIO.BCM) # broadcom

LED_BCM_PIN = 27 # physical pin number 13
sleepTime = 0.1

BUTTON_BCM_PIN = 22 # physical pin 15

BUTTON_RESET_BCM_PIN = 18 # physical pin 12

from time import sleep

# servo -- use pigpio for jitter-free
# https://steemit.com/python/@makerhacks/jitter-free-servo-control-on-the-raspberry-pi
# note that you first have to run a daemon:
# sudo pigpiod
# I've already started it here with:
# sudo systemctl enable pigpiod


# pin numbering -- broadcom needed
# https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering



myGPIOServo=17 # physical board pin 11
myCorrection=0.45
maxPW=(2.0+myCorrection)/1000
minPW=(1.0-myCorrection)/1000

pi = pigpio.pi()

# light 
GPIO.setup(LED_BCM_PIN, GPIO.OUT)
# start button
# set the default to high, pull up on default
GPIO.setup(BUTTON_BCM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# reset button
GPIO.setup(BUTTON_RESET_BCM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



photoProcessingState = 0 # 0=not set, 1=initializing, 2=ready for button, 3=processing


def extractFileNameFromGphotoOutput(inputString):
    try:
        lines = inputString.splitlines()
        result = lines[1]
        result = result.replace("Saving file as ","")
        return result
    except:
        return ""

def deleteLocalImages():
    try:
        for f in glob.glob("DSC*.jpg"):
            os.remove(f)
        for f in glob.glob("capt*.jpg"):
            os.remove(f)
    except OSError:
        pass
    print("Files Deleted")
    


def moveServo():
    #pi.set_servo_pulsewidth(myGPIOServo, 0)    # off
    #sleep(1)
    pi.set_servo_pulsewidth(myGPIOServo, 1000) # position anti-clockwise
    sleep(1)
    pi.set_servo_pulsewidth(myGPIOServo, 1500) # middle is 1500
    sleep(1)
    pi.set_servo_pulsewidth(myGPIOServo, 0)    # off


def showButton():
    btn.lift()

def hideButton():
    btn.lower()

def updatePhoto(filename):
    global photoProcessingState
    photoProcessingState = 1
    
    global img
    n = 1
    same = True 
    
    path = filename
    image = Image.open(path)
    [imageSizeWidth, imageSizeHeight] = image.size
    newImageSizeWidth = int(imageSizeWidth*n)
    if same:
        newImageSizeHeight = int(imageSizeHeight*n)
    else:
        newImageSizeHeight = int(imageSizeHeight/n) 

    #image = image.resize((newImageSizeWidth, newImageSizeHeight), Image.ANTIALIAS)
    image = image.resize((300, 200), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image)
    
    #print("updating image...")
    #global img
    #img = ImageTk.PhotoImage(Image.open("image2.jpg"))
    #resized = img.zoom(1000,500)
    
    canvas.create_image(10,10, anchor=NW, image=img) 
    canvas.grid(column=0,row=1)
    canvas.update()

def flashLightOn():
    #GPIO.setwarnings(False)
    print("LED on")
    GPIO.output(LED_BCM_PIN, GPIO.HIGH)


def flashLightOff():
    print("LED off")
    GPIO.output(LED_BCM_PIN, GPIO.LOW)


def takePhoto():
    # fswebcam to snap with webcam
    subprocess.Popen(["fswebcam", "-r","1920x1280","--no-banner", "webcam.jpg"])
    lbl.configure(text="PHOTO SNAPPED!")
    updatePhoto("webcam.jpg")
    
    send_data_to_server("webcam.jpg")
    
    # servo based camera cable shutter
    #moveServo()
    
def takePhotoWithGPhoto2():
    lbl.configure(text="Downloading photo...")
    lbl.update()
    out = check_output(["gphoto2", "--capture-image-and-download"])
    print("output is:")
    print(out)
    print(out.decode())
    fileName = extractFileNameFromGphotoOutput(out.decode())
    print(fileName)
    updatePhoto(fileName)
    

    #subprocess.Popen(["gphoto2", "--capture-image-and-download"])
    lbl.configure(text=fileName)
    lbl.update()
    print("loading photo... one moment please")
    print(fileName)
    upload_response = send_data_to_server(fileName)
    print(upload_response)
    print("deleting local files")
    deleteLocalImages()
    
    
def fullReset():
    resetUSB()
    gphotoReset()
    setupPhotoShoot()

def playCameraSound():
    # requires mpg321 install first
    subprocess.Popen(["mpg321","camera.mp3"])

def reset_button_pressed(event):
    print("RESET!")
    update_status("heather","One moment, rebooting board...")
    print("resetting usb")
    sudoPassword="raspberry"
    command = 'reboot'.split()
    p = Popen(['sudo','-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines = True)


    

def physical_button_pressed(event):
    # time.sleep(.01)    # Wait a while for the pin to settle
    #print("pin %s's value is %s" % (BUTTON_BCM_PIN, GPIO.input(BUTTON_BCM_PIN)))
    
    
    
    if (GPIO.input(BUTTON_BCM_PIN)==1):  #ignore second one
        return 
    
    if (not detectCamera()):
        update_status("heather","Camera not detected. Is it powered on?")
        return 
    
    print(time.time())
    global photoProcessingState 
    #sleep(1) # debounce
    print("button")
    print(photoProcessingState)
    
    if (photoProcessingState == 2):
        photoProcessingState = 1
        countdown()
    else:
        photoProcessingState = 1
        print("Not yet ready")


def countdown():
    update_status("heather","Taking a new picture...")
    
    global photoProcessingState
    photoProcessingState = 0
    hideButton()
    lbl.configure(text="READY? COUNTING FROM 3!")
    lbl.update()
    sleep(1)
    updatePhoto("3.png")
    #lbl.configure(text="3...")
    #lbl.update()
    sleep(1)
    updatePhoto("2.png")
    #lbl.configure(text="2...")
    #lbl.update()
    sleep(1)
    #lbl.configure(text="1...")
    #lbl.update()
    updatePhoto("1.png")
    sleep(0.8)
    lbl.configure(text="SNAP!")
    lbl.update()
    flashLightOn()
    #playCameraSound()
    
    # update the web album on popsee 
    update_status("heather","Getting photo from camera...")
    
    updatePhoto("hourglass.png")
    snapPhotoReliably()
    
    
    #playCameraSound()
    #takePhotoWithGPhoto2()

    #updatePhoto("wait.jpg")
    #sleep(0.25)
    lbl.update()
    flashLightOff()
    
    #sleep(2)
    #updatePhoto("image2.jpg")
    updatePhoto("camera.png")
    update_status("heather","Ready")
    lbl.configure(text="Press button to take photo!")
    lbl.update()
    photoProcessingState = 2
    

def clicked():
    btn.grid_remove()
    countdown()
    add_button()

def add_button():
    btn.grid(column=0, row=2)


# delete files
#deleteLocalImages()

setupPhotoShoot()

# set up TKinter window
root = Tk()
root.geometry('600x400')
root.title("Photo Booth")

lbl = Label(root, text="Press button to take photo!", font=("Arial Bold", 20))
lbl.grid(column=0, row=0)
update_status("heather","")

canvas = Canvas(root, width = 600, height = 400) 
img = ImageTk.PhotoImage(Image.open("camera.png"))      
canvas.create_image(0,0, anchor=NW, image=img) 
canvas.grid(column=0,row=1)

btn = Button(root, text="Take Photo", command=clicked)
btn.grid(column=0, row=2)

photoProcessingState = 2 # ready for input
update_status("heather","Ready")

# detect 3..2..1 button
GPIO.add_event_detect(BUTTON_BCM_PIN, GPIO.BOTH, callback=physical_button_pressed, bouncetime=500)
# detect reset button
GPIO.add_event_detect(BUTTON_RESET_BCM_PIN, GPIO.BOTH, callback=reset_button_pressed, bouncetime=500)


root.mainloop()



print("Goodbye...")
GPIO.cleanup()
