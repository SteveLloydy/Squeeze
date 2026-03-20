#!/usr/bin/env python3
"""
NeoPixel control example for Linux (Tiny Core) using rpi_ws281x.
Tested with WS2812B LEDs.
"""

import time
import board
import threading
import time

import neopixel
import argparse
import RPi.GPIO as GPIO

# ====== CONFIGURATION ======
LED_COUNT = 24          # Number of NeoPixels
LED_PIN = board.D18    # GPIO pin (PWM-capable, e.g., GPIO18 on Raspberry Pi)
BRIGHTNESS = 0.8       # Brightness (0.0 to 1.0)
ORDER = neopixel.GRB   # Color order for most WS2812 LEDs

print(f"Imported GPIO and NeoPixel on pin {LED_PIN} with {LED_COUNT} LEDs at brightness {BRIGHTNESS}")

adjustable_brightness = 256 * BRIGHTNESS

CLK = 9
DT = 10
SW = 11

GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
print(f"GPIO setup complete, CLK={CLK}, DT={DT}, SW={SW}")

# ====== INITIALIZE ======
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

pixels.fill((0, 0, 0))
pixels.show()

# ====== MAIN LOOP ======
try:
    while True:
        pixels.fill((255, 0, 0))
        time.sleep(3)
        pixels.fill((0, 255, 0))
        time.sleep(3)
        pixels.fill((0, 0, 255))
        time.sleep(3)
except KeyboardInterrupt:
    # Turn off LEDs on exit
    print("KeyboardInterrupt received, stopping animation and cleaning up GPIO...")
    pixels.fill((0, 0, 0))
    pixels.show()
    GPIO.cleanup()
