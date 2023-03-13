import random
from typing import List
from game.player import Player
import numpy as np


class Utils():
    @staticmethod
    def get_random_player(players):
        return random.choice(players)

    @staticmethod
    def calculate_available_role_frequency(player_n, roles):
        pass

    @staticmethod
    def get_player_by_id(id, players: List[Player]):
        for player in players:
            if player.id == id:
                return player

    @staticmethod
    def float_to_byte(sig):
        # float32 -> int16(PCM_16) -> byte
        return Utils.float2pcm(sig, dtype='int16').tobytes()

    @staticmethod
    def byte_to_float(byte):
        # byte -> int16(PCM_16) -> float32
        return Utils.pcm2float(np.frombuffer(byte, dtype=np.int16), dtype='float32')

    @staticmethod
    def pcm2float(sig, dtype='float32'):
        sig = np.asarray(sig)
        if sig.dtype.kind not in 'iu':
            raise TypeError("'sig' must be an array of integers")
        dtype = np.dtype(dtype)
        if dtype.kind != 'f':
            raise TypeError("'dtype' must be a floating point type")

        i = np.iinfo(sig.dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (sig.astype(dtype) - offset) / abs_max

    @staticmethod
    def float2pcm(sig, dtype='int16'):
        sig = np.asarray(sig)
        if sig.dtype.kind != 'f':
            raise TypeError("'sig' must be a float array")
        dtype = np.dtype(dtype)
        if dtype.kind not in 'iu':
            raise TypeError("'dtype' must be an integer type")

        i = np.iinfo(dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)
