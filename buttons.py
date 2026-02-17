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

try:
	import paho.mqtt.client as mqtt
except Exception as exc:
	print("paho-mqtt not available. Install with: pip3 install paho-mqtt")
	raise SystemExit(1) from exc

# MQTT configuration
MQTT_BROKER = "192.168.0.157"
MQTT_PORT = 1883
MQTT_TOPIC = "encoder/rotation"	

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

SW = 25
BTN = 26
LED = 17

print("Imported GPIO")
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.HIGH)

GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# Initial state
counter = 0

GPIO.output(LED, GPIO.HIGH)
try:
	while True:
		if GPIO.input(BTN) == GPIO.HIGH:
			print("Button BTN Pressed!")
			GPIO.output(LED, GPIO.LOW)
			
		if GPIO.input(SW) == GPIO.HIGH:
			print("Button SW Pressed!") 
			GPIO.output(LED, GPIO.HIGH)    
		
		time.sleep(0.0001) # debounce delay    
        
except KeyboardInterrupt:
	GPIO.cleanup()

print("Finished waiting")
sleep(10)

GPIO.output(LED, GPIO.LOW)

GPIO.cleanup()






