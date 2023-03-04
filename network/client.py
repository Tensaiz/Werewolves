import socket
import threading
import pyaudio
import keyboard as kb
import json


class WerewolfNetworkClient:
    def __init__(self, host, port):
        # Network
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Audio
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

        self.controller = None

        # Game state
        self.is_muted = False
        self.is_deafened = False

    def connect(self):
        self.tcp_socket.connect((self.host, self.port))
        self.udp_socket.connect((self.host, self.port + 1))

        self.send_message(json.dumps({
            "sender": "me",
            "data": "hi"
        }))


        print('Connected to server')

    def send_message(self, message):

        # action: START_GAME
        # action:REGISTERED_PLAYER - name: [name]

        # action == "BASE_VOTE"
        # action == "WEREWOLF_VOTE"

        # Votes:
        # sender_id
        # selected_player_id

        self.tcp_socket.send(message.encode("utf-8"))

    def send_audio(self):
        print("AUDIO ACTIVATED")
        while True:
            if kb.read_key() == 'q' and not self.is_muted:
                data = self.input_stream.read(self.audio_settings['chunks'])
                self.udp_socket.sendto(data, (self.host, self.port + 1))
                print("Sent audio!")

    # Receive audio
    def handle_audio(self):
        while True:
            if not self.is_deafened:
                message_bytes = self.udp_socket.recv(16384)
                self.output_stream.write(message_bytes)

    def handle_message(self):
        while True:
            try:
                message_bytes = self.tcp_socket.recv(self.audio_settings['chunks'])
                message = json.loads(message_bytes.decode('utf-8'))
                self.controller.handle_message(message)
            except ConnectionError:
                break

    def set_controller(self, controller):
        self.controller = controller

    def update_muted(self, muted):
        self.is_muted = muted

    def update_deafened(self, deafened):
        self.is_deafened = deafened

    def run(self):
        threading.Thread(target=self.handle_message, daemon=True).start()
        threading.Thread(target=self.handle_audio, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
