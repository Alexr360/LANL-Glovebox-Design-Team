# Portable Single-Person Lift for LANL Glove Boxes

## Project Objective

The goal of this project is to design and implement a portable single-person lift capable of elevating individuals 4’10’’ or taller to a comfortable working height for Los Alamos National Laboratory's (LANL) glove boxes. This lift is intended to improve ergonomics and efficiency for operators working with glove boxes.

## Features

- **Jog Control**: The lift can be controlled using two physical buttons:
    - **Clockwise (CW)** button for upward movement.
    - **Counter-Clockwise (CCW)** button for downward movement.
- **Safety Mechanisms**:
    - Debounced button inputs to prevent accidental multiple activations.
    - Automatic motor stop when no buttons are pressed.
    - Buffer clearing to ensure safe operation when both buttons are pressed simultaneously.
- **Serial Communication**:
    - Communicates with the motor controller via a serial interface.
    - Sends commands to control motor speed, direction, and other parameters.
- **Startup Sequence**:
    - Waits for a power-up packet from the motor controller.
    - Sends initialization commands to enter the appropriate control mode.

## Hardware Requirements

- **Raspberry Pi**: Used for controlling the lift and interfacing with the motor controller.
- **Motor Controller**: Communicates with the Raspberry Pi via a serial connection.
- **Buttons**: Two physical buttons for controlling the lift's movement.
- **Lift Mechanism**: A motorized system capable of lifting a person to the desired height.

## Software Overview

The software is implemented in Python and uses the following libraries:
- `RPi.GPIO`: For interfacing with the physical buttons.
- `pySerial`: For communicating with the motor controller.
- `time`: For handling delays and timing operations.

### Key Functions

- **`wait_for_power_up(ser)`**: Waits for a power-up packet from the motor controller and initializes the system.
- **`send_command(ser, command, expect_response=True)`**: Sends a command to the motor controller and optionally handles the response.
- **`jog_motor(ser, direction)`**: Starts the motor in the specified direction (CW or CCW).
- **`stop_motor(ser)`**: Stops the motor.
- **`kill_buffer(ser)`**: Clears the motor controller's command buffer.

### Main Program Flow

1. Initializes the GPIO pins and serial connection.
2. Waits for the motor controller to send a power-up packet for 10 seconds.
3. Sets up event listeners for the CW and CCW buttons.
4. Continuously monitors button states to control the motor:
     - Starts jogging in the appropriate direction when a button is pressed.
     - Stops the motor when no buttons are pressed.
     - Clears the buffer if both buttons are pressed simultaneously.

## How to Run

1. Connect the Raspberry Pi to the motor controller via the specified serial port (`/dev/ttyUSB0`).
2. Wire the CW and CCW buttons to the appropriate GPIO pins (`BUTTON_CW` and `BUTTON_CCW`).
3. Power on the system and run the Python script.

## Possible Bugs

- If you get the GPIO busy command, it is likely that the Python program is already running in the background.  
    Run `pkill -f lift.py` and then re-run the Python program.
- If the motor is not responding at all, try unplugging only the motor controller, waiting a minute, and plugging it back in.