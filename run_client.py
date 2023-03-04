import signal

from game.client_ui import WerewolfClientUI
from network.client import WerewolfNetworkClient


signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    client = WerewolfNetworkClient('localhost', 27015)
    ui = WerewolfClientUI(client)
    client.set_ui(ui)
    client.connect()
    client.run()
    ui.app.mainloop()
    # ui.run()
