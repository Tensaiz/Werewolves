import json
import socket
import threading
from typing import List
from network.game_progression import GameProgression


class WerewolfServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.basic_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_clients = []
        self.basic_clients: List[BaseClientThread] = []
        self.game_progression: GameProgression = GameProgression(self)

    def start(self):
        self.basic_socket.bind((self.host, self.port))
        self.audio_socket.bind((self.host, self.port + 1))

        self.basic_socket.listen()
        self.audio_socket.listen()

        print(f'Server is running on port {self.port}!')

        threading.Thread(target=self.handle_audio, daemon=True).start()
        self.handle_base()

    def handle_audio(self):
        while True:
            audio_client_socket, client_address = self.audio_socket.accept()
            audio_client = AudioClientThread(audio_client_socket, client_address, self)
            audio_client.start()
            self.audio_clients.append(audio_client)

    def handle_base(self):
        while True:
            base_client_socket, client_address = self.basic_socket.accept()
            print(f"New TCP client connected {client_address}")
            base_client = BaseClientThread(base_client_socket, client_address, self)
            base_client.start()
            self.basic_clients.append(base_client)

    def broadcast(self, message, receivers=None):
        if receivers is None:
            receivers = self.basic_clients
        for client in receivers:
            client.send(message)

    def remove_audio_client(self, client):
        self.audio_clients.remove(client)

    def remove_base_client(self, client):
        self.basic_clients.remove(client)
        self.game_progression.remove_player(client)


class AudioClientThread(threading.Thread):
    def __init__(self, socket, address, server: WerewolfServer):
        super().__init__()
        self.socket = socket
        self.address = address
        self.server = server

    def run(self):
        try:
            while True:
                data = self.socket.recv(4096*2*4)
                if not data:
                    self.server.remove_audio_client(self)
                    break
                self.server.broadcast(data, self.server.audio_clients)
        except (ConnectionResetError):
            print(f"Client {self.address} disconnected from audio.")
            self.server.remove_audio_client(self)

    def send(self, message):
        self.socket.send(message)


class BaseClientThread(threading.Thread):
    def __init__(self, socket, address, server: WerewolfServer):
        super().__init__()
        self.socket = socket
        self.address = address
        self.server = server

    # Listen to messages from client
    def run(self):
        try:
            while True:
                data = self.socket.recv(4096*2)
                if not data:
                    self.server.remove_base_client(self)
                    break
                self.server.game_progression.process(data, self)
                # self.server.broadcast(data)
        except (ConnectionResetError):
            print(f"Client {self.address} disconnected from messaging.")
            self.server.remove_base_client(self)

    def send(self, message):
        message = json.dumps(message).encode("utf-8")
        self.socket.send(message)
