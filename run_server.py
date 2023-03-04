import signal

from network.server import WerewolfServer

signal.signal(signal.SIGINT, signal.SIG_DFL)

server = WerewolfServer('localhost', 27015)
server.start()
