Setup and install

* On any SD card greater than 32gb, be sure to format as FAT, not ExFAT, or else your Rpi won't boot.

* Install Raspbian

* Install updates and WAIT for full completion of updates, 
  (or else next step will fail)

* Install gphoto2 with script found here:
  https://github.com/gonzalo/gphoto2-updater

* cd /home/pi/Desktop

* git clone https://github.com/stevemurch/photobooth

* Install usbreset (that's installed by default actually with git pull)

* Ensure that the gphoto2 volume monitor doesn't get run, because
  this interferes with the claiming of USB:

  run this at a terminal:
  sudo chmod 644 /usr/lib/gvfs/gvfs-gphoto2-volume-monitor 



