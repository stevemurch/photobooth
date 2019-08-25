# PhotoBooth
# LED on BOARD PIN 13
# 
# wait for button press
#     count down 3..2..1
#     snap photo
#          move servo
#          move servo back
#          download image from camera
#     display image on screen
#     resize to 3Mb or less
#     tweet it
#     upload to Google Photos
#     delete image(s) from camera
#     delete image(s) from rPi

# arcade wait mode
#     

from tkinter import *
from time import sleep
import subprocess
from PIL import Image, ImageTk
import RPi.GPIO as GPIO

LED_BOARD_PIN = 13




def showButton():
    btn.lift()

def hideButton():
    btn.lower()

def updatePhoto():
    global img
    n=1
    same = True 
    
    path = "image2.jpg"
    image = Image.open(path)
    [imageSizeWidth, imageSizeHeight] = image.size
    newImageSizeWidth = int(imageSizeWidth*n)
    if same:
        newImageSizeHeight = int(imageSizeHeight*n)
    else:
        newImageSizeHeight = int(imageSizeHeight/n) 

    image = image.resize((newImageSizeWidth, newImageSizeHeight), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image)
    
    
    
    #print("updating image...")
    #global img
    #img = ImageTk.PhotoImage(Image.open("image2.jpg"))
    #resized = img.zoom(1000,500)
    
    canvas.create_image(10,10, anchor=NW, image=img) 
    canvas.grid(column=0,row=1)
    canvas.update()

def flashLightOn():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(LED_BOARD_PIN,GPIO.OUT)
    print("LED on")
    GPIO.output(LED_BOARD_PIN,GPIO.HIGH)



def flashLightOff():
    print("LED off")
    GPIO.output(LED_BOARD_PIN,GPIO.LOW)
    

def takePhoto():
    subprocess.Popen(["fswebcam", "-r","800x600","--no-banner", "image2.jpg"])
    lbl.configure(text="PHOTO SNAPPED!")

def playCameraSound():
    # requires mpg321 install first
    subprocess.Popen(["mpg321","camera.mp3"])
    

def countdown():
    hideButton()
    lbl.configure(text="3...")
    lbl.update()
    sleep(1)
    lbl.configure(text="2...")
    lbl.update()
    sleep(1)
    lbl.configure(text="1...")
    lbl.update()
    sleep(0.8)
    playCameraSound()
    lbl.configure(text="SNAP!")
    lbl.update()
    flashLightOn()
    takePhoto()
    sleep(0.25)
    flashLightOff()
    lbl.update()
    
    sleep(2)
    updatePhoto()
    lbl.configure(text="Press the button to take a photo!")
    lbl.update()
    

def clicked():
    btn.grid_remove()
    countdown()
    add_button()

def add_button():
    btn.grid(column=0, row=2)

root = Tk()
root.geometry('800x800')
root.title("Photo Booth")

lbl = Label(root, text="Press the button to take a photo!", font=("Arial Bold", 20))
lbl.grid(column=0, row=0)



canvas = Canvas(root, width = 800, height = 600) 
img = ImageTk.PhotoImage(Image.open("image.jpg"))      
canvas.create_image(0,0, anchor=CENTER, image=img) 
canvas.grid(column=0,row=1)

btn = Button(root, text="Take Photo", command=clicked)
btn.grid(column=0, row=2)

root.mainloop()
