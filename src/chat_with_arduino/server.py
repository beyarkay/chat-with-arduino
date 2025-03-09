from enum import Enum
from mcp.server.fastmcp import FastMCP
from typing import Any, Union, Tuple
import httpx
import json
import mcp
import os
import serial
import serial.tools.list_ports
import subprocess

# Initialize FastMCP server
my_mcp = FastMCP("chat-with-arduino")


SERIAL_PORT = None

SERIAL_PORT_NC_MESSAGE = (
    'Serial Port not connected, use `list_devices()` to view the '
    'available devices and `connect_to_arduino` to connect via '
    'serial port to an arduino'
)

START_OF_MESSAGE = 0xFE
END_OF_MESSAGE = 0xFF

class TctlmIds(Enum):
    ERR = 0
    ACK = 1
    DIGITAL_READ = 2
    DIGITAL_WRITE = 3
    PIN_MODE = 4
    ANALOG_READ = 5
    ANALOG_WRITE = 6
    DELAY = 7
    MILLIS = 8

@my_mcp.tool()
async def ack() -> Union[bool, str]:
    """Request an acknowledgement from the arduino. Useful for checking that
    it's got power and has the Chat With Arduino firmware loaded.

    Arguments: None

    Returns: (True or False indicating whether the arduino replied correctly
    to the ACK), or a stringified error message if there was an exception or
    something went wrong
    """
    global SERIAL_PORT
    try:
        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.ACK.value, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        return list(reply) == [START_OF_MESSAGE, TctlmIds.ACK.value, END_OF_MESSAGE]

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def digital_read(pin: int) -> Union[bool, str]:
    """Reads the state of a digital pin.

    Arguments:
        pin (int): The pin number to read (0-255).

    Returns:
        (bool) True for HIGH, False for LOW, or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= pin <= 255, f"Pin must be in range 0-255, but was {pin}"

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.DIGITAL_READ.value, pin, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 4, "Expected reply to be 4 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, "Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.DIGITAL_READ.value, "Expected reply[1] to be TctlmIds.DIGITAL_READ {TctlmIds.DIGITAL_READ.value}, but was {reply[1]}"
        assert reply[3] == END_OF_MESSAGE, "Expected reply[3] to be end of message {END_OF_MESSAGE}, but was {reply[3]}"
        assert reply[2] in (0, 1), f"Expected reply[2] to be 0 or 1, but was {reply[2]}"

        return bool(reply[2])  # Convert 0/1 to False/True

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def digital_write(pin: int, state: int) -> Union[None, str]:
    """Writes a state to a digital pin.

    Arguments:
        pin (int): The pin number to write to (0-255).
        state (int): The state to write (0 for LOW, 1 for HIGH).

    Returns:
        None if successful, or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= pin <= 255, f"Pin must be in range 0-255, but was {pin}"
        assert state in (0, 1), f"State must be 0 (LOW) or 1 (HIGH), but was {state}"

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.DIGITAL_WRITE.value, pin, state, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 3, f"Expected reply to be 3 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.DIGITAL_WRITE.value, f"Expected reply[1] to be TctlmIds.DIGITAL_WRITE {TctlmIds.DIGITAL_WRITE.value}, but was {reply[1]}"
        assert reply[2] == END_OF_MESSAGE, f"Expected reply[2] to be end of message {END_OF_MESSAGE}, but was {reply[2]}"

        return None  # Success

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def pin_mode(pin: int, mode: str) -> Union[None, str]:
    """Defines the mode of a pin. This can only be set once before the Arduino
    needs to be reset and should be set before using the pin.

    Arguments:
        pin (int): The pin number to set the mode for (0-255).
        mode (str): The mode to set for the pin. Available modes are:
            'INPUT', 'OUTPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'OUTPUT_OPENDRAIN'.

    Returns:
        None if successful, or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= pin <= 255, f"Pin must be in range 0-255, but was {pin}"

        mode_map = {
            'INPUT': 0,
            'OUTPUT': 1,
            'INPUT_PULLUP': 2,
            'INPUT_PULLDOWN': 3,
            'OUTPUT_OPENDRAIN': 4
        }

        assert mode in mode_map, f"Invalid mode '{mode}'. Available modes are 'INPUT', 'OUTPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'OUTPUT_OPENDRAIN'."

        mode_value = mode_map[mode]

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.PIN_MODE.value, pin, mode_value, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 3, f"Expected reply to be 3 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.PIN_MODE.value, f"Expected reply[1] to be TctlmIds.PIN_MODE {TctlmIds.PIN_MODE.value}, but was {reply[1]}"
        assert reply[2] == END_OF_MESSAGE, f"Expected reply[2] to be end of message {END_OF_MESSAGE}, but was {reply[2]}"

        return None  # Success

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def analog_read(pin: int) -> Union[int, str]:
    """Reads the value of an analog pin in 10-bit resolution (0-1023).

    Arguments:
        pin (int): The pin number to read from (0-255).

    Returns:
        (int) The analog reading (0-1023), or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= pin <= 255, f"Pin must be in range 0-255, but was {pin}"

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.ANALOG_READ.value, pin, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 5, f"Expected reply to be 5 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.ANALOG_READ.value, f"Expected reply[1] to be TctlmIds.ANALOG_READ {TctlmIds.ANALOG_READ.value}, but was {reply[1]}"
        assert reply[4] == END_OF_MESSAGE, f"Expected reply[4] to be end of message {END_OF_MESSAGE}, but was {reply[4]}"

        value = (reply[2] << 8) & reply[3]
        assert 0 <= value <= 1023, f"Analog read value must be between 0 and 1023, but was {value}"

        return value  # The analog reading

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def analog_write(pin: int, value: int) -> Union[None, str]:
    """Writes a value to a PWM-supported pin in 8-bit resolution (0-255).

    Arguments:
        pin (int): The pin number to write to (0-255).
        value (int): The PWM value to write (0-255).

    Returns:
        None if successful, or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= pin <= 255, f"Pin must be in range 0-255, but was {pin}"
        assert 0 <= value <= 255, f"Value must be in range 0-255, but was {value}"

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.ANALOG_WRITE.value, pin, value, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 3, f"Expected reply to be 3 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.ANALOG_WRITE.value, f"Expected reply[1] to be TctlmIds.ANALOG_WRITE {TctlmIds.ANALOG_WRITE.value}, but was {reply[1]}"
        assert reply[2] == END_OF_MESSAGE, f"Expected reply[2] to be end of message {END_OF_MESSAGE}, but was {reply[2]}"

        return None  # Success

    except Exception as e:
        return str(e)

@my_mcp.tool()
async def delay(milliseconds: int) -> Union[None, str]:
    """Freezes program execution for the specified number of milliseconds.

    Note that the serial timeout will be increased by `milliseconds//1000 + 1`
    for the duration of this function call so that the serial port doesn't time
    out waiting for the response.

    Arguments:
        milliseconds (int): The number of milliseconds to delay (valid range: 0 to 4294967295).

    Returns:
        None if successful, or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        assert 0 <= milliseconds <= 4294967295, f"Milliseconds must be in range 0 to 4294967295, but was {milliseconds}"

        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        old_timeout = SERIAL_PORT.timeout
        if SERIAL_PORT.timeout is not None:
            SERIAL_PORT.timeout = SERIAL_PORT.timeout + (milliseconds // 1000)

        print(f"TIMEOUT: {SERIAL_PORT.timeout}")

        # Send delay command to Arduino
        SERIAL_PORT.write([
            START_OF_MESSAGE,
            TctlmIds.DELAY.value,
            milliseconds >> 24,
            (milliseconds >> 16) & 0xFF,
            (milliseconds >> 8) & 0xFF,
            milliseconds & 0xFF,
            END_OF_MESSAGE
        ])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 3, f"Expected reply to be 3 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.DELAY.value, f"Expected reply[1] to be TctlmIds.DELAY {TctlmIds.DELAY.value}, but was {reply[1]}"
        assert reply[2] == END_OF_MESSAGE, f"Expected reply[2] to be end of message {END_OF_MESSAGE}, but was {reply[2]}"

        SERIAL_PORT.timeout = old_timeout
        return None  # Success

    except Exception as e:
        SERIAL_PORT.timeout = old_timeout
        return str(e)


@my_mcp.tool()
async def millis() -> Union[int, str]:
    """Returns the number of milliseconds since the program started.

    Returns:
        (int) The number of milliseconds passed since program start,
        or a stringified error message if something went wrong.
    """
    global SERIAL_PORT
    try:
        if SERIAL_PORT is None:
            return SERIAL_PORT_NC_MESSAGE

        # Send millis command to Arduino
        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.MILLIS.value, END_OF_MESSAGE])
        reply = list(SERIAL_PORT.read_until(expected=[END_OF_MESSAGE]))

        assert not (len(reply) == 4 and reply[1] == TctlmIds.ERR.value), f"Received an error code: {reply[2]}"
        assert len(reply) == 7, f"Expected reply to be 7 bytes, but was {len(reply)}: {reply}"
        assert reply[0] == START_OF_MESSAGE, f"Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.MILLIS.value, f"Expected reply[1] to be TctlmIds.MILLIS {TctlmIds.MILLIS.value}, but was {reply[1]}"
        assert reply[6] == END_OF_MESSAGE, f"Expected reply[4] to be end of message {END_OF_MESSAGE}, but was {reply[4]}"

        # Convert the 4-byte reply to an integer (milliseconds)
        millis_value = (reply[2] << 24) | (reply[3] << 16) | (reply[4] << 8) | reply[5]

        return millis_value

    except Exception as e:
        return str(e)

@my_mcp.tool()
async def check_arduino_cli() -> Tuple[bool, str]:
    """Checks if the arduino-cli command-line tool is available on the system.

    Returns: A (bool, str) tuple. True if there is an arduino cli available.
    False otherwise. The string is either the stdout of `arduino-cli version`,
    or it is the stderr/exception that occured."""
    try:
        # Run arduino-cli --version to check if the tool is installed
        result = subprocess.run(['arduino-cli', 'version'], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            return (True, result.stdout)
        else:
            return (False, f"returncode is {result.returncode}, stderr: {result.stderr}")
    except Exception as e:
        return (False, str(e))

@my_mcp.tool()
async def list_arduino_boards() -> Union[list, str]:
    """Gets and parses the list of connected Arduino boards in JSON format
    using `arduino-cli board list --json`.

    Returns either a list of dictionaries, or a string with an error message
    the dictionaries have the format:

    { "port": str, "board_name": str, "fqbn": str }
    """
    try:
        # Run arduino-cli board list --json to get the list of boards in JSON format
        result = subprocess.run(['arduino-cli', 'board', 'list', '--json'], capture_output=True, text=True, check=True)

        if result.returncode != 0:
            return f"Return code is {result.returncode}, stderr: {result.stderr}"

        # Parse the JSON output
        data = json.loads(result.stdout)

        boards = []
        for entry in data.get("detected_ports", []):
            # Check if the entry has matching_boards and parse accordingly
            if "matching_boards" in entry:
                for board in entry["matching_boards"]:
                    boards.append({
                        "port": entry["port"]["address"],
                        "board_name": board["name"],
                        "fqbn": board["fqbn"],
                    })

        return boards

    except Exception as e:
        return str(e)


@my_mcp.tool()
async def list_devices() -> list[str]:
    """List the available serial ports/COM ports. One of these might be an
    Arduino that can be connected to. Empty if no serial ports are found. See
    also `list_arduino_boards` (iff the arduino-cli is available)

    Returns: A list of (port_name, description) tuples
    """
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return []
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")

    return [(port.device, port.description) for port in ports]


@my_mcp.tool()
async def disconnect_from_arduino() -> bool:
    global SERIAL_PORT
    try:
        if SERIAL_PORT is not None:
            SERIAL_PORT.close()
            SERIAL_PORT = None
    except:
        return False
    return True


@my_mcp.tool()
async def connect_to_arduino(
    port,
    baud_rate=9600,
    timeout_s=1,
    parity='NONE',
    stop_bits=1,
    byte_size=8,
) -> bool:
    """Connect to the selected serial port, optionally specifying the
    connection settings.

    Args:
        port: The string describing the serial port
        baud_rate: baud rate e.g. transmission speed (default: 9600),
        timeout_s: timeout in seconds before abandoning the connection (default: 1),
        parity: The serial port parity to use (default: 'NONE', options: EVEN, ODD, MARK, SPACE),
        stop_bits: The number of stop bits to use (default: 1, options: 1, 1.5, 2),
        byte_size: The number of bits in a byte (default: 8),

    Returns: False if a connection couldn't be made, otherwise True. The
    connection's state is maintained indefinitely.
    """
    global SERIAL_PORT
    parity  = {
        'NONE': serial.PARITY_NONE,
        'EVEN': serial.PARITY_EVEN,
        'ODD': serial.PARITY_ODD,
        'MARK': serial.PARITY_MARK,
        'SPACE': serial.PARITY_SPACE,
    }.get(parity, serial.PARITY_NONE)

    stop_bits = {
        1: serial.STOPBITS_ONE,
        1.5: serial.STOPBITS_ONE_POINT_FIVE,
        2: serial.STOPBITS_TWO,
    }.get(stop_bits, serial.STOPBITS_ONE)

    try:
        SERIAL_PORT = serial.Serial(
            port=port,
            baudrate=baud_rate,
            bytesize=byte_size,
            parity=parity,
            stopbits=stop_bits,
            timeout=timeout_s,
        )
        print(f"Connected to {port} with baud rate {baud_rate}.")
        return True
    except serial.SerialException as e:
        print(f"Failed to connect to {port}: {e}")
        return False

@my_mcp.tool()
async def upload_chat_with_arduino_firmware(fqbn: str, port: str) -> tuple:
    """Re-upload the Chat With Arduino firmware to the board.

    The arduino should already have the firmware, but if it doesn't or you're
    getting communication protocol errors, you can re-upload the firmware with
    this.

    Arguments:
        fqbn (str): The Fully Qualified Board Name (FQBN) of the Arduino board.
        port (str): The port to which the Arduino board is connected.

    Returns:
        tuple: A tuple containing the return code and either the stderr or stdout.
    """
    try:
        # Run the compile and upload command
        script_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(['arduino-cli', 'compile', '--fqbn', fqbn, '--port', port, '--upload', script_dir], capture_output=True, text=True)

        # Return the result
        if result.returncode == 0:
            return (result.returncode, result.stdout)
        else:
            return (result.returncode, '---stderr---\n' + result.stderr + '\n---stdout---\n' + result.stdout)

    except Exception as e:
        return (1, str(e))


@my_mcp.tool()
async def compile_and_upload_arduino_program(program_code: str, program_name: str, fqbn: str, port: str) -> tuple:
    """Compiles and uploads an Arduino program to a given board using arduino-cli.

    Arguments:
        program_code (str): The complete Arduino program code.
        program_name (str): The name of the program (without spaces).
        fqbn (str): The Fully Qualified Board Name (FQBN) of the Arduino board.
        port (str): The port to which the Arduino board is connected.

    Returns:
        tuple: A tuple containing the return code and either the stderr or stdout.
    """
    try:
        # Check if program_name contains spaces
        if " " in program_name:
            return (1, "Error: Program name cannot contain spaces.")

        # Create the directory for the program
        script_dir = os.path.dirname(os.path.abspath(__file__))
        program_dir = os.path.join(script_dir, 'code_written_by_llms', program_name)
        if not os.path.exists(program_dir):
            os.makedirs(program_dir, exist_ok=True)

        # Write the program code to the .ino file
        program_file_path = os.path.join('code_written_by_llms', program_dir, f"{program_name}.ino")
        with open(program_file_path, 'w') as program_file:
            program_file.write(program_code)

        # Run the compile and upload command
        command = ['arduino-cli', 'compile', '--fqbn', fqbn, '--port', port, '--upload', program_dir]
        result = subprocess.run(command, capture_output=True, text=True)

        # Return the result
        if result.returncode == 0:
            return (result.returncode, result.stdout)
        else:
            return (result.returncode, '---stderr---\n' + result.stderr + '\n---stdout---\n' + result.stdout)

    except Exception as e:
        return (1, str(e))


def main():
    my_mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
