import socket
import select
import sys
import threading

sys.path.append("/var/task")

from thundra import config

broker_socket = None
debugger_socket = None
try:
    broker_socket = socket.socket()
    debugger_socket = socket.socket()

    broker_socket.connect((config.debugger_broker_host(), config.debugger_broker_port()))
    debugger_socket.connect(("localhost", config.debugger_port()))

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