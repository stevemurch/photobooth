# postimage.py

import requests
import os

 
def send_data_to_server(image_path):
 
    try:
        image_filename = os.path.basename(image_path)
        multipart_form_data = {
        'file': (image_filename, open(image_path, 'rb'))
        }
        response = requests.post('https://chatsparkapi.azurewebsites.net/api/album/heather/image',
                             
                             files=multipart_form_data)
        print(response.text)
        print(response.status_code)
        return response.text 
    except:
        update_status("heather","An exception occurred in upload: "+response.text)

        print("An exception occurred in upload")
        return "Error"

def update_status(code, message):
 
    try:
        
        response = requests.post('https://chatsparkapi.azurewebsites.net/api/album/heather/status',
                             json={"code": code, "message":message})
        print(response.text)
        print(response.status_code)
        return response.text 
    except:
        print("An exception occurred in posting status")
        #return "Error"