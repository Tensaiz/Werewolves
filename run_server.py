import signal

from network.server import WerewolfServer

signal.signal(signal.SIGINT, signal.SIG_DFL)

server = WerewolfServer('0.0.0.0', 27015)
server.start()
