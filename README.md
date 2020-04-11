# rpi-keyboard-emulator
Web interface for using a Raspberry Pi Zero W into a keyboard

Uses a Raspberry Pi Zero W (W is needed to display web interface while USB HID is connected.)

Display/keys: https://www.pishop.us/product/240x240-1-3inch-ips-lcd-display-hat-for-raspberry-pi/

Case STL: https://www.thingiverse.com/thing:3328994. This needs a bit of modification to work well.

### Setup
* To set up the display, follow parts of https://www.waveshare.com/wiki/Libraries_Installation_for_RPi:
  * The section "Install C Library bcm2835"
  * The section "Configuring the interfaces". Enable I2C, serial, and SPI.
* Check out source into ~/source.
* Add ~/source/enable_usb.sh and ~/source/main.py to /etc/rc.local (see below.)
* Add ~/source/main.py to /etc/rc.local.

##### /etc/rc.local
```
/home/pi/source/enable_usb.sh
/usr/bin/python3 /home/pi/source/main.py >/dev/null 2>&1 &

exit 0
```

### Reference
Initial inspiration: https://randomnerdtutorials.com/raspberry-pi-zero-usb-keyboard-hid/ and http://www.isticktoit.net/?p=1383

USB HID tables: https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf