import signal

from game.controller import Controller

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    controller = Controller()
    controller.start_auth_ui()
