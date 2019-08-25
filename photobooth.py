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

def takePhoto():
	subprocess.Popen(["fswebcam", "-r","800x600", "image2.jpg"])
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

canvas = Canvas(root, width = 800, height = 600) 
img = ImageTk.PhotoImage(Image.open("image.jpg"))      
canvas.create_image(0,0, anchor=CENTER, image=img) 
canvas.grid(column=0,row=1)

root.mainloop()
