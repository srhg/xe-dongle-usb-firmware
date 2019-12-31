#!/usr/bin/env python3

import argparse
import sys
import time
import usb.core
import usb.util


CONTROL_REQ_GETMAGIC = 0
CONTROL_REQ_DEVICEMODE = 1

DEVICE_MODE_CDC = 0
DEVICE_MODE_AVRISP = 1
DEVICE_MODE_BOOTLOADER = 2


def get_dev():
    dev = usb.core.find(idVendor=0x3eb, idProduct=0x204a)
    if dev is None:
        dev = usb.core.find(idVendor=0x03eb, idProduct=0x204b)
    if dev is None:
        dev = usb.core.find(idVendor=0x03eb, idProduct=0x2104)
    return dev


def get_mode(dev):
    if dev.idProduct == 0x204b:
        return DEVICE_MODE_CDC
    
    if dev.idProduct == 0x2104:
        return DEVICE_MODE_AVRISP
    
    if dev.idProduct == 0x204a:
        return DEVICE_MODE_BOOTLOADER


def set_mode(dev, mode):
    if get_mode(dev) == mode:
        return

    if dev.idProduct == 0x204a:
        # leave bootloader mode
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        if dev.is_kernel_driver_active(1):
            dev.detach_kernel_driver(1)
        dev.write(4, 'E')
        assert(dev.read(0x83, 1).tobytes() == b'\r')
        time.sleep(3)

    dev = get_dev()
    assert(dev)
    magic = dev.ctrl_transfer(0xC0, CONTROL_REQ_GETMAGIC, 0, 0, 4).tobytes()
    assert(magic == b'srxe')

    dev.ctrl_transfer(0x40, CONTROL_REQ_DEVICEMODE, mode, 0, None)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--get-mode', action='store_true')
    group.add_argument('--set-mode', nargs='?')
    args = parser.parse_args()

    if args.get_mode:
        dev = get_dev()
        if not dev:
            print('No devices found', file=sys.stderr)
            return
        mode = get_mode(dev)
        if mode == DEVICE_MODE_CDC:
            print('CDC')
        elif mode == DEVICE_MODE_AVRISP:
            print('AVRISP')
        elif mode == DEVICE_MODE_BOOTLOADER:
            print('BOOTLOADER')

    if args.set_mode:
        mode_name = args.set_mode.upper()
        if mode_name == 'CDC':
            mode = DEVICE_MODE_CDC
        elif mode_name == 'AVRISP':
            mode = DEVICE_MODE_AVRISP
        elif mode_name == 'BOOTLOADER':
            mode = DEVICE_MODE_BOOTLOADER
        else:
            print('Unknown mode, must be one of CDC, AVRISP, or BOOTLOADER', file=sys.stderr)
            return
        
        dev = get_dev()
        if not dev:
            print('No devices found')
        set_mode(dev, mode)


if __name__ == '__main__':
    main()