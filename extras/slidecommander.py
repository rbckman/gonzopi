import serial
import serial.tools.list_ports
import time

def list_serial_ports():
    # Get a list of all serial ports
    ports = serial.tools.list_ports.comports()
    # Print the available ports
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(f"{port.device} - {port.description}")
            return port.device

def listen_serial_port(serial_port):
    baud_rate = 57600# Set the baud rate according to your device
    # Create a serial connection
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {serial_port} at {baud_rate} baud.")
    except serial.SerialException as e:
        print(f"Error: {e}")
        exit()
    # Give some time for the connection to establish
    time.sleep(0)
    # Read data from the serial port
    try:
        while True:
            if ser.in_waiting > 0:  # Check if there is data waiting to be read
                received_data = ser.readline().decode('utf-8').strip()  # Read a line and decode
                print(f"Received: {received_data}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Close the serial connection
        ser.close()
        print("Serial connection closed.")

def send_serial_port(serial_port,msg):
    baud_rate = 57600       # Set the baud rate according to your device
    # Create a serial connection
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {serial_port} at {baud_rate} baud.")
    except serial.SerialException as e:
        print(f"Error: {e}")
        exit()

    # Give some time for the connection to establish

    # Write data to the serial port
    data_to_send = msg  # Add a newline if needed
    try:
        ser.write(data_to_send.encode('utf-8'))  # Encode the string to bytes
        print(f"Sent: {data_to_send.strip()}")
    except Exception as e:
        print(f"Error while sending data: {e}")

    # Close the serial connection
    ser.close()
    print("Serial connection closed.")

if __name__ == "__main__":
    port = list_serial_ports()
    while True:
        user_input = input("slidecommando: ")
        send_serial_port(port,user_input)

