import socket
import pickle
from _thread import *
import threading
import sys
from modules import mystrip
import time


server = '192.168.0.11'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen()
print('Waiting for a connection, Server is running...')

connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    if p == 0:
        games[gameId]['p1'] = pickle.loads(conn.recv(4096 * 100))
        while games[gameId]['p2'] is None:
            pass
        conn.sendall(pickle.dumps(games[gameId]['p2']))
    else:
        games[gameId]['p2'] = pickle.loads(conn.recv(4096 * 100))
        while games[gameId]['p1'] is None:
            pass
        conn.sendall(pickle.dumps(games[gameId]['p1']))

    while True:
        try:
            data = pickle.loads(conn.recv(4096))

            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if p == 0:
                        mystrip.server_strip(game['p2'], data)
                        conn.send(pickle.dumps(game['p1']))
                    else:
                        mystrip.server_strip(game['p1'], data)
                        conn.send(pickle.dumps(game['p2']))

            else:
                break
        except:
            break
    print(f'Lost connection with P:{p}')
    try:
        games[gameId]['end'] = True
    except KeyError:
        pass
    print('Closing game: ', gameId)

    idCount -= 1
    conn.close()


def run_game(gameId, FPS=60):
    g = games[gameId]
    while g['p1'] is None or g['p2'] is None:
        # Wait till the players are connected
        pass

    prev_time = time.perf_counter()
    while not g['end']:
        dt = time.perf_counter() - prev_time
        dfix = FPS * dt  # Delay fix

        if g['p1'].ready_to_shot:
            print('Player1 shot!')
        if g['p2'].ready_to_shot:
            print('Player2 shot!')

        prev_time = time.perf_counter()
        time.sleep(1/FPS)

    del games[gameId]
    print('Game stop!')


while True:
    conn, addr = s.accept()  # Waiting for connection..
    print('Connected to: ', addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = {'p1': None, 'p2': None, 'p1_bullet': None, 'p2_bullet': None, 'end': False}
        threading.Thread(target=run_game, args=(gameId, )).start()
        print('Creating a new game...')
    else:
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))
