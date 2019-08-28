import time 
from time import sleep
import subprocess
from subprocess import check_output
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import os, glob
from postimage import send_data_to_server
from subprocess import Popen, PIPE


# Occasionally if autofocus does not work, Fuji X-T2 will report back that autofocus is a problem
# and all further attempts hang. Only solution I've found is to reset the full USB hub, not just
# the USB connection to the camera.

# This seems to be a software solution (though hacky) to get over the showstopper bugs when
# PTP errors or autofocus errors hang the process. 

def resetUSB():
    print("resetting usb")
    sudoPassword="raspberry"
    command = 'usbreset 001/002'.split()
    p = Popen(['sudo','-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines = True)
    sudo_prompt = p.communicate(sudoPassword + '\n')[1]
    sleep(3)
    print("done resetting usb")
    #p = os.system("echo %s|sudo -S %s" % (sudoPassword, command))

def gphotoReset():
    out = check_output(["gphoto2","--reset"])
    sleep(0.5)
    
    
# normal output should have DSCF and JPG in it, and no mention of error.
# If not, it's an error
def detectErrorNeedingReset(inString):
    print("checking this string for presence of magic words:")
    print(inString)
    # if the word Error or error
    if ("is in location" in inString):
        return False
    return True
    

def takePicture():
    print("taking picture...")
    outString = "Error Error Error"
    try:
        print("before check_output")
        out = check_output(["gphoto2", "--capture-image-and-download"])
        print("output is:")
        outString = out.decode()
        print(outString)
    except:
        print("Exception! Trying to reset USB. One moment.")
        resetUSB()
        gphotoReset()
        deleteLocalImages()
        return 
    else:
        print("Nothing went wrong.")
        
    print("checking if return statement contained an error")
    errorNeedingResetOccurred = detectErrorNeedingReset(outString)
    if (errorNeedingResetOccurred):
        print("ERROR NEEDING RESET OCCURRED. ONE MOMENT.")
        resetUSB()
        gphotoReset()
        deleteLocalImages()
        return 
    
    fileName = extractFileNameFromGphotoOutput(out.decode())
    print(fileName)

    print("sending file to server")
    print(fileName)
    #send_data_to_server(fileName)
    
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
    
deleteLocalImages()
while True:
    #resetUSB()
    #gphotoReset()
    takePicture()
    
