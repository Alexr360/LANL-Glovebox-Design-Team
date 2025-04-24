import RPi.GPIO as GPIO
import serial
import time

# ─── Configuration Constants ──────────────────────────────
# GPIO pin for counter-clockwise button
BUTTON_CCW = 10
# GPIO pin for clockwise button
BUTTON_CW = 11
# Motor drive speed
DRIVE_SPEED = 1
# Motor acceleration rate
ACCELERATION = 10
# Motor deceleration rate
DECELERATION = 25
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
    """
    print("Waiting for power-up packet. (10s)")
    start_time = time.time()
    while True:
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
        if time.time() - start_time > 10:  # Timeout after 10 seconds
            print("No power-up packet received within 10 seconds. Proceeding without it.")
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
    send_command(ser, f"JS{DRIVE_SPEED}")  # Set speed
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
            b2 = GPIO.input(BUTTON_CW) == GPIO.HIGH  # Check CW button state

            if not b1 and not b2 and last_command != "STOP":  # No buttons pressed
                stop_motor(ser)
                last_command = "STOP"
                print("┌───────────────────────────────────┐\n│ Stopped Jog                       │\n└───────────────────────────────────┘")
            elif b1 and b2:  # Both buttons pressed
                kill_buffer(ser)
                last_command = None
                print("┌───────────────────────────────────┐\n│ Stopped Jog and Killed Buffer     │\n└───────────────────────────────────┘")

            time.sleep(0.05)  # Small delay to reduce CPU usage

    except KeyboardInterrupt:
        # Handle user interrupt (Ctrl+C)
        print("\nInterrupted by user. Cleaning up...")
        GPIO.cleanup()
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")
    except serial.SerialException as e:
        # Handle serial communication errors
        print(f"Serial error: {e}")
    finally:
        # Cleanup GPIO and close serial connection on exit
        GPIO.cleanup()
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
