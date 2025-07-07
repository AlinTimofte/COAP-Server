import threading
import select

from analyzer import syntax_analyze
from deduplicator import deduplicate
import coap_tools as ct


def main_thrd_fct():
    while main_thread_event.is_set():
        try:
            # from https://docs.python.org/3/howto/sockets.html explaining non-blocking sockets
            recieved, _, _ = select.select([ct.socket_], [], [], 1)
            if recieved:
                ct.recieve_data()
                continue_analyzer_thread_event.set()
        except Exception as e:
            print(e)


def analyzer_thrd_fct():
    while analyzer_thread_event.is_set():
        if ct.msg_queue1.is_empty():
            continue_analyzer_thread_event.wait()
            continue_analyzer_thread_event.clear()
        message = ct.msg_queue1.pop()
        if syntax_analyze(message):
            if deduplicate(message):
                ct.msg_queue2.put(message)
                continue_processing_thread_event.set()


def processing_thrd_fct():
    while processing_thread_event.is_set():
        if ct.msg_queue2.is_empty():
            continue_processing_thread_event.wait()
            continue_processing_thread_event.clear()
        message = ct.msg_queue2.pop()
        ct.process_response(message)


def start_threads():
    try:
        main_thread_event.set()
        analyzer_thread_event.set()
        processing_thread_event.set()
        main_thread.start()
        analyzer_thread.start()
        processing_thread.start()
    except Exception as e:
        print(e)
        raise


def stop_threads():
    try:
        main_thread_event.clear()
        analyzer_thread_event.clear()
        processing_thread_event.clear()

        main_thread.join()
        analyzer_thread.join()
        processing_thread.join()
    except Exception as e:
        print(e)


main_thread = threading.Thread(target=main_thrd_fct, name="Main Thread")
analyzer_thread = threading.Thread(target=analyzer_thrd_fct, name="Analyzer Thread")
processing_thread = threading.Thread(target=processing_thrd_fct, name="Processing Thread")

main_thread_event = threading.Event()
analyzer_thread_event = threading.Event()
processing_thread_event = threading.Event()

continue_analyzer_thread_event = threading.Event()
continue_processing_thread_event = threading.Event()
