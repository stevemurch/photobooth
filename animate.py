#animate.py

from tkinter import *
import time
import os
root = Tk()

maxFrames = 8

frames = [PhotoImage(file='sample.gif',format = 'gif -index %i' %(i)) for i in range(0, maxFrames)]

def update_wait_indicator(ind):
    if (ind==maxFrames):
        ind = 0
        root.after(0,update_wait_indicator, ind)
        return
    print(ind)
    frame = frames[ind]
    ind += 1
    print(ind)
    label.configure(image=frame)
    root.after(100, update_wait_indicator, ind)
    
label = Label(root)
label.pack()
root.after(0, update_wait_indicator, 0)
root.mainloop()