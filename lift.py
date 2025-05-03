import RPi.GPIO as GPIO
import serial
import time

# ─── Configuration Constants ──────────────────────────────
# GPIO pin for counter-clockwise button
BUTTON_CCW = 10
# GPIO pin for clockwise button
BUTTON_CW = 11
# Motor drive speed
UP_SPEED = 3
DOWN_SPEED = 3
# Motor acceleration rate
ACCELERATION = 0.5
# Motor deceleration rate
DECELERATION = 0.5
# Serial port for motor controller
SERIAL_PORT = "/dev/ttyUSB0"
# Baud rate for serial communication
BAUD_RATE = 9600
# Debounce time for button presses (in milliseconds)
DEBOUNCE_MS = 100

# ─── Setup ────────────────────────────────────────────────
# Disable GPIO warnings
GPIO.setwarnings(False)
# Set GPIO mode to BOARD
GPIO.setmode(GPIO.BOARD)
# Configure GPIO pins for buttons with pull-down resistors
GPIO.setup(BUTTON_CCW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_CW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def wait_for_power_up(ser):
    """
    Wait for the motor controller to send a power-up packet.
    If received, send a double-zero command to enter SCL mode.
    Also exit early if a button is pressed.
    """
    print("Waiting for power-up packet. (10s)")
    start_time = time.time()
    while True:
        # Check if a button is pressed to break out of wait early
        if GPIO.input(BUTTON_CCW) == GPIO.HIGH or GPIO.input(BUTTON_CW) == GPIO.HIGH:
            print("Button press detected. Skipping power-up wait.")
            break

        if ser.in_waiting >= 3:  # Check if at least 3 bytes are available
            packet = ser.read(3)
            if packet[0] == 0xFF:  # Check for power-up packet signature
                fw = packet[1]
                model = packet[2]
                print(f"Power-up packet received: FW 1.{fw}, Model {model}")
                time.sleep(0.005)
                ser.write(b'00')  # Send double-zero command
                print("Sent double-zero to enter SCL mode.")
                break

        if time.time() - start_time > 60:  # Timeout after 10 seconds
            print("No power-up packet received within 60 seconds. Proceeding without it.")
            break

        time.sleep(0.05)


def send_command(ser, command, expect_response=True):
    """
    Send a command to the motor controller via serial.
    Optionally check for a response and handle errors.
    """
    try:
        full_cmd = command + '\r'  # Append carriage return to command
        ser.reset_input_buffer()  # Clear input buffer
        ser.write(full_cmd.encode('ascii'))  # Send command
        if expect_response:
            time.sleep(0.1)  # Wait for response
            response = ser.read_all().decode('ascii').strip()
            if response == "?":  # Command not understood
                print(f"⚠ Drive did not understand command: {command}")
            elif response != "%" and response != "":  # Unexpected response
                print(f"⚠ Unexpected Response: {response}")
    except Exception as e:
        print(f"Error sending command: {e}")


def jog_motor(ser, direction):
    """
    Start jogging the motor in the specified direction (CW or CCW).
    """
    send_command(ser, "SJ")  # Stop any current jog
    send_command(ser, f"JA{ACCELERATION}")  # Set acceleration
    send_command(ser, f"JL{DECELERATION}")  # Set deceleration
    send_command(ser, f"JS{DOWN_SPEED if direction == 'CW' else UP_SPEED}")  # Set speed
    send_command(ser, f"DI{1 if direction == 'CW' else -1}")  # Set direction
    send_command(ser, "CJ")  # Start jog


def stop_motor(ser):
    """
    Stop the motor immediately.
    """
    send_command(ser, "SJ")  # Stop jog


def kill_buffer(ser):
    """
    Clear the command buffer on the motor controller.
    """
    send_command(ser, "SK")  # Kill buffer


def main():
    """
    Main function to initialize the system and handle button events.
    """
    try:
        print("┌───────────────────────────────────────┐\n│ Starting Up Please Wait               │\n└───────────────────────────────────────┘")
        # Open serial connection to motor controller
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        wait_for_power_up(ser)

        print("┌───────────────────────────────────────┐\n│ Startup Complete, Lift Ready for Use! │\n└───────────────────────────────────────┘")

        last_command = None  # Track the last command sent to avoid duplicates

        # Callback for counter-clockwise button press
        def on_ccw(channel):
            nonlocal last_command
            if last_command != "CCW":  # Avoid duplicate commands
                jog_motor(ser, "CCW")
                last_command = "CCW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Counter Clockwise    │\n└───────────────────────────────────┘")

        # Callback for clockwise button press
        def on_cw(channel):
            nonlocal last_command
            if last_command != "CW":  # Avoid duplicate commands
                jog_motor(ser, "CW")
                last_command = "CW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Clockwise            │\n└───────────────────────────────────┘")

        # Attach event listeners to buttons
        GPIO.add_event_detect(BUTTON_CCW, GPIO.RISING, callback=on_ccw, bouncetime=DEBOUNCE_MS)
        GPIO.add_event_detect(BUTTON_CW, GPIO.RISING, callback=on_cw, bouncetime=DEBOUNCE_MS)

        # Main loop to monitor button states
        while True:
            b1 = GPIO.input(BUTTON_CCW) == GPIO.HIGH  # Check CCW button state
            b2 = GPIO.inpu        jog_start_time = None  # Track when jogging starts

        while True:
            b1 = GPIO.input(BUTTON_CCW) == GPIO.HIGH  # CCW button state
            b2 = GPIO.input(BUTTON_CW) == GPIO.HIGH   # CW button state

            if b1 or b2:
                if jog_start_time is None:
                    jog_start_time = time.time()  # Start jogging timer
            else:
                jog_start_time = None  # Reset jogging timer if no button is pressed

            if not b1 and not b2 and last_command != "STOP":
                stop_motor(ser)
                last_command = "STOP"
                jog_start_time = None
                print("┌───────────────────────────────────┐\n│ Stopped Jog                       │\n└───────────────────────────────────┘")
            elif b1 and b2:
                kill_buffer(ser)
                last_command = None
                jog_start_time = None
                print("┌───────────────────────────────────┐\n│ Stopped Jog and Killed Buffer     │\n└───────────────────────────────────┘")
            elif jog_start_time and (time.time() - jog_start_time > 30):
                stop_motor(ser)
                last_command = "STOP"
                jog_start_time = None
                print("┌───────────────────────────────────┐\n│ Jog Timeout: Stopped after 30s    │\n└───────────────────────────────────┘")

            time.sleep(0.05)
            
            
if __name__ == "__main__":
    main()
