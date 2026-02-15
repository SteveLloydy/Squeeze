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

GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# Initial state
last_clk_state = GPIO.input(CLK)
last_dt_state = GPIO.input(DT)
counter = 0

print(f"Last Clock State {last_clk_state}")
print(f"Last DT State {last_dt_state}")
time.sleep(2)
try:
	while True:
		if GPIO.input(26) == GPIO.HIGH:
			print("Button BTN Pressed!")
		if GPIO.input(SW) == GPIO.HIGH:
			print("Button SW Pressed!")
        
		clk_state = GPIO.input(CLK)
		dt_state = GPIO.input(DT)
		print(f"Clock State {clk_state}")
		print(f"DT State {dt_state}")
		time.sleep(1)
        # Detect rotation
		if clk_state != last_clk_state:
			if dt_state != clk_state:
				counter += 1
				direction = "CW"  # Clockwise
		else:
			counter -= 1
			direction = "CCW"  # Counter-clockwise
		print(f"Direction:{direction}|Counter:{counter}")
		last_clk_state = clk_state
		time.sleep(1) # debounce delay            
        
except KeyboardInterrupt:
	GPIO.cleanup()

print("Finished waiting")
sleep(10)

GPIO.output(LED, GPIO.LOW)

GPIO.cleanup()




