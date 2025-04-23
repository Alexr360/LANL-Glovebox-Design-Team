import RPi.GPIO as GPIO
import serial
import time

# ─── Configuration Constants ──────────────────────────────
BUTTON_CCW = 10
BUTTON_CW = 11
DRIVE_SPEED = 10
ACCELERATION = 10
DECELERATION = 25
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
DEBOUNCE_MS = 100

# ─── Setup ────────────────────────────────────────────────
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON_CCW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_CW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def wait_for_power_up(ser):
    print("Waiting for power-up packet. (10s)")
    start_time = time.time()
    while True:
        if ser.in_waiting >= 3:
            packet = ser.read(3)
            if packet[0] == 0xFF:
                fw = packet[1]
                model = packet[2]
                print(f"Power-up packet received: FW 1.{fw}, Model {model}")
                time.sleep(0.005)
                ser.write(b'00')
                print("Sent double-zero to enter SCL mode.")
                break
        if time.time() - start_time > 10:
            print("No power-up packet received within 10 seconds. Proceeding without it.")
            break
        time.sleep(0.05)


def send_command(ser, command, expect_response=True):
    try:
        full_cmd = command + '\r'
        ser.reset_input_buffer()
        ser.write(full_cmd.encode('ascii'))
        if expect_response:
            time.sleep(0.1)
            response = ser.read_all().decode('ascii').strip()
            if response == "?":
                print(f"⚠ Drive did not understand command: {command}")
            elif response != "%" and response != "":
                print(f"⚠ Unexpected Response: {response}")
    except Exception as e:
        print(f"Error sending command: {e}")


def jog_motor(ser, direction):
    send_command(ser, "SJ")
    send_command(ser, f"JA{ACCELERATION}")
    send_command(ser, f"JL{DECELERATION}")
    send_command(ser, f"JS{DRIVE_SPEED}")
    send_command(ser, f"DI{1 if direction == 'CW' else -1}")
    send_command(ser, "CJ")


def stop_motor(ser):
    send_command(ser, "SJ")


def kill_buffer(ser):
    send_command(ser, "SK")


def main():
    try:
        print("┌───────────────────────────────────────┐\n│ Starting Up Please Wait               │\n└───────────────────────────────────────┘")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        wait_for_power_up(ser)

        print("┌───────────────────────────────────────┐\n│ Startup Complete, Lift Ready for Use! │\n└───────────────────────────────────────┘")

        last_command = None

        def on_ccw(channel):
            nonlocal last_command
            if last_command != "CCW":
                jog_motor(ser, "CCW")
                last_command = "CCW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Counter Clockwise    │\n└───────────────────────────────────┘")

        def on_cw(channel):
            nonlocal last_command
            if last_command != "CW":
                jog_motor(ser, "CW")
                last_command = "CW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Clockwise            │\n└───────────────────────────────────┘")

        GPIO.add_event_detect(BUTTON_CCW, GPIO.RISING, callback=on_ccw, bouncetime=DEBOUNCE_MS)
        GPIO.add_event_detect(BUTTON_CW, GPIO.RISING, callback=on_cw, bouncetime=DEBOUNCE_MS)

        while True:
            b1 = GPIO.input(BUTTON_CCW) == GPIO.HIGH
            b2 = GPIO.input(BUTTON_CW) == GPIO.HIGH

            if not b1 and not b2 and last_command != "STOP":
                stop_motor(ser)
                last_command = "STOP"
                print("┌───────────────────────────────────┐\n│ Stopped Jog                       │\n└───────────────────────────────────┘")
            elif b1 and b2:
                kill_buffer(ser)
                last_command = None
                print("┌───────────────────────────────────┐\n│ Stopped Jog and Killed Buffer     │\n└───────────────────────────────────┘")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Cleaning up...")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        GPIO.cleanup()
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
