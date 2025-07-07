import coap_tools as ct
from coap_tools import msg_queue1

# TODO: make a MESSAGE_ID LIST with the timestamp


def deduplicate(message):
    if message in ct.msg_queue2:
        return False
    return True
