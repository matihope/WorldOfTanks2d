import socket
import pickle
from modules import mystrip


class Network:
    def __init__(self, ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        self.id_send = False

    def getId(self):
        self.id_send = True
        return self.id

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            quit(print('Connection error..'))

    def send_player(self, player):
        new_p = mystrip.my_stripInit(player)
        try:
            self.client.sendall(pickle.dumps(new_p))
        except socket.error as e:
            print(e)

    def p2(self, client):
        try:
            return mystrip.un_stripInit(pickle.loads(self.client.recv(4096 * 100)), client)
        except socket.error as e:
            print(e)

    def trade(self, player, client):
        try:
            self.client.send(pickle.dumps(mystrip.my_stripLite(player)))
            return mystrip.un_stripLite(pickle.loads(self.client.recv(1024)), client)
        except socket.error as e:
            print(e)
