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
LED_PIN = board.D12    # GPIO pin (PWM-capable, e.g., GPIO18 on Raspberry Pi)
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

# ====== INITIALIZE ======
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

run_animation = False

# Background task function
def listen_for_switches():
    global run_animation
    global pixels
    global adjustable_brightness
    switchOn = True
    last_clk_state = GPIO.input(CLK)
    while True:
        if GPIO.input(SW) == GPIO.HIGH:
            if (switchOn):
                print("Switch SW Pressed!")
                switchOn = False
                run_animation = not run_animation
        else:
            switchOn = True

        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)
        
		# Detect rotation
        if clk_state != last_clk_state:
            print(f"Clock State {clk_state}")
            print(f"Last Clock State {last_clk_state}")
            print(f"DT State {dt_state}")
            if dt_state != clk_state:
                direction = "CW"  # Clockwise
                adjustable_brightness += 5
                # pixels.setBrightness(adjustable_brightness)
                pixels.show()
            else:
                direction = "CCW"  # Counter-clockwise
                adjustable_brightness -= 5
                # pixels.setBrightness(adjustable_brightness)
                pixels.show()
            print(f"Direction:{direction}|Brightness:{adjustable_brightness}")
            last_clk_state = clk_state
        time.sleep(0.1)

def display_animation():
    while True:
        color_wipe((255, 0, 0))  # Red
        if (not run_animation):
            break
        color_wipe((0, 255, 0))  # Green
        if (not run_animation):
            break
        color_wipe((0, 0, 255))  # Blue
        if (not run_animation):
            break
        rainbow_cycle()
        if (not run_animation):
            break
    print("Animation stopped, turning off LEDs.")
    pixels.fill((0, 0, 0))
    pixels.show()
		
# Create and start a daemon thread
listen_for_switches_thread = threading.Thread(target=listen_for_switches, daemon=True)
listen_for_switches_thread.start()

def color_wipe(color, wait=0.05):
    """Fill the strip with a single color, one pixel at a time."""
    for i in range(LED_COUNT):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

def rainbow_cycle(wait=0.02):
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

display_animation_thread = threading.Thread(target=display_animation, daemon=True)

# ====== MAIN LOOP ======
try:
    while True:
        if run_animation and run_animation != last_run:
            if display_animation_thread.is_alive():
                display_animation_thread.join(timeout=5)
            display_animation_thread = threading.Thread(target=display_animation, daemon=True)
            display_animation_thread.start()        
           
        last_run = run_animation
        time.sleep(0.05)
except KeyboardInterrupt:
    # Turn off LEDs on exit
    pixels.fill((0, 0, 0))
    pixels.show()
    GPIO.cleanup()
