# 1.  Install Arduino and Teensyduino
## On Linux
 Go to https://www.arduino.cc/en/software/ and download the Arduino IDE AppImage

(Optional but recommended) In the Home directory, create an Applications folder and copy the Arduino IDE AppImage into this folder.

Make the AppImage executable and run it:
```shell
chmod a+x arduino-ide_xxx.AppImage
```

Go to https://www.pjrc.com/teensy/td_download.html and follow the instructions there to install Teensyduino.

TODO: Other OS
# 2. Load the Firmware
1. Make sure the rack containing the control module is powered and running.
2. Connect the control module via USB to the computer
3. Connect the control module via Ethernet to the local network.
4. Clone the git repository containing the firmware from https://github.com/lautaroleon/dbayfirmware
5. In the Arduino IDE, in the taskbar, select the board Teensy 4.1. Open the file *dbay_ctrlFW/dbay_ctrlFW.ino* found in the cloned firmware repository.  Then click *Upload* in the Arduino IDE's task bar. During the upload, you might be required to press the button on the Teensy.
6. If there aren't any errors in the Output log in the Arduino IDE, open *Tools>Serial Monitor* in the Arduino IDE. Wait for about 1min  and send the command *help*. If the firmware was loaded correctly, the message should start with ```-Available commands:```.  If the ethernet connection could be established, the answer to the *help* command states the IP address. It has to be different from 0.0.0.0.

# Troubleshooting
## The IP address is 0.0.0.0
TODO is this true?
This happens when there was no IP assigned to the Control Module. This can happen if the Control Module is directly connected to a computer instead of a network. Please connect the Control Module to the network and send the command *reset* via Serial Monitor. Check the IP again after the reset using the command *help*.