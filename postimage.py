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
    except:
        print("An exception occurred in upload")
         

#send_data_to_server('image2.jpg')
