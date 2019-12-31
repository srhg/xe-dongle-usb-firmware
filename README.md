# xe-dongle-usb-firmware
Mode switching USB firmware for the Smart Response XE dongle.


Example command to flash firmware

$`avrdude -c avr109 -p m16u2 -P /dev/ttyACM0 -v -U flash:w:firmware.bin`
