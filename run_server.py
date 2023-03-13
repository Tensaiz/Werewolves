import signal

from werewolves.network.server import Server

signal.signal(signal.SIGINT, signal.SIG_DFL)

server = Server('0.0.0.0', 27015)
server.start()
