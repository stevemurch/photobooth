# PhotoBooth
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

from Tkinter import *
from time import sleep
import subprocess
from PIL import Image, ImageTk

def showButton():
	btn.lift()

def hideButton():
	btn.lower()

def updatePhoto():
    print("updating image...")
    global img
    img = ImageTk.PhotoImage(Image.open("image2.jpg"))   
      
    canvas.create_image(10,10, anchor=CENTER, image=img) 
    canvas.grid(column=0,row=1)
    canvas.update()

def takePhoto():
	subprocess.Popen(["fswebcam", "-r","1600x800", "image2.jpg"])
	lbl.configure(text="PHOTO SNAPPED!")

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
    sleep(1)
    takePhoto()
    sleep(3)
    updatePhoto()

def clicked():
	btn.grid_remove()
	countdown()
	add_button()

def add_button():
	btn.grid(column=1, row=0)

root = Tk()
root.geometry('800x600')
root.title("Photo Booth")

lbl = Label(root, text="Press the button to take a photo!", font=("Arial Bold", 20))
lbl.grid(column=0, row=0)

btn = Button(root, text="Take Photo", command=clicked)
btn.grid(column=1, row=0)

canvas = Canvas(root, width = 600, height = 600) 
img = ImageTk.PhotoImage(Image.open("image.jpg"))      
canvas.create_image(10,10, anchor=CENTER, image=img) 
canvas.grid(column=0,row=1)

root.mainloop()
