import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time  # Import time library for delays

# Define GPIO pins for buttons
button1 = 11
button2 = 23

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 18 to be an input pin and set initial value to be pulled low (off)

while True:  # Run forever
    pin_10_status = "HIGH" if GPIO.input(button1) == GPIO.HIGH else "LOW"
    pin_18_status = "HIGH" if GPIO.input(button2) == GPIO.HIGH else "LOW"
    print(f"Button 1: {pin_10_status}, Button 2: {pin_18_status}")
    time.sleep(0.5)  # Wait for 1/2 second