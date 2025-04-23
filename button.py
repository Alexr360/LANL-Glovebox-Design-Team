import RPi.GPIO as GPIO
import time

# Define GPIO pins for buttons
button1 = 17
button2 = 27

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

while True:
    button1_status = "HIGH" if GPIO.input(button1) == GPIO.HIGH else "LOW"
    button2_status = "HIGH" if GPIO.input(button2) == GPIO.HIGH else "LOW"

    print(f"Button 1: {button1_status}, Button 2: {button2_status}")
    time.sleep(0.5)  # Wait for 1/2 second