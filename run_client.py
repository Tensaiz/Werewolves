import signal

from game.controller import WerewolfClientController

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    controller = WerewolfClientController()
    controller.start_auth_ui()
