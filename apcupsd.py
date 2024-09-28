#!/bin/python3
import serial
import time
import subprocess

# Open Serial
ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, bytesize=8, parity='N', stopbits=1, timeout=1)
executed = False

while True:
    while True:
        # Send Command
        result = ser.write(b'QS\r')
        # Read UPS Status
        response = ser.read_until(b'\r').decode('ascii').strip()
        # If empty resend
        if len(response) != 0 :
            break
        print("retry...")
        time.sleep(0.1)

    # Parse Binary Data
    utilize = response.split()[3]
    flags = int(response[-8:], 2)

    # Excute Command
    power = int(utilize)*3.6    # MAX Power is 360W
    print("power: %.1fW"%power)
    print("flag: %s"%bin(flags)[2:].zfill(8))

    if flags & 0b10000000:
        # Power fail
        if not executed:
            executed = True
            print("power failed, switch to low power mode...")
            subprocess.call(['/usr/bin/cpupower','frequency-set','-u','1.6G'])
    else:
        # Power online
        if executed:
            executed = False
            print("power online.")
            subprocess.call(['/usr/bin/cpupower','frequency-set','-u','3.8G'])

    if flags & 0b00000001:
	# Toggle Beep
        print("toggling beep...")
        result = ser.write(b'Q\r')

    if flags & 0b01000000:
	# Perform hibernate
        print("low power, ready to hibernate...")
        subprocess.call(['/usr/bin/cpupower','frequency-set','-u','3.4G'])
        subprocess.call(['/usr/bin/systemctl','hibernate'])

    # Wait for 5 seconds
    time.sleep(5)
