import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time  # Import time library for delays

# Define GPIO pins for buttons
button1 = 10
button2 = 11

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 18 to be an input pin and set initial value to be pulled low (off)

while True:  # Run forever
    button1Status = GPIO.input(button1) == GPIO.HIGH
    button2Status = GPIO.input(button2) == GPIO.HIGH
    
    if button1Status and button2Status:  # If both buttons are pressed
        print("Both buttons pressed")

    elif button1Status:  # If button 1 is pressed
        print("Button 1 pressed")

    elif button2Status:  # If button 2 is pressed
        print("Button 2 pressed")
        
    else:
        print("No button pressed")
    time.sleep(0.1)