import json
import socket
import threading
from typing import List
from network.game_progression import GameProgression


class WerewolfServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_clients: List[ServerClientThread] = []
        self.udp_client_addresses = []
        self.game_progression: GameProgression = GameProgression(self)

    def start(self):
        self.tcp_socket.bind((self.host, self.port))
        self.udp_socket.bind((self.host, self.port + 1))
        self.tcp_socket.listen()
        print(f'Server is running on port {self.port}!')
        threading.Thread(target=self.handle_udp, daemon=True).start()
        self.handle_tcp()

    def handle_udp(self):
        while True:
            message, client_address = self.udp_socket.recvfrom(16384)

            if client_address not in self.udp_client_addresses:
                self.udp_client_addresses.append(client_address)

            self.transmit_audio(message)

    def transmit_audio(self, message):
        for udp_client in self.udp_client_addresses:
            self.udp_socket.sendto(message, udp_client)

    def handle_tcp(self):
        while True:
            tcp_client_socket, tcp_address = self.tcp_socket.accept()
            print(f"New TCP client connected {tcp_address}")
            tcp_client = ServerClientThread(tcp_client_socket, tcp_address, self)
            tcp_client.start()
            self.tcp_clients.append(tcp_client)

    def broadcast(self, message):
        for client in self.tcp_clients:
            client.send(message)

    def remove_client(self, client):
        self.tcp_clients.remove(client)
        self.game_progression.remove_player(client)
        # TODO: Remove UDP client with same IP


class ServerClientThread(threading.Thread):
    def __init__(self, socket, address, server: WerewolfServer):
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
                self.server.game_progression.process(data, self)
                # self.server.broadcast(data)
        except (ConnectionResetError):
            print(f"Client {self.address} disconnected.")
            self.server.remove_client(self)

    def send(self, message):
        message = json.dumps(message).encode("utf-8")
        self.socket.send(message)