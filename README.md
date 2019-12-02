# photobooth
Simple Photobooth with RaspberryPi

Created for a party, not a commercial project. 

Entry point: photobooth.py

*WARNING!*: The code, by design, deletes all JPG images on your camera's SD card at startup. This is done to speed up the capture-and-download process and ensure that the only images on the camera are ones taken at the photo booth. 

I've written a short explainer, along with a short demo video, here: 
https://www.stevemurch.com/build-a-photo-booth-for-your-next-party/2019/12

This code was written for a Fuji X-T2, which by default names its photos DSC_____.JPG You may need to adjust some of the code within (search for "DSC") if your camera has a different naming convention. The Photo Transfer Protocol (PTP) implementation in Fuji cameras and/or the libgphoto2 library are relatively flaky. So various "double-check" hacks are used to verify if the photo is retrieved properly from the camera, and if not, it takes a series of steps to reset the USB bus. The kiosk is designed to run unattended, and it goes into a re-cycle mode after X number of failures. I still have quite a bit of refactoring and cleanup to do. Sharing here in hopes that it inspires a build of your own.
