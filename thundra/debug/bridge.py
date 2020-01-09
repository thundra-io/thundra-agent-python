import os
import socket
import select
import sys
import threading
import time
import json


broker_socket = None
debugger_socket = None
try:
    broker_socket = socket.socket()
    debugger_socket = socket.socket()

    broker_socket.connect((os.environ.get('BROKER_HOST'), int(os.environ.get('BROKER_PORT'))))
    debugger_socket.connect(("localhost", int(os.environ.get('DEBUGGER_PORT'))))

    auth_request = {
        "authToken": os.environ.get('AUTH_TOKEN'),
        "sessionName": os.environ.get('SESSION_NAME'),
        "protocolVersion": "1.0",
        "runtime": "python"
    }

    broker_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    broker_socket.sendall((json.dumps(auth_request) + "\n").encode("utf-8"))

    running = True
    while running:
        rlist = select.select([broker_socket, debugger_socket, sys.stdin], [], [])[0]

        if sys.stdin in rlist:
            line = sys.stdin.readline()
            if line.strip() == "fin":
                running = False

        if broker_socket in rlist:
            buf = broker_socket.recv(4096)
            if len(buf) == 0:
                running = False
            debugger_socket.send(buf)

        if debugger_socket in rlist:
            buf = debugger_socket.recv(4096)
            if len(buf) == 0:
                running = False
            broker_socket.send(buf)

    broker_socket.close()
    debugger_socket.close()
except Exception as e:
    print(e)

try:
    broker_socket.close()
except: pass

try:
    debugger_socket.close()
except: pass