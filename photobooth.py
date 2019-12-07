# PhotoBooth

# https://www.stevemurch.com/build-a-photo-booth-for-your-next-party/2019/12

# WARNING: This code (by design) will delete all photos on your 
# camera's SD card when it boots up. This is to get the 
# camera ready to take photos and to generally save time in file transfer,
# and avoid file collisions (e.g., prompts to overwrite the filename)...  
# Also saves the camera and RPi from iterating through a bunch of photos. 

# GPIO PINS ARE IN BROADCOM FORMAT, NOT PHYSICAL PIN FORMAT

# Raspberry Pi 3B+ used. Connected to Wifi. 

# Wiring: You'll need a large arade button w/LED, USB cable, and a relay to a 110V connection. 

# Camera: Set Connection mode to USB Auto. Put it in PTP mode if it has one. Disable any power saving/screensaver. 
# Install gphoto2, turn on your camera, connect the USB cable, and try running the 
# following on the RPi command line to test the connection: 

# gphoto2 --capture-image-and-download

# In my own tests with a Fuji X-T2, note that the camera CANNOT be in "MENU" mode

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

from takepictures import resetUSB, gphotoReset, detectCamera, snapPhotoReliably, setupPhotoShoot
from tkinter import *
import time 
from time import sleep
import subprocess
from subprocess import check_output, Popen, PIPE
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import os, glob
from remoterequests import send_data_to_server, send_data_to_server_async, update_status, get_current_config
import logging

# Back-end support. 
# The file "secret.py" is not in the GitHub repo, and simply holds the value for these variables, 
# which relate to POSTing an image to a remote server: 
# 
# albumCode:    the "shortcode" for the popsee album to post to
# postImageUrl: the URL to POST images to 
# statusUrl:    the URL to POST text status updates to (the server then rebroadcasts them)
from secret import *





try: 
    os.chdir("/home/pi/Desktop/photobooth")
except:
    print("Please run this from /home/pi/Desktop/photobooth")

# get the home screen image
# Comment out this line if you're not using the popsee server.
get_current_config("")


logging.basicConfig(level=logging.DEBUG, filename='photobooth.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.info("Initializing")

# Various globals

GO_FULL_SCREEN = True
is_exiting = False 

# Some settings I use for development on desktop Windows 
if (sys.platform == "win32"):
    GO_FULL_SCREEN = False 



sleepTime = 0.1
photo_round = 0
bPhotoButtonLit = False
bSnapPhotoButtonShouldFlash = True
is_kiosk_mode = True
current_kiosk_screen = 0 

# PIN I/O for Raspberry Pi 
GPIO.setmode(GPIO.BCM) # broadcom

# PINS 

LED_BCM_PIN = 27 # physical pin number 13.
BUTTON_BCM_PIN = 22 # physical pin 15 -- This is the blue GO button
SNAP_PHOTO_LED_BCM_PIN = 4 # physical pin 7 -- This is the LIGHT inside the blue GO button
RELAY_CONTROL_PIN = 18 # physical pin 12 -- Turn on or off the relay (photographic lighting)

# pin numbering -- broadcom needed
# https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering

# light 
GPIO.setup(LED_BCM_PIN, GPIO.OUT)

# LED on pushbutton
GPIO.setup(SNAP_PHOTO_LED_BCM_PIN, GPIO.OUT)

# RELAY CONTROL FOR LIGHTS JUST BEFORE SHOT
GPIO.setup(RELAY_CONTROL_PIN, GPIO.OUT)

# start button
# set the default to high, pull up on default
GPIO.setup(BUTTON_BCM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

photoProcessingState = 0 # 0=not set, 1=initializing, 2=ready for button, 3=processing

def turnOffPhotoLighting():
    GPIO.output(RELAY_CONTROL_PIN, GPIO.LOW)
    
def turnOnPhotoLighting():
    GPIO.output(RELAY_CONTROL_PIN, GPIO.HIGH)

# called by loop. 
# if button should be flashing, toggle it. if it shouldn't turn it off.
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
        logging.info("extractFileNameFromGphotoOutput: %s", result)
        return result
    except:
        logging.exception("Could not extractFileNameFromGphotoOutput('%s')", inputString)
        return ""

# Delete all the local images on the SD Card
# This is done to make photo handling simpler and faster (don't have to iterate through all files)

def deleteLocalImages():
    try:
        for f in glob.glob("DSC*.jpg"):
            os.remove(f)
        for f in glob.glob("capt*.jpg"):
            os.remove(f)
    except OSError:
        logging.exception("OS error in deleteLocalImages()")

        pass
    print("Files deleted.")
    logging.info("Files deleted.")
    
def updatePhoto(filename):
    logging.info("update photo to %s", filename)
    
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

    image = image.resize(1440, 960, Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image)
    
    canvas.create_image(0,0, anchor=NW, image=img) 
    canvas.grid(column=1,row=1,padx=(0,0), pady=(0,0))
    canvas.update()
    
def updatePhotoFull(filename):
    global is_exiting 
    if (is_exiting==True):
        return 
    logging.info("update photo to %s", filename)
    
    global photoProcessingState
    photoProcessingState = 1
    global image
    
    global imgFull
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

    image = image.resize((1440, 960), Image.ANTIALIAS)
    imgFull = ImageTk.PhotoImage(image)
    
    canvas.create_image(0,0, anchor=NW, image=imgFull) 
    canvas.grid(column=0,row=0,padx=(0,0), pady=(0,0))
    canvas.update()

    

def flashLightOn():
    GPIO.output(LED_BCM_PIN, GPIO.HIGH)

def flashLightOff():
    GPIO.output(LED_BCM_PIN, GPIO.LOW)
    
def fullReset():
    logging.warning("fullReset called")
    resetUSB()
    gphotoReset()
    setupPhotoShoot()


# Uses mpg321 to play an MP3 file. 
# Install mpg321 onto your RPi via:
# sudo apt-get install mpg321 

def playChimeSound():
    # requires mpg321 install first
    try:
        subprocess.Popen(["mpg321","-q", "chime.mp3"])
    except:
        print("exception playing chime")
    return

def playGetReadySound():
    # requires mpg321 install first
    try:
        subprocess.Popen(["mpg321","-q","get-ready.mp3"])
    except:
        print("exception playing GET READY sound")
    return


# Called when reset button is pressed. 
# An optional hardware reset button can be wired into the board. 
# In my first build, I decided not to mount this reset button into the enclosure; 
# Instead I provided a keyboard and mouse for admin input. 

def reset_button_pressed(event):
    logging.warning("reset_button_pressed")
    logging.warning("Initiating a reset of the board.")
    print("RESET!")
    update_status(albumCode, "Reset button pressed. One moment; rebooting photo booth...")
    print("resetting usb")
    sudoPassword="raspberry"
    command = 'reboot'.split()
    p = Popen(['sudo','-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines = True)

def physical_button_pressed(event):
    global photoProcessingState 
    global bSnapPhotoButtonShouldFlash

    print("physical_button_pressed")
    if (GPIO.input(BUTTON_BCM_PIN)==1):  #ignore second one; debounce the button
        return 
    
    logging.info("physical_button_pressed called")
    bSnapPhotoButtonShouldFlash = False 
    
    if (not detectCamera()):
        logging.error("Cannot detect camera. Is it powered on?")
        update_status(albumCode,"Camera not detected. Is it powered on?")
        updatePhotoFull("assets/images/error-no-camera.png")
        return 
    
    if (photoProcessingState == 2):
        photoProcessingState = 1
        countdown()
    else:
        photoProcessingState = 1
        logging.error("photoProcessingState is 1; not yet ready")
        countdown() 

def show_upload_processing_graphic():
    updatePhotoFull("assets/images/see-your-photos.png")
    
def show_got_it():
    updatePhotoFull("got-it.png")

def update_and_show_photo_round():
    updatePhotoRound()
    showPhotoRound()

def clearDisplay():
    updatePhotoFull("assets/images/clearpixel.png")

def countdown():
    global photo_round
    global current_kiosk_screen
    current_kiosk_screen = 0
    global is_kiosk_mode
    is_kiosk_mode = False 
    global is_counting_down
    is_counting_down = True 
    logging.info("COUNTDOWN called")
    
    clearDisplay()
    
    global bSnapPhotoButtonShouldFlash
    bSnapPhotoButtonShouldFlash = False
    
    update_status(albumCode,"Taking a new picture...")
    
    global photoProcessingState
    photoProcessingState = 0

    if (photo_round==1):
        playGetReadySound()
    
    showPhotoRound()
    
    sleep(2)
    
    turnOnPhotoLighting()
    # display "READY?"
    
    if (photo_round==1):
        sleep(3)
    else:
        sleep(0.2)
    
    if (photo_round==1):
        updatePhotoFull("assets/images/5.png")
        playChimeSound()
        sleep(0.5)

        updatePhotoFull("assets/images/4.png")
        playChimeSound()
        sleep(0.5)
    
    updatePhotoFull("assets/images/3.png")
    playChimeSound()
    sleep(0.5)
    
    #playChimeSound()
    updatePhotoFull("assets/images/2.png")
    sleep(0.5)
    
    #playChimeSound()
    updatePhotoFull("assets/images/1.png")
    sleep(0.3)
    
    # update the web album on popsee 
    update_status(albumCode,"Getting photo from camera...")
    logging.info("Getting photo from camera")
    
    is_counting_down = False 
    root.after(50, show_got_it)
    
    root.after(2000, turnOffPhotoLighting)
    root.after(1600, show_wait_indicator)
    fileNameOrError = snapPhotoReliably()
    
    logging.info("snapPhotoReliably result is:%s", fileNameOrError)
    
    print("fileNameOrError is:")
    print("["+fileNameOrError+"]")
    
    if (fileNameOrError == "") or (fileNameOrError == "Try Again"):
        print("COULD NOT GET PHOTO FROM CAMERA. ERROR NEEDING RESET OCCURRED. ONE MOMENT.")
        resetUSB()
        gphotoReset()
        deleteLocalImages()
        print("An error occurred A1")
        logging.error("An error occurred:%s", fileNameOrError)
        update_status(albumCode,"Error on last photo attempt. Could not get photo from camera. Please try again.")
        photoProcessingState = 2
        flashLightOff()
        hide_wait_indicator()
        bSnapPhotoButtonShouldFlash = True
        return "Error"
    
    if ("error" not in fileNameOrError) and ("Error" not in fileNameOrError) :
        update_status(albumCode,"Your photo is on its way...")
        logging.info("Got what looks like a filename from camera:%s", fileNameOrError)

        print("sending file to server")
        print(fileNameOrError)
        updatePhotoFull(fileNameOrError)
        print("SHOWING ["+fileNameOrError+"]")
        sleep(1)
        updatePhotoFull(fileNameOrError)

        logging.info("Uploading %s to popsee", fileNameOrError)

        upload_response = send_data_to_server_async(fileNameOrError)
        time.sleep(3)
        hide_wait_indicator()
        print(upload_response)
        updatePhotoRound()
        logging.info("response from upload: %s", upload_response)
        flashLightOff()
        
    else:
        print("An error occurred Q1")
        updatePhotoFull("assets/images/sorry-error.png")
        logging.error("An error occurred:%s", fileNameOrError)
        update_status(albumCode,"Error on last photo attempt. Trying again.")
        
        photoProcessingState = 2
        flashLightOff()
        hide_wait_indicator()
        bSnapPhotoButtonShouldFlash = True
        countdown()
        return 
    
    update_status(albumCode,"Ready")
    
    is_kiosk_mode = True 
    hide_wait_indicator()
    photoProcessingState = 2
    
    if (photo_round > 1):
        countdown()
        return
    
    bSnapPhotoButtonShouldFlash = True

def clicked():
    hide_qr_code_prompt()
    countdown()

def update_wait_indicator(ind):
    global bShowWaitIndicator
    if (bShowWaitIndicator):
        if (ind == maxFrames):
            ind = 0
            root.after(0,update_wait_indicator, ind)
            return
        frame = frames[ind]
        ind += 1
        waitindicator.configure(image=frame, borderwidth=0, highlightbackground='black', highlightthickness=0)
        root.after(150, update_wait_indicator, ind)
    else:
        ind = 0
        

def show_wait_indicator():
    global is_exiting
    if (is_exiting):
        return 
    global bShowWaitIndicator
    bShowWaitIndicator = True
    waitindicator.grid(column=1, row=0, pady=(0,0), padx=(0,0))
    # show wait indicator
    root.after(0, update_wait_indicator, 0)

    
def hide_wait_indicator():
    global is_exiting
    if (is_exiting):
        return 
    global bShowWaitIndicator
    bShowWaitIndicator = False
    waitindicator.grid_remove()

def showHomeScreenImage():
    updatePhotoFull("homescreen-image.jpg")

    #updatePhotoFull("assets/images/photo-booth-home.jpg")


def handleKioskMode():
    global current_kiosk_screen 
    global is_kiosk_mode 
    if (is_kiosk_mode):
        #updatePhotoFull("sample-image.jpg")
        showHomeScreenImage()
    else:
        x=1
    root.after(10000, handleKioskMode)

def showPhotoRound():
    global photo_round
    fileToShow = "assets/images/"+str(photo_round)+"-of-3.png"
    updatePhotoFull(fileToShow)
    

def updatePhotoRound():
    global photo_round
    if (photo_round == 3):
        photo_round = 0
    
    photo_round = photo_round + 1
    
def handleKeyPress(event):
    if (is_exiting==False):
        print(event.char)
        if (event.char=="x"):
            countdown()

def cleanup_and_exit():
    global is_exiting 
    is_exiting = True 
    GPIO.cleanup()
    print("Exiting now.")
    root.destroy()
    exit()


# delete files
# deleteLocalImages()

setupPhotoShoot()

is_counting_down = False 

# set up main TKinter root window
root = Tk()
root.geometry('1440x960')
root.title("Photo Booth")
root.configure(background='red', borderwidth=0, border=0, highlightthickness=0)

# remove titlebar
# root.overrideredirect(1)

if GO_FULL_SCREEN:
    root.attributes("-fullscreen", True)

update_status(albumCode,"")

canvas = Canvas(root, width = 1440, height = 960, background='#000',highlightthickness=0, borderwidth=0, border=0) 

photoProcessingState = 2 # ready for input
update_status(albumCode,"Ready")

# detect 3..2..1 button
GPIO.add_event_detect(BUTTON_BCM_PIN, GPIO.BOTH, callback=physical_button_pressed, bouncetime=500)

# wait indicator on lit button, to flash on and off
root.after(1000, handlePhotoButtonFlash)

# wait indicator
maxFrames = 8
bShowWaitIndicator = False 
frames = [PhotoImage(file='assets/images/wait-indicator.gif',format = 'gif -index %i' %(i)) for i in range(0, maxFrames)]
waitindicator = Label(root, highlightthickness=0,borderwidth=0, highlightbackground='black')

root.after(0, handleKioskMode)    

root.bind('<Escape>', lambda e: cleanup_and_exit())

# Any key press will exit the photo booth. 
root.bind('<Any-KeyPress>', handleKeyPress)

updatePhotoRound()


#label = Label(root, text="Hello xxxx world")
#label.grid(column=0,row=0,padx=(0,0), pady=(0,0))


# Run the main loop
root.mainloop()

