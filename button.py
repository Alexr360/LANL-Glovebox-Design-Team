import serial
import time
import RPi.GPIO as GPIO

def wait_for_power_up(ser):
    print("Waiting for power-up packet... (power cycle the drive)")
    start_time = time.time()
    while True:
        if ser.in_waiting >= 3:
            packet = ser.read(3)
            if packet[0] == 0xFF:
                fw = packet[1]
                model = packet[2]
                print(f"Power-up packet received: FW 1.{fw}, Model {model}")
                time.sleep(0.005)
                ser.write(b'00')  # Send double-zero
                print("Sent double-zero to enter SCL mode.")
                break
        if time.time() - start_time > 10:
            print("No power-up packet received within 10 seconds. Proceeding without it.")
            break
        time.sleep(0.05)

def send_command(ser, command, expect_response=True):
    """Send SCL command with carriage return."""
    try:
        full_cmd = command + '\r'
        ser.reset_input_buffer()
        ser.write(full_cmd.encode('ascii'))
        print(f"Sent: {command}")
        if expect_response:
            time.sleep(0.1)
            response = ser.read_all().decode('ascii').strip()
            if response:
                print(f"Response: {response}")
            else:
                print("No response.")
    except Exception as e:
        print(f"Error sending command: {e}")

def main():
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    CCW_BUTTON = 10  # Button 1 pin
    CW_BUTTON = 11   # Button 2 pin
    GPIO.setup(CCW_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CW_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1)
        wait_for_power_up(ser)
        time.sleep(3)

        # Pre-configure jog parameters
        send_command(ser, "SJ")        # Stop any previous jog
        time.sleep(0.1)
        send_command(ser, "JA10")      # Jog acceleration
        send_command(ser, "JL25")      # Jog deceleration
        send_command(ser, "JS5")       # Jog speed

        last_state = None  # None, 'cw', or 'ccw'

        print("Waiting for button presses. CTRL+C to exit.")
        while True:
            ccw_pressed = GPIO.input(CCW_BUTTON)
            cw_pressed = GPIO.input(CW_BUTTON)

            if ccw_pressed and last_state != 'ccw':
                # Start counterclockwise jog
                send_command(ser, "SJ")
                time.sleep(0.1)
                send_command(ser, "DI-1")  # CCW direction
                send_command(ser, "CJ")
                last_state = 'ccw'

            elif cw_pressed and last_state != 'cw':
                # Start clockwise jog
                send_command(ser, "SJ")
                time.sleep(0.1)
                send_command(ser, "DI1")   # CW direction
                send_command(ser, "CJ")
                last_state = 'cw'

            elif not ccw_pressed and not cw_pressed and last_state is not None:
                # Stop jogging when no button pressed
                send_command(ser, "SJ")
                last_state = None

            time.sleep(0.05)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExit requested by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")
        GPIO.cleanup()
        print("GPIO cleaned up.")

if __name__ == "__main__":
    main()
