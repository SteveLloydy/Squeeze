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

try:
	from gpiozero import LED, Button, RotaryEncoder
except Exception as exc:
	print("gpiozero not available: this script must run on a Raspberry Pi with gpiozero installed.")
	print("Install with: pip3 install gpiozero")
	raise SystemExit(1) from exc

try:
	import paho.mqtt.client as mqtt
except Exception as exc:
	print("paho-mqtt not available. Install with: pip3 install paho-mqtt")
	raise SystemExit(1) from exc

import RPi.GPIO as GPIO

BUTTON_PIN = 26
LED_PIN = 17
BOUNCE_MS = 0.05  # debounce in seconds

# Rotary encoder pins (BCM)
ENCODER_CLK = 23
ENCODER_DT = 24

# MQTT configuration
MQTT_BROKER = "192.168.0.157"
MQTT_PORT = 1883
MQTT_TOPIC = "encoder/rotation"


def main(argv=None):
	parser = argparse.ArgumentParser(description="Button -> LED control for Raspberry Pi")
	parser.add_argument("--debug", action="store_true", help="Wait for debugger to attach (debugpy on port 5678)")
	args = parser.parse_args(argv)
	
	if args.debug:
		try:
			import debugpy
			print("Debug mode: listening on 0.0.0.0:5678, waiting for client to attach...")
			debugpy.listen(("0.0.0.0", 5678))
			debugpy.wait_for_client()
			print("Debugger attached")
		except Exception:
			print("debugpy not available in the environment. Install debugpy in your venv to use --debug.")
	
	try:
		# Initialize MQTT client with updated callback API
		mqtt_client = mqtt.Client()
		print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
		try:
			mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
			mqtt_client.loop_start()
			print("MQTT connected")
		except Exception as e:
			print(f"Failed to connect to MQTT broker: {e}")
			mqtt_client = None
		
		led = LED(LED_PIN)
		led.on()
		print("LED Loaded")
		button = Button(BUTTON_PIN)
		print("Button Loaded")
		rbutton = Button(25)
		print("Button Loaded")
		
		encoder = RotaryEncoder(ENCODER_DT,ENCODER_CLK)

		def on_rotated_clockwise():
			print("Rotated clockwise")
		
		def on_rotated_antclockwise():
			print("Rotated anti-clockwise")

		encoder.when_rotated_clockwise = on_rotated_clockwise 
		encoder.when_rotated_counter_clockwise = on_rotated_antclockwise
			
		
		# Set up event handlers
		def on_button_pressed():
			print("Button pressed")
			led.on()
			
		button.when_pressed = on_button_pressed
		rbutton.when_pressed = on_button_pressed
		button.when_released = led.off
		rbutton.when_released = led.off
		# encoder_clk.when_pressed = on_encoder_change
		# encoder_clk.when_released = on_encoder_change
		
		# Ensure LED follows current button state at start
		if button.is_pressed:
			led.on()
		else:
			led.off()
	except Exception as e:
		print(f"Failed to initialize GPIO: {e}")
		print("This script requires:")
		print("  1. Run on Raspberry Pi hardware with GPIO")
		print("  2. Run with sudo: sudo python3 led_control.py")
		raise SystemExit(1) from e

	try:
		print(f"Listening: button GPIO{BUTTON_PIN} -> LED GPIO{LED_PIN}. Press Ctrl+C to exit.")
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass
	finally:
		led.off()
		if mqtt_client:
			mqtt_client.loop_stop()
			mqtt_client.disconnect()


if __name__ == "__main__":
	main()
























