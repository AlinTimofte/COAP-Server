import socket
import base64
import json
import struct
import os

def parse_coap_message(data):
    """
    Parse a CoAP message and print its components.
    CoAP header structure:
    - 0-1 bits: Version
    - 2-3 bits: Type
    - 4-7 bits: Token length
    - 8-15 bits: Code
    - 16-31 bits: Message ID
    """
    if len(data) < 4:
        print("Invalid CoAP message: Too short")
        return

    # Extract the header fields
    version = (data[0] >> 6) & 0x03
    msg_type = (data[0] >> 4) & 0x03
    token_length = data[0] & 0x0F
    code_class = data[1] >> 5
    code_detail = data[1] & 0x1F
    message_id = struct.unpack("!H", data[2:4])[0]

    print("CoAP Message Details:")
    print(f"Version: {version}")
    print(f"Type: {msg_type}")
    print(f"Token Length: {token_length}")
    print(f"Code: {code_class}.{code_detail}")
    print(f"Message ID: {message_id}")

    # Extract the token if it exists
    if token_length > 0:
        token = data[4:4 + token_length]
        print(f"Token: {token.hex()}")
    else:
        token = None
        print("Token: None")

    # Extract options and payload
    payload_marker_index = data.find(b'\xFF')
    if payload_marker_index != -1:
        options = data[4 + token_length:payload_marker_index]
        payload = data[payload_marker_index + 1:]
    else:
        options = data[4 + token_length:]
        payload = b""

    print(f"Options: {options}")
    print(f"Payload: {payload.decode('utf-8', errors='ignore')}")

# CoAP constants
COAP_VERSION = 1  # CoAP version 1
TYPE_CON = 0  # Confirmable message
CODE_PUT = 1  # PUT request
MESSAGE_ID = 12345  # Arbitrary message ID

# JSON payload (replace with your actual JSON input)
json_payload = {
    "action": "GET",
    "folder_path": ".",
    "folder_type": "dir",
    "content": {
        "file_name": "directory1",
        "file_content": ""
    }
}

# Encode the payload as JSON and then as Base64
payload = json.dumps(json_payload).encode()

# Construct the basic CoAP header (4 bytes)
coap_header = bytearray(4)
coap_header[0] = (COAP_VERSION << 6) | (TYPE_CON << 4) | 0  # Version, Type, Token Length
coap_header[1] = CODE_PUT  # Code (0.03 = PUT)
coap_header[2] = (MESSAGE_ID >> 8) & 0xFF  # Message ID (high byte)
coap_header[3] = MESSAGE_ID & 0xFF  # Message ID (low byte)

# Construct an Option: URI-Path ("example")
# Format: delta (4 bits), length (4 bits), value (variable length)
uri_path = "example"
uri_path_option_delta = 11  # URI-Path has option number 11
uri_path_length = len(uri_path)
option_header = bytearray(1)
option_header[0] = (uri_path_option_delta << 4) | uri_path_length  # Option header
option_value = uri_path.encode()  # Encode the URI path as bytes

# Add the payload marker (0xFF) and the payload itself
payload_marker = bytearray([0xFF])  # Payload marker indicates the start of the payload

# Combine all parts into the final CoAP message
coap_message = coap_header + option_header + option_value + payload_marker + payload

# Send the CoAP message and wait for a response
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5683)  # Localhost and CoAP default port

try:
    # Send the message
    sock.sendto(coap_message, server_address)
    print(f"Sent CoAP message to {server_address}")
    print(f"Message (hex): {coap_message.hex()}")

    # Set a timeout for the socket to wait for a response
    sock.settimeout(5)  # Wait for up to 5 seconds

    # Receive the response
    response, address = sock.recvfrom(1024)  # Buffer size of 1024 bytes
    print(f"Received response from {address}")
    print(f"Response (hex): {response.hex()}")
    parse_coap_message(response)

except socket.timeout:
    print("No response received (timeout).")
finally:
    # Close the socket
    sock.close()

