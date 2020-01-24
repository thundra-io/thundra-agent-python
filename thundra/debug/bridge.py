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

ws = None
debugger_socket = None

def on_open(ws):
    def run():
        try:
            debugger_socket = socket.socket()
            debugger_socket.connect(("localhost", int(os.environ.get('DEBUGGER_PORT'))))
            ws.debugger_socket = debugger_socket
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
                    ws.send(buf)
            
        except Exception as e:
            print("Exception while listening from debugger socket and stdin: {}".format(e))
        ws.close()
    thread.start_new_thread(run, ())

def on_message(ws, message):
    ws.debugger_socket.send(message.encode())

def on_error(ws, error):
    print("Broker connection got error: {}".format(error))
    ws.running = False

def on_close(ws, code, message):
    print("Broker closed with code:{}, message:{}".format(code, message))
    ws.running = False


try:
    ws = websocket.WebSocketApp("ws://{}:{}".format(os.environ.get('BROKER_HOST'), os.environ.get('BROKER_PORT')),
        header=[
            "x-thundra-auth-token: {}".format("thundra"),
            "x-thundra-session-name: {}".format("test"),
            "x-thundra-protocol-version: 1.0"
            ],
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
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