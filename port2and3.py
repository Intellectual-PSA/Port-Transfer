import socket
import select
import time
import sys

# Changing buffer_size and delay can improve speed and reliability
buffer_size = 4096
delay = 0.05
forward_to = ('localhost', 3)

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False

class TheServer:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self, forward_to):
        input_list = [self.server]
        channel = {}

        while 1:
            ss = select.select
            inputready, outputready, exceptready = ss(input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept(forward_to, input_list, channel)
                elif self.s in channel:
                    self.on_recv(input_list, channel)

    def on_accept(self, forward_to, input_list, channel):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print(clientaddr, "has connected")
            input_list.append(clientsock)
            input_list.append(forward)
            channel[clientsock] = forward
            channel[forward] = clientsock
        else:
            print("Can't establish connection with remote server.", end=' ')
            print("Closing connection with client side", clientaddr)
            clientsock.close()

    def on_recv(self, input_list, channel):
        data = self.s.recv(buffer_size)
        if len(data) == 0:
            print(self.s.getpeername(), "has disconnected")
            self.s.close()
            input_list.remove(self.s)
            out = channel[self.s]
            channel[out].close()
            input_list.remove(channel[self.s])
            del channel[self.s]
            del channel[out]
            return
        print(data)
        channel[self.s].send(data)

if __name__ == '__main__':
    server = TheServer('localhost', 2)
    try:
        server.main_loop(forward_to)
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
