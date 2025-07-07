import json
import socket
import os
from functools import reduce

import message as ms
import threading
import file_system as fs

max_size = 65507

defaultServerFileLocation = "server"
defaultToolsFileLocation = "tools"

# AF_INET for IPv4, SOCK_DGRAM for specification of datagram package, IPPROTO_UDP is the protocol
socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)


# Necessary to ensure thread safety
class MessageQueue:

    def __init__(self):

        self.__list = list()
        self.__lock = threading.Lock()

    # for the use of "x in message_queue"
    def __contains__(self, item):

        with self.__lock:
            return item in self.__list

    def get(self, index):

        with self.__lock:
            return self.__list[index]

    def pop(self):

        with self.__lock:
            return self.__list.pop()

    def put(self, message):

        with self.__lock:
            self.__list.insert(0, message)

    def is_empty(self):

        with self.__lock:
            if self.__list:
                return False
            else:
                return True


def recieve_data():
    data, address = socket_.recvfrom(max_size)
    message_recv = ms.Message()
    message_recv.build_message(data, address)
    print(message_recv)
    # socket_.sendto(message_recv.get_raw_message(), message_recv.address)
    msg_queue1.put(message_recv)


def process_response(message):
    payload = message.payload
    code = 0
    try:
        parsed = json.loads(payload)
    except Exception as e:
        print(e)
        return False
    parsed['folder_path'] = 'home/' + parsed['folder_path']
    try:
        if parsed['action'] == 'PUT' and message.coap_code_detail == 3:
            if parsed['folder_type'] != 'dir':
                code = fs.create_file(parsed['folder_path'], parsed['content']['file_name'],
                                      parsed['content']['file_content'], parsed['folder_type'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 1)
            else:
                code = fs.create_dir(parsed['folder_path'], parsed['content']['file_name'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 1)
        elif parsed['action'] == 'POST' and message.coap_code_detail == 2:
            if parsed['folder_type'] != 'dir':
                code = fs.add_to_file(parsed['folder_path'], parsed['content']['file_name'],
                                      parsed['folder_type'], parsed['content']['file_content'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 4)
            else:
                code = fs.move_dir(parsed['folder_path'], 'home/' + parsed['content']['file_content'],
                                   parsed['content']['file_name'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 4)
        elif parsed['action'] == 'GET' and message.coap_code_detail == 1:
            if parsed['folder_type'] == 'dir':
                code = get_dir(message, parsed['folder_path'], parsed['content']['file_name'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 5)
            else:
                code = get_file(message, parsed)
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 5)
        elif parsed['action'] == 'DELETE' and message.coap_code_detail == 4:
            if parsed['folder_type'] == 'dir':
                code = fs.delete(parsed['folder_path'], parsed['content']['file_name'], "")
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 2)
            else:
                code = fs.delete(parsed['folder_path'], parsed['content']['file_name'], parsed['folder_type'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 2)
        elif parsed['action'] == 'RENAME' and message.coap_code_detail == 5:
            if parsed['folder_type'] == 'dir':
                code = fs.rename(parsed['folder_path'], parsed['content']['file_name'], "",
                                 parsed['content']['file_content'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 4)
            else:
                code = fs.rename(parsed['folder_path'], parsed['content']['file_name'], parsed['folder_type'],
                                 parsed['content']['file_content'])
                if code < 0:
                    send_client_error_message(message, code)
                else:
                    send_response_message(message, 4)

    except Exception as e:
        print(e)
        print('eroare')
        return False


def send_reset_message(message):
    message.message_type = message.TYPE_RST
    message.coap_code_class = 0
    message.coap_code_detail = 0
    message.payload_marker = 0
    socket_.sendto(message.get_raw_message(), message.address)


def send_client_error_message(message, error_code):
    if message.message_type == message.TYPE_CON:
        message.message_type = message.TYPE_ACK
    else:
        ms.Message.message_id_number = (ms.Message.message_id_number + 1) % 0xFFFF
        message.message_id = ms.Message.message_id_number
    message.coap_code_class = 4
    if error_code == -1:
        message.coap_code_detail = 4
        message.payload = 'File path does not exist'.encode()
        print(message.payload)
    if error_code == -2:
        message.coap_code_detail = 9
        message.payload = 'File already exists'.encode()
        print(message.payload)
    if error_code == -3:
        message.coap_code_detail = 0
        message.payload = 'Directory is not empty'.encode()
        print(message.payload)
    socket_.sendto(message.get_raw_message(), message.address)


def send_response_message(message, code):
    if message.message_type == message.TYPE_CON:
        message.message_type = message.TYPE_ACK
    else:
        ms.Message.message_id_number = (ms.Message.message_id_number + 1) % 0xFFFF
        message.message_id = ms.Message.message_id_number
    message.coap_code_class = 2
    message.coap_code_detail = code
    socket_.sendto(message.get_raw_message(), message.address)


def get_dir(message, path, name):
    if not os.path.exists(path + '/' + name):
        return -1
    message.payload = reduce(lambda x, y: x + '\n' + y, os.listdir(path + '/' + name), "").encode()
    return 0


def get_file(message, parsed):
    if not os.path.isfile(parsed['folder_path'] + '/' + parsed['content']['file_name'] + '.' + parsed['folder_type']):
        return -1
    parsed['content']['file_content'] = open(parsed['folder_path'] + '/' + parsed['content']['file_name']
                                             + '.' + parsed['folder_type'], 'r').read()
    message.payload = json.dumps(parsed).encode()
    return 0


msg_queue1 = MessageQueue()

msg_queue2 = MessageQueue()
