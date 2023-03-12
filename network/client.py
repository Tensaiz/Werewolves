import re
import socket
import threading
import time
import pyaudio
import json
import base64
import numpy as np
from game.utils import Utils
MAX_STREAM_POOL = 32


class WerewolfNetworkClient:
    def __init__(self, host, port):
        # Network
        self.host = host
        self.port = port
        self.base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.apply_effect = False
        # Audio
        self.audio = pyaudio.PyAudio()
        self.audio_settings = {
            'format': pyaudio.paInt16,
            'chunks': 4096,
            'channels': 2,
            'rate': 48000
        }
        self.input_stream = self.audio.open(
            format=self.audio_settings['format'],
            channels=self.audio_settings['channels'],
            rate=self.audio_settings['rate'],
            input=True,
            frames_per_buffer=self.audio_settings['chunks']
        )
        self.stream_pool = []
        self.stream_pool_availability = []

        for _ in range(MAX_STREAM_POOL):
            self.stream_pool.append(
                self.audio.open(
                    format=self.audio_settings['format'],
                    channels=self.audio_settings['channels'],
                    rate=self.audio_settings['rate'],
                    output=True,
                    frames_per_buffer=self.audio_settings['chunks'],
                )
            )
            self.stream_pool_availability.append(True)
        self.controller = None

        # Game state
        self.is_muted = False
        self.is_deafened = False

    def callback(self, in_data, frame_count, time_info, flag):
        return (in_data, pyaudio.paContinue)

    def connect(self):
        self.base_socket.connect((self.host, self.port))
        self.audio_socket.connect((self.host, self.port + 1))
        print('Connected to server')

    def send_message(self, message):
        self.base_socket.send(message.encode("utf-8"))

    def on_key_press(self, key):
        if hasattr(key, 'char') and key.char == 'v' and not self.is_muted:
            self.controller.ui.mark_player_speaking(self.controller.player.id)
            speech_bytes = self.input_stream.read(self.audio_settings['chunks'])
            speech_str = base64.b64encode(speech_bytes).decode("utf-8")
            speech_message = {
                'sender_id': self.controller.player.id,
                'status': 0,
                'data':  speech_str
            }
            message = json.dumps(speech_message).encode("utf-8")
            self.audio_socket.send(message)
            time.sleep(0.0001)

    def on_key_release(self, key):
        if hasattr(key, 'char') and key.char == 'v':
            self.controller.ui.mark_player_done_speaking(self.controller.player.id)
            speech_message = {
                'sender_id': self.controller.player.id,
                'status': 1
            }
            message = json.dumps(speech_message).encode("utf-8")
            self.audio_socket.send(message)

    # Receive audio
    def handle_audio(self):
        while True:
            if not self.is_deafened:
                message_bytes = self.audio_socket.recv(self.audio_settings['chunks'] * 4 * 16 * 4)
                try:
                    message = message_bytes.decode('utf-8')
                    object_indices = [m.start() for m in re.finditer("sender_id", message)]

                    for i, obj_idx in enumerate(object_indices):
                        start_idx = obj_idx - 2
                        end_idx = object_indices[i+1] - 2 if i < len(object_indices) - 1 else len(message)

                        message_obj = json.loads(message[start_idx:end_idx])
                        sender_id = message_obj['sender_id']

                        if sender_id != self.controller.player.id:
                            if message_obj["status"] == 0:
                                self.controller.ui.mark_player_speaking(sender_id)
                                audio_bytes = base64.b64decode(message_obj['data'])

                                # audio effect
                                # audio_bytes = self.pitch(audio_bytes, 30)

                                t = threading.Thread(target=lambda: self.play_audio(audio_bytes, sender_id))
                                t.start()
                            else:
                                self.controller.ui.mark_player_done_speaking(sender_id)
                except Exception as e:
                    print(e)

    def pitch(self, bytes, shift):
        pcm_floats = Utils.byte_to_float(bytes)

        pcm_floats = np.fft.rfft(pcm_floats)
        pcm_floats = np.roll(pcm_floats, shift)
        pcm_floats[0:shift] = 0
        pcm_floats = np.fft.irfft(pcm_floats)

        return Utils.float_to_byte(pcm_floats)

    def select_output_stream(self):
        while True:
            for i, is_available in enumerate(self.stream_pool_availability):
                if is_available:
                    return i

    def play_audio(self, message_bytes, sender_id):
        output_stream_index = self.select_output_stream()

        self.stream_pool_availability[output_stream_index] = False
        self.stream_pool[output_stream_index].write(message_bytes)
        self.stream_pool_availability[output_stream_index] = True

    def handle_message(self):
        while True:
            try:
                message_bytes = self.base_socket.recv(self.audio_settings['chunks'])
                message = json.loads(message_bytes.decode('utf-8'))
                # print(message)
                self.controller.handle_message(message)
            except ConnectionError:
                break

    def set_controller(self, controller):
        self.controller = controller

    def update_muted(self, muted):
        self.is_muted = muted

    def toggle_mute(self):
        self.is_muted = ~self.is_muted

    def update_deafened(self, deafened):
        self.is_deafened = deafened

    def run(self):
        threading.Thread(target=self.handle_message, daemon=True).start()
        threading.Thread(target=self.handle_audio, daemon=True).start()
        self.controller.ui.bind("<KeyPress>", self.on_key_press)
        self.controller.ui.bind("<KeyRelease>", self.on_key_release)
