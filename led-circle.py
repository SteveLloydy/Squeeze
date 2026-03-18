#!/usr/bin/env python3
"""
NeoPixel control example for Linux (Tiny Core) using rpi_ws281x.
Tested with WS2812B LEDs.
"""

import time
import board
import neopixel

# ====== CONFIGURATION ======
LED_COUNT = 24          # Number of NeoPixels
LED_PIN = board.D18    # GPIO pin (PWM-capable, e.g., GPIO18 on Raspberry Pi)
BRIGHTNESS = 0.8       # Brightness (0.0 to 1.0)
ORDER = neopixel.GRB   # Color order for most WS2812 LEDs

# ====== INITIALIZE ======
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

def color_wipe(color, wait=0.5):
    """Fill the strip with a single color, one pixel at a time."""
    for i in range(LED_COUNT):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

def rainbow_cycle(wait=0.2):
    """Draw rainbow that uniformly distributes across all pixels."""
    for j in range(255):
        for i in range(LED_COUNT):
            pixel_index = (i * 256 // LED_COUNT) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

# ====== MAIN LOOP ======
try:
    print ("running")
    while True:
        print ("looping")
        color_wipe((255, 0, 0))  # Red
        color_wipe((0, 255, 0))  # Green
        color_wipe((0, 0, 255))  # Blue
        rainbow_cycle()
except KeyboardInterrupt:
    # Turn off LEDs on exit
    pixels.fill((0, 0, 0))
    pixels.show()
