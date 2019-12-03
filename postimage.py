# postimage.py

# My version of the Photo Booth posts to a back-end Internet service I created called popsee.com, 
# which lets users review the photos taken, get a download link via SMS, and allows admins 
# to create a big-screen slideshow of the photos "favorited" by the admin. 
# 
# At this writing, I'm not making popsee.com available for public use, but if you've got a special use-case, 
# jot me a note. Jot me a note at @stevemur on Twitter. 

# Change the functions here to post to YOUR own endpoint(s). You could upload to Google Photos or 
# tweet out the photos via Twitter for instance. 

import requests
import os
from secret import *
import aiohttp
import json 
from threading import Thread


def send_data_to_server_async(image_path):
    t = Thread(target=send_data_to_server, args=(image_path,))
    t.start()
    return "Queued"


def send_data_to_server(image_path):
    try:
        image_filename = os.path.basename(image_path)
        multipart_form_data = {'file': (image_filename, open(image_path, 'rb'))}
        response = requests.post(postImageUrl, files=multipart_form_data)
        print(response.text)
        print(response.status_code)
        update_status(albumCode, "Uploaded with status code "+str(response.status_code))
        
        print("response code from server is:")
        print(json_response)
        return response.text 
    except:
        #update_status(albumCode, "An exception occurred in upload!")
        print("An exception occurred in upload")
        #parsed = json.loads(response.content)
        #print (parsed)
        return "Error"

def update_status(code, message):
    try:
        response = requests.post(statusUrl, json={"code": code, "message":message })
        print(response.text)
        print(response.status_code)
        return response.text 
    except:
        print("An exception occurred in posting status")
        #return "Error"
        
async def send_file(image_path):
   url = postImageUrl
   async with aiohttp.ClientSession() as session:
      _url = postImageUrl
      async with  session.post(url, data ={
            'url': postImageUrl,
            'file': open(image_path, 'rb')
      }) as response:
            data = await response.text()
            print (data)
