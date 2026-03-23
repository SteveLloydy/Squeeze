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
BRIGHTNESS = 0.1       # Brightness (0.0 to 1.0)
ORDER = neopixel.GRB   # Color order for most WS2812 LEDs

print(f"Imported GPIO and NeoPixel on pin {LED_PIN} with {LED_COUNT} LEDs at brightness {BRIGHTNESS}")

adjustable_brightness = BRIGHTNESS

CLK = 10
DT = 9
SW = 11
SW2 = 7
CLK2 = 8
DT2 = 16
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(CLK2, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(DT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
print(f"Dial 1 setup complete, CLK={CLK}, DT={DT}, SW={SW}")
print(f"Dial 2 setup complete, CLK={CLK2}, DT={DT2}, SW={SW2}")

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
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

run_animation = False

# Background task function
def listen_for_switches():
    global run_animation
    global pixels
    global adjustable_brightness
    switchOn = True
    switch2On = True
    colorindex=0
    last_clk_state = GPIO.input(CLK)
    while True:
        if GPIO.input(SW) == GPIO.HIGH:
            if (switchOn):
                print("Switch SW Pressed!")
                switchOn = False
                run_animation = not run_animation            
        else:
            switchOn = True

        if GPIO.input(SW2) == GPIO.HIGH:
            if (switch2On):
                print("Switch 2 Pressed!")
                switchOn = False
                run_animation = False
                pixels.fill(colors[colorindex % len(colors)])
                time.sleep(0.5)
                pixels.show()
                colorindex += 1
        else:
            switch2On = True

        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)
        
		# Detect rotation        
        if clk_state != last_clk_state:
            print(f"Clock State 2 {clk_state}")
            print(f"DT State 2 {dt_state}")
            direction = "None"
            if clk_state == 1 and dt_state == 0:
                direction = "CW"  # Clockwise
                adjustable_brightness += 0.05
                pixels.brightness = adjustable_brightness
                pixels.show()
            elif clk_state == 0 and dt_state == 0:
                direction = "CCW"  # Counter-clockwise
                adjustable_brightness -= 0.05
                pixels.brightness = adjustable_brightness
                pixels.show()
            print(f"Direction 2:{direction}|Brightness 2:{adjustable_brightness}")
            last_clk_state = clk_state
        time.sleep(0.05)


        if clk_state != last_clk_state:
            print(f"Clock State {clk_state}")
            print(f"DT State {dt_state}")
            if dt_state != clk_state:
                direction = "CW"  # Clockwise
                adjustable_brightness += 0.05
                pixels.brightness = adjustable_brightness
                pixels.show()
            else:
                direction = "CCW"  # Counter-clockwise
                adjustable_brightness -= 0.05
                pixels.brightness = adjustable_brightness
                pixels.show()
            print(f"Direction:{direction}|Brightness:{adjustable_brightness}")
            last_clk_state = clk_state
        time.sleep(0.05)

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
        if (not run_animation):
            return
            
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

def rainbow_cycle(wait=0.02):
    """Draw rainbow that uniformly distributes across all pixels."""
    for j in range(255):
        for i in range(LED_COUNT):
            if (not run_animation):
                return
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
        time.sleep(0.1)
except KeyboardInterrupt:
    # Turn off LEDs on exit
    pixels.fill((0, 0, 0))
    pixels.show()
    run_animation = False
    while display_animation_thread.is_alive():
        print("Waiting for animation thread to finish...")        
        time.sleep(1)        
    GPIO.cleanup()
