import sys
import socket
import os

import thread as th
import coap_tools as ct

if __name__ == '__main__':
    if not os.path.exists('home'):
        os.mkdir('home')
    try:
        # ip 127.0.0.1 with the port of 5683, could also add an option in the future for config
        ct.socket_.bind(('127.0.0.1', 5683))
    except Exception as e:
        print("Eroare bind socket")
        sys.exit()
    try:
        th.start_threads()
    except Exception as e:
        print("Eroare creare thread-uri")
        sys.exit()

    while True:
        try:
            input("CTRL-c to stop execution")
        except KeyboardInterrupt:
            th.stop_threads()
            print("Program stopped")
