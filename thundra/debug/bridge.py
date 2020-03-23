import os
import socket
import select
import sys
import threading
import time
import json
import sys

sys.path.append("/opt")
sys.path.append("/var/task")

import websocket


try:
    import thread
except ImportError:
    import _thread as thread

OPCODE_BINARY = 0x2
PROTOCOL_VER = 1.0
BROKER_HANDSHAKE_HEADERS = {
    "AUTH_TOKEN": "x-thundra-auth-token",
    "SESSION_NAME": "x-thundra-session-name",
    "PROTOCOL_VER": "x-thundra-protocol-version",
    "RUNTIME": "x-thundra-runtime",
    "SESSION_TIMEOUT": "x-thundra-session-timeout"
}

BROKER_WS_HTTP_ERR_CODE_TO_MSG = {
    429: "Reached the concurrent session limit, couldn't start Thundra debugger.",
    401: "Authentication is failed, check your Thundra debugger authentication token.",
    409: "Another session with the same session name exists, connection closed.",
}


ws = None
debugger_socket = None

def handle_error_message(error):
    if hasattr(error, 'status_code'):
        print(BROKER_WS_HTTP_ERR_CODE_TO_MSG.get(error.status_code, "Broker connection got error: {}".format(error)), file=sys.stderr)
    else:
        print("Broker connection got error: {}".format(error), file=sys.stderr)

def handle_close_message(code, message):
    if code is None and message is None:
        print("Thundra debug broker connection is closed")
    elif code:
        print("Thundra debug broker closed with code:{}".format(code))
    else:
        print("Thundra debug broker closed with code:{}, message:{}".format(code, message))

def on_open(ws):
    def run():
        try:
            ws.running = True
            while ws.running:
                rlist = select.select([debugger_socket, sys.stdin], [], [])[0]

                if sys.stdin in rlist:
                    line = sys.stdin.readline()
                    if line.strip() == "fin":
                        ws.running = False

                if debugger_socket in rlist:
                    buf = debugger_socket.recv(4096)
                    if len(buf) == 0:
                        ws.running = False
                    ws.send(buf, opcode=OPCODE_BINARY)
            
        except Exception as e:
            print("Exception while listening from debugger socket and stdin: {}".format(e))
        ws.close()
    thread.start_new_thread(run, ())

def on_message(ws, message):
    try:
        if isinstance(message, bytes):
            ws.debugger_socket.send(message)
        else:
            ws.debugger_socket.send(message.encode())
    except Exception as e:
        print("Error on on_message: {}".format(e))

def on_error(ws, error):
    handle_error_message(error)
    ws.running = False

def on_close(ws, code, message):
    handle_close_message(code, message)
    ws.running = False

def normalize_broker_host(host):
    if host.startswith("wss://") or host.startswith("ws://"):
        return host
    return "wss://" + host

try:
    debugger_socket = socket.socket()
    debugger_socket.connect(("localhost", int(os.environ.get('DEBUGGER_PORT'))))
    ws = websocket.WebSocketApp("{}:{}".format(normalize_broker_host(os.environ.get('BROKER_HOST')), os.environ.get('BROKER_PORT')),
        header=[
            "{auth_token_header}: {value}".format(auth_token_header=BROKER_HANDSHAKE_HEADERS.get("AUTH_TOKEN"), value=os.environ.get("AUTH_TOKEN")),
            "{session_name_header}: {value}".format(session_name_header=BROKER_HANDSHAKE_HEADERS.get("SESSION_NAME"), value=os.environ.get("SESSION_NAME")),
            "{protocol_ver_header}: {value}".format(protocol_ver_header=BROKER_HANDSHAKE_HEADERS.get("PROTOCOL_VER"), value=PROTOCOL_VER),
            "{runtime_header}: {value}".format(runtime_header=BROKER_HANDSHAKE_HEADERS.get("RUNTIME"), value="python"),
            '{session_timeout_header}: {value}'.format(session_timeout_header=BROKER_HANDSHAKE_HEADERS.get("SESSION_TIMEOUT"), value=os.environ.get("SESSION_TIMEOUT"))
            ],
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.debugger_socket = debugger_socket
    ws.on_open = on_open
    ws.run_forever(sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))

except Exception as e:
    print(e)

try:
    ws.close()
except: pass

try:
    debugger_socket.close()
except: pass