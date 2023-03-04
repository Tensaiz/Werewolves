import signal

from game.client_controller import WerewolfClientController
from network.client import WerewolfNetworkClient


signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    network_client = WerewolfNetworkClient('localhost', 27015)
    controller = WerewolfClientController(network_client)
    network_client.set_controller(controller)
    network_client.connect()
    network_client.run()
    controller.ui.mainloop()
