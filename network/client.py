import socket
import threading
import pyaudio
import keyboard as kb


class WerewolfNetworkClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.socket.connect((self.host, self.port))
        print('Connected to server')

    def send_text(self, message):
        self.socket.send(message.encode("utf-8"))

    def send_audio(self):
        while True:
            try:
                if kb.read_key() == 'q' and not self.muted:
                    data = self.input_stream.read(
                        self.audio_settings['chunks']
                    )
                    self.socket.send(data)
            except:
                break

    def handle_message(self):
        while True:
            try:
                message_bytes = self.socket.recv(self.audio_settings['chunks'])
                if not message_bytes:
                    break
                try:
                    message = message_bytes.decode('utf-8')
                    self.ui.display_message(message)
                except(UnicodeDecodeError):
                    self.output_stream.write(message_bytes)
            except ConnectionError:
                break

    def set_ui(self, ui):
        self.ui = ui

    def run(self):
        threading.Thread(target=self.handle_message, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
