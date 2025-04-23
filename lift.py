import serial
import time

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
        if time.time() - start_time > 30:
            print("No power-up packet received within 30 seconds. Proceeding without it.")
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
    try:
        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1)
        wait_for_power_up(ser)
        time.sleep(3)
        # Now in SCL mode
        while True:
            print("\nEnter a command: ")
            print("1 = Clockwise")
            print("2 = Counterclockwise")
            print("3 = Stop")
            print("4 = Emergency Stop")
            print("q = Quit")
            choice = input("Choice: ").strip().lower()
            if choice == "1":
                send_command(ser, "JA10")
                send_command(ser, "JL25")
                send_command(ser, "JS5")
                send_command(ser, "DI1")
                send_command(ser, "CJ")
            elif choice == "2":
                send_command(ser, "JA10")
                send_command(ser, "JL25")
                send_command(ser, "JS0")
                send_command(ser, "DI-1")
                send_command(ser, "CJ")
            elif choice == "3":
                send_command(ser, "SJ")
            elif choice == "4":
                send_command(ser, "SK")
            elif choice == "q":
                print("Exiting program...")
                break
            else:
                print("Invalid input. Please enter 1, 2, 3, or q.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()