import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time  # Import time library for delays

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 18 to be an input pin and set initial value to be pulled low (off)

while True:  # Run forever
    pin_10_status = "HIGH" if GPIO.input(10) == GPIO.HIGH else "LOW"
    pin_18_status = "HIGH" if GPIO.input(18) == GPIO.HIGH else "LOW"
    print(f"Pin 10: {pin_10_status}, Pin 18: {pin_18_status}")
    time.sleep(0.5)  # Wait for 1/2 second