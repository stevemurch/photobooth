import time 
from time import sleep
import subprocess
from subprocess import check_output
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import os, glob
from subprocess import Popen, PIPE
from remoterequests import update_status, send_data_to_server
from secret import *
import sys 

# Occasionally if autofocus does not work, Fuji X-T2 will report back that autofocus is a problem
# and all further attempts hang. Only solution I've found is to reset the full USB hub, not just
# the USB connection to the camera.

# This seems to be a software solution (though hacky) to get over the showstopper bugs when
# PTP errors or autofocus errors hang the process. 

IS_DESKTOP_DEVELOPMENT = False 

if (sys.platform == "win32"):
    IS_DESKTOP_DEVELOPMENT = True 
    

def resetUSB():
    update_status(albumCode,"One moment, resetting USB...")
    print("resetting usb")
    sudoPassword="raspberry"
    command = 'usbreset 001/002'.split()

    try:
        p = Popen(['sudo','-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines = True)
        sudo_prompt = p.communicate(sudoPassword + '\n')[1]
        sleep(3)
    except:
        print("exception on resetting usb")

    print("done resetting usb")
    #p = os.system("echo %s|sudo -S %s" % (sudoPassword, command))

def gphotoReset():
    update_status(albumCode, "Resetting link to camera...")

    try:
        out = check_output(["gphoto2","--reset"])
        sleep(0.5)
    except:
        print("exception in resetting link to camera")
    
    
# normal output should have DSCF and JPG in it, and no mention of error.
# If not, it's an error
def detectErrorNeedingReset(inString):
    print("checking this string for presence of magic words:")
    print(inString)
    # if the word Error or error
    
    if ("is in location" in inString):
        update_status(albumCode,"Got photo successfully...")
        return False
    return True

def detectCamera():
    try:
        out = check_output(["gphoto2", "--auto-detect"]).decode()
        if ("Fuji" not in out):
            update_status(albumCode,"Camera not detected. Is it powered on? Check, and try again.")
            return False
        return True
    except:
        print("exception in resetting camera")
        return False 

def takePicture():
    global IS_DESKTOP_DEVELOPMENT
    print("taking picture...")

    if (IS_DESKTOP_DEVELOPMENT):
        return "sample-image.jpg"

    outString = "Error Error Error"
    
    try:
        print("before check_output")
        out = check_output(["gphoto2", "--capture-image-and-download"])
        # I've seen it error here. Best put in some kind of reset clock
        
        print("output is:")
        outString = out.decode()
        print("outString:")
        print(outString)
        if ("No camera found" in outString):
            update_status(albumCode,"No camera found. Ensure it's powered on.")
            messagebox.showinfo("No Camera Found.","No camera found. Ensure it's powered on.")
    except:
        if (not detectCamera()):
            update_status(albumCode,"No camera found. Ensure it's powered on.")
        if (detectCamera()):
            update_status(albumCode,"Exception! Trying to reset USB. One moment.")
            print("Exception! Trying to reset USB. One moment.")
            resetUSB()
            gphotoReset() # will fail if power is turned off or no camera found
            deleteLocalImages()
            return "Error"
    else:
        print("Success")
        
    print("checking if return statement contained an error")
    errorNeedingResetOccurred = detectErrorNeedingReset(outString)
    if (errorNeedingResetOccurred):
        print("ERROR NEEDING RESET OCCURRED. ONE MOMENT.")
        resetUSB()
        try: 
            gphotoReset()
        except:
            print("gphotoReset caused an exception.")
        deleteLocalImages()
        return "Error"
    
    fileName = extractFileNameFromGphotoOutput(out.decode())
    return fileName 
    
    #deleteLocalImages()

def extractFileNameFromGphotoOutput(inputString):
    try:
        lines = inputString.splitlines()
        result = lines[1]
        result = result.replace("Saving file as ","")
        return result
    except:
        return ""

def deleteLocalImages():
    print("deleting local files")
    try:
        for f in glob.glob("DSC*.jpg"):
            os.remove(f)
        for f in glob.glob("capt*.jpg"):
            os.remove(f)
    except OSError:
        pass
    print("Files Deleted")


def setupPhotoShoot():
    deleteLocalImages()
    if (not detectCamera()):
        exit
        
def snapPhotoReliably():
    try:
        #resetUSB()
        #gphotoReset()
        result = takePicture()
        return result 
    except:
        print("An error has occurred in the application. One moment while I reset.")
        update_status(albumCode, "An error occurred... one moment while I reset.")
        resetUSB()
        gphotoReset()
        update_status(albumCode, "OK, I've reset. Please try again.")
        return "Try Again"

      
                  
    
