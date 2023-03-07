import json
import socket
import threading
import time
import pyaudio
from typing import List
import queue
from network.game_progression import GameProgression
import numpy as np
CHUNK_SIZE = 32768
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class WerewolfServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_clients: List[ServerClientThread] = []
        self.udp_client_addresses = []
        self.game_progression: GameProgression = GameProgression(self)
        self.buffer = {}
        # Create PyAudio instance
        self.p = pyaudio.PyAudio()
        # Create PyAudio stream
        self.stream = self.p.open(format=FORMAT, channels=1, rate=RATE, output=True, frames_per_buffer=4096, stream_callback=self.callback)

    def start(self):
        # self.handle_audio_stream()
        self.tcp_socket.bind((self.host, self.port))
        self.udp_socket.bind((self.host, self.port + 1))
        self.tcp_socket.listen()
        print(f'Server is running on port {self.port}!')
        threading.Thread(target=self.handle_udp, daemon=True).start()
        # self.stream.start_stream()
        threading.Thread(target=self.handle_audio_stream, daemon=True).start()
        self.handle_tcp()

    # Callback function for PyAudio
    def callback(self, in_data, frame_count, time_info, status):
        data = b""
        for key in self.buffer:
            if len(self.buffer[key]) >= CHUNK_SIZE:
                data += self.buffer[key][:CHUNK_SIZE]
                self.buffer[key] = self.buffer[key][CHUNK_SIZE:]
        self.transmit_audio(data)
        # if len(data) == 0:
        data = b"0"*frame_count*8
        print(len(data))
        return (data, pyaudio.paContinue)

    def handle_audio_stream(self):
        self.stream.start_stream()

        while True:
            pass

    def handle_udp(self):
        # Start PyAudio stream
        while True:
            message, client_address = self.udp_socket.recvfrom(16384*64)
            if client_address not in self.udp_client_addresses:
                print(f"New UDP client connected {client_address}")
                self.udp_client_addresses.append(client_address)

            client_id = client_address[0]
            if client_id not in self.buffer:
                self.buffer[client_id] = b""
            self.buffer[client_id] += message

            # t = threading.Thread(target=lambda: self.transmit_audio(message))
            # t.start()

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