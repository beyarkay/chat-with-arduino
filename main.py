from typing import Any, Union
import httpx
from mcp.server.fastmcp import FastMCP
import serial
import serial.tools.list_ports
from enum import Enum

# Initialize FastMCP server
mcp = FastMCP("chat-with-arduino")

SERIAL_PORT = None

SERIAL_PORT_NC_MESSAGE = (
    'Serial Port not connected, use `list_devices()` to view the '
    'available devices and `connect_to_arduino` to connect via '
    'serial port to an arduino'
)

START_OF_MESSAGE = 0xFE
END_OF_MESSAGE = 0xFF

class TctlmIds(Enum):
    ACK = 1
    DIGITAL_READ = 2
    DIGITAL_WRITE = 3
    PIN_MODE = 4
    ANALOG_READ = 5
    ANALOG_WRITE = 6
    TONE = 7
    NO_TONE = 8
    DELAY = 9
    MILLIS = 10
    AI = 11

@mcp.tool()
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

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.ACK, END_OF_MESSAGE])
        reply = SERIAL_PORT.read_until(expected=TctlmIds.END)

        return reply == [START_OF_MESSAGE, TctlmIds.ACK, END_OF_MESSAGE]

    except Exception as e:
        return str(e)

@mcp.tool()
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

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.DIGITAL_READ, pin, END_OF_MESSAGE])
        reply = SERIAL_PORT.read_until(expected=END_OF_MESSAGE)

        assert len(reply) == 4, "Expected reply to be 4 bytes, but was {len(reply)}"
        assert reply[0] == START_OF_MESSAGE, "Expected reply[0] to be start of message {START_OF_MESSAGE}, but was {reply[0]}"
        assert reply[1] == TctlmIds.DIGITAL_READ, "Expected reply[1] to be TctlmIds.DIGITAL_READ {TctlmIds.DIGITAL_READ}, but was {reply[1]}"
        assert reply[3] == END_OF_MESSAGE, "Expected reply[3] to be end of message {END_OF_MESSAGE}, but was {reply[3]}"
        assert reply[2] in (0, 1), f"Expected reply[2] to be 0 or 1, but was {reply[2]}"

        return bool(reply[2])  # Convert 0/1 to False/True

    except Exception as e:
        return str(e)




@mcp.tool()
async def digital_read() -> Union[bool, str]:
    global SERIAL_PORT
    try:
        if SERIAL_PORT is None:
            return False

        SERIAL_PORT.write([START_OF_MESSAGE, TctlmIds.ACK, END_OF_MESSAGE])
        reply = SERIAL_PORT.read_until(expected=TctlmIds.END)

        return reply == [START_OF_MESSAGE, TctlmIds.ACK, END_OF_MESSAGE]

    except Exception as e:
        return str(e)

@mcp.tool()
async def ack() -> Union[bool, str]:
    global SERIAL_PORT
    try:
        if SERIAL_PORT is None:
            return False

        SERIAL_PORT.write([TctlmIds.START, TctlmIds.ACK, TctlmIds.END])
        reply = SERIAL_PORT.read_until(expected=TctlmIds.END)

        return reply == [TctlmIds.START, TctlmIds.ACK, TctlmIds.END]

    except Exception as e:
        return str(e)

@mcp.tool()
async def list_devices() -> list[str]:
    """List the available serial ports/COM ports. One of these might be an
    Arduino that can be connected to. Empty if no serial ports are found

    Returns: A list of (port_name, description) tuples
    """
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return []
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")

    return [(port.device, port.description) for port in ports]

@mcp.tool()
async def disconnect_from_arduino() -> bool:
    global SERIAL_PORT
    try:
        if SERIAL_PORT is not None:
            SERIAL_PORT.close()
            SERIAL_PORT = None
    except:
        return False
    return True

@mcp.tool()
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


@mcp.tool()
async def is_connected() -> bool:
    """Check if you're connected to an Arduino

    Returns: True if the MCP server can communicate with the Arduino, False
    otherwise
    """
    global SERIAL_PORT
    SERIAL_PORT.write('ping'.encode())
    response = SERIAL_PORT.readline().decode().strip()
    return response == 'pong'

# @mcp.tool()
# async def digital_read(pin: int):
#     pass

@mcp.tool()
async def digital_write(pin: int, set_high: bool):
    if SERIAL_PORT is None:
        return
    SERIAL_PORT.write([0x00, pin, 0x1 if set_high else 0x0])
    pass

# @mcp.tool()
# async def analogue_read(pin: int):
#     pass
#
# @mcp.tool()
# async def analogue_write(pin: int):
#     pass
#
# @mcp.tool()
# async def set_pin_mode(pin: int, mode: int):
#     pass


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

