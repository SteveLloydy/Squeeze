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
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# Initial state
last_clk_state = GPIO.input(CLK)
last_dt_state = GPIO.input(DT)
counter = 0

def button_callback(channel):
    """Handle button press."""
    print("Button pressed! Counter reset to 0.")
    global counter
    counter = 0

# Detect falling edge on button press
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
	while True:
		if GPIO.input(26) == GPIO.HIGH:
			print("Button 26 Pressed!")
		if GPIO.input(25) == GPIO.HIGH:
			print("Button 25 Pressed!")

		clk_state = GPIO.input(CLK)
		dt_state = GPIO.input(DT)
	
        # Detect rotation
		if clk_state != last_clk_state:
			if dt_state != clk_state:
				counter += 1
				direction = "CW"  # Clockwise
		else:
			counter -= 1
			direction = "CCW"  # Counter-clockwise

	    print(f"Direction: {direction} | Counter: {counter}")
        last_clk_state = clk_state        
		print("looping")        
		input = GPIO.input(26)
		input2 = GPIO.input(25)
		print(input)
		time.sleep(0.05) # debounce delay
except KeyboardInterrupt:
	GPIO.cleanup()

print("Finished waiting")
sleep(10)

GPIO.output(LED, GPIO.LOW)

GPIO.cleanup()
