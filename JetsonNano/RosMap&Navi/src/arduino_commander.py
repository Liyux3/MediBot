#!/usr/bin/env python

import serial
import time
import sys

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0' # Or whatever port your Arduino is on (use ls /dev/tty* to check)
BAUD_RATE = 115200

# --- Main Code ---
ser = None
print("--- Arduino Serial Commander ---")
print("Enter commands like 'W:0.5', 'A:0.2', 'S', etc.")
print("Type 'quit' or press Ctrl+C to exit.")
print("-" * 30)

try:
    # --- Connect to Serial Port ---
    print("Connecting to %s at %d baud..." % (SERIAL_PORT, BAUD_RATE))
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Wait for Arduino to reset after connection
    if ser.is_open:
        print("Connected successfully!")
    else:
        print("Failed to open serial port.")
        sys.exit(1)

    # --- Command Loop ---
    while True:
        try:
            # Get command from user
            command = raw_input("Enter command: ") # Use raw_input for Python 2
            command = command.strip() # Remove extra whitespace

            if command.lower() == 'quit':
                break

            if len(command) > 0:
                # Send command to Arduino (append newline)
                print("Sending: '%s'" % command)
                ser.write(command.encode('utf-8') + b'\n')
                ser.flush() # Ensure data is sent immediately

                # Optional: Read any response from Arduino
                # time.sleep(0.1) # Give Arduino time to respond
                # while ser.in_waiting > 0:
                #     response = ser.readline().decode('utf-8').strip()
                #     print("Arduino says: %s" % response)

            else:
                print("Empty command, not sending.")

        except EOFError: # Handle Ctrl+D
            print("\nExiting.")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            print("\nExiting.")
            break
        except serial.SerialException as e:
            print("\nSerial error: %s. Exiting." %e)
            break


except serial.SerialException as e:
    print("Error setting up serial port %s: %s" % (SERIAL_PORT, e))
except Exception as e:
    print("An unexpected error occurred: %s" % e)
finally:
    # --- Cleanup ---
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed.")
    print("Goodbye.")