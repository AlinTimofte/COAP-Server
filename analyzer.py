

def syntax_analyze(message):
    # Messages with unknown version numbers MUST be silently ignored.
    if message.coap_version == 1:
        # Lengths 9-15 are reserved, MUST NOT be sent, and MUST be processed as a message format error.
        if message.token_length < 9:
            if check_coap_code(message):
                return True
        else:
            # TODO: build a message with format error
            pass
    return False


def check_coap_code(message):
    if message.coap_code_class == 0:
        if message.coap_code_detail in (0, 1, 2, 3, 4, 5):
            return True
        else:
            return False
    elif message.coap_code_class == 2:
        if message.coap_code_detail in (1, 2, 3, 4, 5):
            return True
        else:
            return False
    elif message.coap_code_class == 4:
        if message.coap_code_detail in (0, 1, 2, 3, 4, 5, 6, 12, 13, 15):
            return True
        else:
            return False
    elif message.coap_code_class == 5:
        if message.coap_code_detail in (0, 1, 2, 3, 4, 5):
            return True
        else:
            return False
    else:
        return False
