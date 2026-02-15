#!/usr/bin/env python3
"""Listen to a button on GPIO26 and light an LED on GPIO17.

Wiring assumed (BCM numbering):
- Button between GPIO26 and GND (using internal pull-up)
- LED (with resistor) between GPIO17 and GND (LED anode -> GPIO17)

Run with sudo on Raspberry Pi: `sudo python3 led_control.py`
"""
import sys
import time
import argparse
from time import sleep

import RPi.GPIO as GPIO

CLK = 23
DT = 24
SW = 25
BTN = 26
LED = 17

print("Imported GPIO")
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.HIGH)

GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

GPIO.output(LED, GPIO.HIGH)
try:
	while True:
		if GPIO.input(BTN) == GPIO.HIGH:
			print("Button BTN Pressed!")
			GPIO.output(LED, GPIO.LOW)      
        
except KeyboardInterrupt:
	GPIO.cleanup()

print("Finished waiting")
sleep(10)

GPIO.output(LED, GPIO.LOW)

GPIO.cleanup()






