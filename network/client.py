import socket
import threading
import pyaudio
import keyboard as kb
import json


class WerewolfNetworkClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.ui = None
        self.muted = False
        self.audio = pyaudio.PyAudio()
        self.audio_settings = {
            'format': pyaudio.paInt16,
            'chunks': 4096,
            'channels': 2,
            'rate': 44100
        }
        self.input_stream = self.audio.open(
            format=self.audio_settings['format'],
            channels=self.audio_settings['channels'],
            rate=self.audio_settings['rate'],
            input=True,
            frames_per_buffer=self.audio_settings['chunks']
        )
        self.output_stream = self.audio.open(
            format=self.audio_settings['format'],
            channels=self.audio_settings['channels'],
            rate=self.audio_settings['rate'],
            output=True,
            frames_per_buffer=self.audio_settings['chunks']
        )

    def connect(self):
        self.tcp_socket.connect((self.host, self.port))
        self.udp_socket.connect((self.host, self.port + 1))
        
        self.send_message(json.dumps({
            "sender": "me",
            "data": "hi"
        }))
        print('Connected to server')

    def send_message(self, message):
        self.tcp_socket.send(message.encode("utf-8"))

    def send_audio(self):
        print("AUDIO ACTIVATED")
        while True:
            if kb.read_key() == 'q' and not self.muted:
                data = self.input_stream.read(self.audio_settings['chunks'])
                self.udp_socket.sendto(data, (self.host, self.port + 1))
                print("Sent audio!")

    def handle_audio(self):
        while True:
            message_bytes = self.udp_socket.recv(16384)
            self.output_stream.write(message_bytes)

    def handle_message(self):
        while True:
            try:
                message_bytes = self.tcp_socket.recv(self.audio_settings['chunks'])
                message = json.loads(message_bytes.decode('utf-8'))
                self.ui.handle_message(message)
            except ConnectionError:
                break

    def set_ui(self, ui):
        self.ui = ui

    def run(self):
        threading.Thread(target=self.handle_message, daemon=True).start()
        threading.Thread(target=self.handle_audio, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
