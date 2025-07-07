import socket


class Message:
    message_id_number = 0

    TYPE_CON = 0
    TYPE_NON = 1
    TYPE_ACK = 2
    TYPE_RST = 3

    def __init__(self):

        # MESSAGE FORMAT
        self.address: tuple = ()
        self.coap_version: int = int()
        self.message_type: int = int()
        self.coap_code_class: int = int()
        self.coap_code_detail: int = int()
        self.message_id: int = int()

        self.token: bytearray = bytearray()
        self.token_length: int = int()

        self.options = list()

        # MESSAGE(URI) OPTIONS
        self.uri_path: int = int()
        self.uri_path_option_delta: int = int()
        self.uri_path_length: int = int()
        self.option_value: int = int()

        # PAYLOAD
        self.payload_marker = 0xFF
        self.payload: bytes = bytes()

    def __str__(self):
        return (f'Message:\n CoAP version: {self.coap_version},\nMessage Type: {self.message_type},\n'
                f'CoAP Code:{self.coap_code_class}.{self.coap_code_detail},\nMessage ID: {self.message_id},\n'
                f'Token Length: {self.token_length},\nToken: {self.token},\n'
                f'Options: {self.options},\nPayload: {self.payload}')

    def build_message(self, data, address):
        self.address = address
        self.coap_version = data[0] >> 6

        self.message_type = data[0] >> 4 & 0x03
        self.token_length = data[0] & 0x08
        self.coap_code_class = data[1] >> 5
        self.coap_code_detail = data[1] & 0x1F

        self.message_id = data[2] << 8 | data[3]

        n = 3 + self.token_length
        option_number = 0
        # travels through the data to get the options
        print(data[n])
        while data[n] is not self.payload_marker:
            temp_option_delta = data[n] >> 4
            option_number = option_number + temp_option_delta
            temp_option_length = data[n] & 0x0F
            n_option_value = data[n + 1: n + 1 + temp_option_length]
            self.options.append((option_number, temp_option_length, n_option_value))
            n = n + temp_option_length

        self.payload = data[n+1:]

    def get_raw_message(self) -> bytearray:
        data = bytearray()

        # Header: version, type, token length
        data.append(self.coap_version << 6 | self.message_type << 4 | self.token_length)
        # CoAP code
        data.append(self.coap_code_class << 5 | self.coap_code_detail)
        # Message ID
        data += self.message_id.to_bytes(2, 'big')
        # Token
        data += self.token

        # Options encoding
        previous_option_number = 0
        for option in self.options:
            option_number, option_length, option_value = option
            delta = option_number - previous_option_number
            previous_option_number = option_number

            # Single byte encoding for delta and length (assuming they fit)
            if delta <= 12 and option_length <= 12:
                data.append((delta << 4) | option_length)
            else:
                raise ValueError("Extended delta or length not implemented.")

            # Option value
            data += option_value

        # Payload
        if self.payload or self.payload_marker:
            data.append(self.payload_marker)
            data += self.payload

        return data

    import socket

    def send_response(self):
        """
        Sends the message as a response to the stored address.
        """
        if not self.address:
            raise ValueError("Address is not set. Cannot send the response.")

        raw_message = self.get_raw_message()

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(raw_message, self.address)
            print(f"Message sent to {self.address}: {raw_message}")

