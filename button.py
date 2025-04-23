import RPi.GPIO as GPIO
import time

# Use Broadcom pin-numbering scheme
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins your buttons are connected to
BUTTON1_PIN = 17  # e.g. physical pin 11
BUTTON2_PIN = 27  # e.g. physical pin 13

# Set up each pin as an input with an internal pull-down resistor
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Callback functions for each button
def button1_callback(channel):
    print("Button 1 pressed!")

def button2_callback(channel):
    print("Button 2 pressed!")

# Add event detection on rising edge (button press)
GPIO.add_event_detect(BUTTON1_PIN, GPIO.RISING, callback=button1_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON2_PIN, GPIO.RISING, callback=button2_callback, bouncetime=200)

try:
    print("Waiting for button presses. Press Ctrl+C to exit.")
    # Keep the script running
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting cleanly.")

finally:
    GPIO.cleanup()
