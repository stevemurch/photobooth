# PhotoBooth

# PINS ARE IN BROADCOM FORMAT, NOT PHYSICAL PIN FORMAT
# Wiring: Button and LED, USB cable

# Camera: Set Connection mode to USB Auto
# gphoto2 --capture-image-and-download
# CAMERA CANNOT BE IN "MENU" Mode.

# TO DO -- need to delete all images from camera at startup
# OTHERWISE gphoto2 --capture-image-and-download might prompt for overwrite
# which would stall this program

# LED on BOARD PIN 13


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
from subprocess import check_output, Popen, PIPE
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import os, glob
from postimage import send_data_to_server, update_status

os.chdir("/home/pi/Desktop/photobooth")

GPIO.setmode(GPIO.BCM) # broadcom

LED_BCM_PIN = 27 # physical pin number 13
sleepTime = 0.1

BUTTON_BCM_PIN = 22 # physical pin 15

BUTTON_RESET_BCM_PIN = 18 # physical pin 12

SNAP_PHOTO_LED_BCM_PIN = 4 # physical pin 7


bPhotoButtonLit = False
bSnapPhotoButtonShouldFlash = True  

# pin numbering -- broadcom needed
# https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering

# light 
GPIO.setup(LED_BCM_PIN, GPIO.OUT)

# LED on pushbutton
GPIO.setup(SNAP_PHOTO_LED_BCM_PIN, GPIO.OUT)

# start button
# set the default to high, pull up on default
GPIO.setup(BUTTON_BCM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# reset button
GPIO.setup(BUTTON_RESET_BCM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

photoProcessingState = 0 # 0=not set, 1=initializing, 2=ready for button, 3=processing

# called by loop. if button should be flashing, toggle it. if it shouldn't turn it off.
def handlePhotoButtonFlash():
    global bPhotoButtonLit
    global bSnapPhotoButtonShouldFlash
    if (bSnapPhotoButtonShouldFlash):
        if (not bPhotoButtonLit):
            GPIO.output(SNAP_PHOTO_LED_BCM_PIN, GPIO.HIGH)
            bPhotoButtonLit = True
        else:
            GPIO.output(SNAP_PHOTO_LED_BCM_PIN, GPIO.LOW)
            bPhotoButtonLit = False
    else:
        bPhotoButtonLit = False
        GPIO.output(SNAP_PHOTO_LED_BCM_PIN, GPIO.LOW)
    root.after(1000, handlePhotoButtonFlash)
    

def flashTakePhotoButton(nTimes):
    for i in range(1,nTimes):
        GPIO.output(SNAP_PHOTO_LED_BCM_PIN, GPIO.HIGH)
        bSnapPhotoButtonLit = True 
        sleep(0.1)
        GPIO.output(SNAP_PHOTO_LED_BCM_PIN, GPIO.LOW)
        bSnapPhotoButtonLit = False 
        sleep(0.1)

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
    #canvas.update()

def flashLightOn():
    #GPIO.setwarnings(False)
    print("LED on")
    GPIO.output(LED_BCM_PIN, GPIO.HIGH)


def flashLightOff():
    print("LED off")
    GPIO.output(LED_BCM_PIN, GPIO.LOW)


# def takePhoto():
#     # fswebcam to snap with webcam
#     subprocess.Popen(["fswebcam", "-r","1920x1280","--no-banner", "webcam.jpg"])
#     lbl.configure(text="PHOTO SNAPPED!")
#     updatePhoto("webcam.jpg")
#     
#     send_data_to_server("webcam.jpg")
   
    
# def takePhotoWithGPhoto2():
#     lbl.configure(text="Downloading photo...")
#     lbl.update()
#     out = check_output(["gphoto2", "--capture-image-and-download"])
#     print("output is:")
#     print(out)
#     print(out.decode())
#     fileName = extractFileNameFromGphotoOutput(out.decode())
#     print(fileName)
#     updatePhoto(fileName)
#     
# 
#     #subprocess.Popen(["gphoto2", "--capture-image-and-download"])
#     lbl.configure(text=fileName)
#     lbl.update()
#     print("loading photo... one moment please")
#     print(fileName)
#     upload_response = send_data_to_server(fileName)
#     print(upload_response)
#     print("deleting local files")
#     deleteLocalImages()
    
    
def fullReset():
    resetUSB()
    gphotoReset()
    setupPhotoShoot()

def playCameraSound():
    # requires mpg321 install first
    subprocess.Popen(["mpg321","camera.mp3"])

def reset_button_pressed(event):
    if (GPIO.input(BUTTON_RESET_BCM_PIN)==1):  #ignore second one
        return
    
    print("RESET!")
    #update_status("heather","One moment, rebooting board...")
    #print("resetting usb")
    #sudoPassword="raspberry"
    #command = 'reboot'.split()
    #p = Popen(['sudo','-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines = True)


    

def physical_button_pressed(event):
    # time.sleep(.01)    # Wait a while for the pin to settle
    #print("pin %s's value is %s" % (BUTTON_BCM_PIN, GPIO.input(BUTTON_BCM_PIN)))
    
    
    
    if (GPIO.input(BUTTON_BCM_PIN)==1):  #ignore second one
        return 
    
    global bSnapPhotoButtonShouldFlash
    bSnapPhotoButtonShouldFlash = False 
    
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

def update_label():
    lbl.configure(text="Great! One moment...")
    lbl.update()


def countdown():
    global bSnapPhotoButtonShouldFlash
    bSnapPhotoButtonShouldFlash = False
    
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
    
    
    
    
    flashLightOn()
    #playCameraSound()
    
    
    
    # update the web album on popsee 
    update_status("heather","Getting photo from camera...")
    
    updatePhoto("camera.png")

    #global root
    root.after(1100, update_label)
    root.after(1600, show_wait_indicator)
    
    fileNameOrError = snapPhotoReliably()
    
    print("fileNameOrError is:")
    print(fileNameOrError)
    


    if ("error" not in fileNameOrError) and ("Error" not in fileNameOrError) :
        update_status("heather","Your photo is on its way...")
        print("sending file to server")
        print(fileNameOrError)
        updatePhoto(fileNameOrError)
        
        lbl.configure(text="Uploading to Popsee...")
        lbl.update()
        upload_response = send_data_to_server(fileNameOrError)
        hide_wait_indicator()
        print(upload_response)
        flashLightOff()
    else:
        print("An error occurred")
        lbl.configure(text="An error occurred. Please try again.")
        update_status("heather","Error on last photo attempt. Please try again.")
        lbl.update()
        photoProcessingState = 2
        flashLightOff()
        hide_wait_indicator()
        return 
    
    #playCameraSound()
    #takePhotoWithGPhoto2()

    #updatePhoto("wait.jpg")
    #sleep(0.25)
    #lbl.update()

    

    
    #sleep(2)
    #updatePhoto("image2.jpg")
    #updatePhoto("camera.png")
    update_status("heather","Ready")
    lbl.configure(text="READY for next photo! Press button!")
    hide_wait_indicator()
    lbl.update()
    photoProcessingState = 2
    
    bSnapPhotoButtonShouldFlash = True
    

def clicked():
    btn.grid_remove()
    countdown()
    add_button()

def add_button():
    btn.grid(column=0, row=2)


def update_wait_indicator(ind):
    global bShowWaitIndicator
    if (bShowWaitIndicator):
        if (ind==maxFrames):
            ind = 0
            root.after(0,update_wait_indicator, ind)
            return
        #print(ind)
        frame = frames[ind]
        ind += 1
        #print(ind)
        waitindicator.configure(image=frame, borderwidth=0, highlightbackground='black', highlightthickness=0)
        root.after(150, update_wait_indicator, ind)
    else:
        ind = 0
        

def show_wait_indicator():
    global bShowWaitIndicator
    bShowWaitIndicator = True
    waitindicator.grid(column=0, row=1)
    # show wait indicator
    root.after(0, update_wait_indicator, 0)

    
def hide_wait_indicator():
    global bShowWaitIndicator
    bShowWaitIndicator = False
    waitindicator.grid_remove()

def keypressed(event):
    out_string = '{k!r}'.format(k = event.char)
    print(out_string)
    print(event.char)
    if (event.char == 'x'): # escape
        print("EXITING")
        #GPIO.cleanup()
        root.destroy()
    



# delete files
#deleteLocalImages()

setupPhotoShoot()

#flashTakePhotoButton(10)

# set up TKinter window
root = Tk()
root.geometry('600x400')
root.title("Photo Booth")
root.configure(background='black')

# remove titlebar
# root.overrideredirect(1)

lbl = Label(root, text="Press button to take photo!",highlightthickness=0, font=("Arial Bold", 20), foreground='white', background='black')
lbl.grid(column=0, row=0)
update_status("heather","")

canvas = Canvas(root, width = 600, height = 400, background='#000',highlightthickness=0) 
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

# wait indicator on SnapPhoto button
root.after(1000, handlePhotoButtonFlash)

# wait indicator
maxFrames = 8
bShowWaitIndicator = False 
frames = [PhotoImage(file='sample.gif',format = 'gif -index %i' %(i)) for i in range(0, maxFrames)]
waitindicator = Label(root, highlightthickness=0,borderwidth=0, highlightbackground='black')


root.bind('<Key>', keypressed)


root.mainloop()



print("Goodbye...")
GPIO.cleanup()
