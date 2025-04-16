import serial
import time
import RPi.GPIO as GPIO

# GPIO Pin Definitions
UP_BUTTON = 17
DOWN_BUTTON = 27
UPPER_LIMIT = 22
LOWER_LIMIT = 23

# Motor Controller Commands
CMD_SET_SLOW_SPEED = "VE5"
CMD_MOVE_DOWN = "FL1"
CMD_SET_LIMITS = "DL"
CMD_STOP = "ST"
CMD_SET_FAST_SPEED = "VE20"
CMD_MOVE_UP = "DI48000"
CMD_MOVE_DOWN_STEPS = "DI-48000"

# Serial communication setup
try:
    ser = serial.Serial("/dev/serial0", 9600, timeout=1)  # Adjust for your port
except serial.SerialException as e:
    print(f"Error initializing serial communication: {e}")
    exit(1)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(UP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOWN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(UPPER_LIMIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LOWER_LIMIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def send_command(command):
    try:
        ser.write((command + "\r").encode())  # Send command to motor controller
        time.sleep(0.1)
        response = ser.readline().decode().strip()
        print(f"Response: {response}")
    except serial.SerialException as e:
        print(f"Error sending command '{command}': {e}")

def cleanup():
    """Cleanup GPIO and serial resources."""
    GPIO.cleanup()
    ser.close()
    print("Resources cleaned up.")

# Main logic
try:
    # Step 1: Move down slowly until Lower Limit is triggered
    send_command(CMD_SET_SLOW_SPEED)  # Set slow speed
    send_command(CMD_MOVE_DOWN)  # Move downward to limit switch

    # Step 2: Define Limits (Use controller commands)
    send_command(CMD_SET_LIMITS)  # Set software limits

    while True:
        up_pressed = not GPIO.input(UP_BUTTON)
        down_pressed = not GPIO.input(DOWN_BUTTON)
        upper_limit = not GPIO.input(UPPER_LIMIT)
        lower_limit = not GPIO.input(LOWER_LIMIT)

        # Step 3: Stop motor if both buttons are pressed or not pressed
        if (up_pressed and down_pressed) or (not up_pressed and not down_pressed):
            send_command(CMD_STOP)

        # Step 4: Move Up if Up Button is pressed and Upper Limit is NOT reached
        elif up_pressed and not upper_limit:
            send_command(CMD_SET_FAST_SPEED)  # Set speed
            send_command(CMD_MOVE_UP)  # Move up by steps

        # Step 5: Move Down if Down Button is pressed and Lower Limit is NOT reached
        elif down_pressed and not lower_limit:
            send_command(CMD_SET_FAST_SPEED)
            send_command(CMD_MOVE_DOWN_STEPS)  # Move down by steps

        # Step 6: Stop Motor if any limit switch is triggered
        if upper_limit or lower_limit:
            send_command(CMD_STOP)

        time.sleep(0.1)  # Add a small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    cleanup()