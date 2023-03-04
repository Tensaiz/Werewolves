import socket
import threading
from typing import List

class WerewolfServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: List[ServerClientThread] = []

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'Server is running on port {self.port}!')

        while True:
            client_socket, address = self.socket.accept()
            print(f"New client connected {address}")
            client = ServerClientThread(client_socket, address, self)
            client.start()
            self.clients.append(client)

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def remove_client(self, client):
        self.clients.remove(client)


class ServerClientThread(threading.Thread):
    def __init__(self, socket, address, server):
        super().__init__()
        self.socket = socket
        self.address = address
        self.server = server

    # Listen to messages from client
    def run(self):
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    self.server.remove_client(self)
                    break
                self.server.broadcast(data)
        except(ConnectionResetError):
            print(f"Client {self.address} disconnected.")

    def send(self, message):
        self.socket.send(message)
