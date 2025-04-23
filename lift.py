import RPi.GPIO as GPIO
import serial
import time

# Define GPIO pins for buttons
button1 = 10  # CCW
button2 = 11  # CW

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
                ser.write(b'00')  # Send double-zero
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
            if response != "%":
                print(f"Unexpected Response: {response}")
    except Exception as e:
        print(f"Error sending command: {e}")


def main():
    try:
        print("┌───────────────────────────────────────┐\n│ Starting Up Please Wait               │\n└───────────────────────────────────────┘")
        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1)
        wait_for_power_up(ser)

        time.sleep(0.1)
        print("┌───────────────────────────────────────┐\n│ Startup Complete, Lift Ready for Use! │\n└───────────────────────────────────────┘")

        last_command = None
        # Continuously read buttons and jog motor accordingly
        while True:
            b1 = GPIO.input(button1) == GPIO.HIGH
            b2 = GPIO.input(button2) == GPIO.HIGH

            if b1 and not b2 and last_command != "CCW":
                # Button1 pressed: Jog CCW
                send_command(ser, "SJ")
                send_command(ser, "JA10")
                send_command(ser, "JL25")
                send_command(ser, "JS5")
                send_command(ser, "DI-1")
                send_command(ser, "CJ")
                last_command = "CCW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Counter Clockwise    │\n└───────────────────────────────────┘")

            elif b2 and not b1 and last_command != "CW":
                # Button2 pressed: Jog CW
                send_command(ser, "SJ")
                send_command(ser, "JA10")
                send_command(ser, "JL25")
                send_command(ser, "JS5")
                send_command(ser, "DI1")
                send_command(ser, "CJ")
                last_command = "CW"
                print("┌───────────────────────────────────┐\n│ Started Jog: Clockwise            │\n└───────────────────────────────────┘")

            elif not b1 and not b2:
                # No buttons: Stop jogging
                send_command(ser, "SJ")
                last_command = "STOP"
                if last_command != "STOP":
                    print("┌───────────────────────────────────┐\n│ Stopped Jog                       │\n└───────────────────────────────────┘")
                time.sleep(0.1)

            elif b1 and b2:
                # Both buttons: Stop and kill buffer
                send_command(ser, "SK")
                last_command = None
                print("┌───────────────────────────────────┐\n│ Stopped Jog and Killed Buffer     │\n└───────────────────────────────────┘")
                time.sleep(0.1)



    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
