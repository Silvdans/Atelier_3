import json
import random
import time
from socket import socket, AF_INET, SOCK_STREAM
import string
from struct import pack, unpack
from threading import Thread, Event
from typing import Any

PORT = 0x2BAD
NB_LETTERS_WIN = 30
players = []
list_of_words = []
first_letter = ""

class Player(Thread):
    def __init__(self, num, sock):
        Thread.__init__(self)
        self._id = num
        self._sock = sock
        self._ready = False
        self._nbletters = 0

    def is_ready(self):
        return self._ready is not None

    def run(self):
        global ready_event

        self._sock.send(create_json("idjoueur",self._id))
        
        isReady = self._sock.recv(4096)
        self._choice = read_json(isReady)
        if all_players_ready():
            starter_time = time.time()
            while True:
                first_letter = random.choice(string.ascii_letters).lower()                
                self._sock.send(create_json("first_letter",first_letter))
                wordIsCorrect = False
                while(not wordIsCorrect):
                    word_dansliste = read_json(self._sock.recv(4096))#MOT Reception
                    word =word_dansliste[0]
                    if not (word[0] == first_letter):
                        #Si 1, mauvaise premiere lettre
                        self._sock.send(create_json_dict("wordStatus",{"WordStatus": "1"})) #Envoie code associé au mot
                    elif word in list_of_words:
                        # Si 3, mot conforme et parte finie
                        self._nbletters += len(word) 
                        if self._nbletters > NB_LETTERS_WIN:
                            end_time = time.time() 
                            x = (end_time - starter_time)
                            #Envoie du code(mot), score, temps
                            self._sock.send(create_json_dict("WordStatus/intScorefinal/timer",
                                            {"WordStatus": "3", "intScore": self._nbletters,"timer" : x}))

                            print(f"- Player {self._id} left")
                            return  
                        else:
                            # Si 0, mot conforme mais partie pas fini
                            self._sock.send(create_json_dict("WordStatus/intScore",
                                                             {"WordStatus": "0","intScore":self._nbletters}))
                            wordIsCorrect = True
                    else:
                        #Si 2 mot qui n'existe pas
                        self._sock.send(create_json("wordStatus","2"))


def load_list_of_words():
    a_file = open("mot.txt", "r", encoding="utf8")
    for line in a_file:
        word =line.rstrip()
        list_of_words.append(word)
    a_file.close()

def all_players_ready():
    global players

    for player in players:
        if player is not None and not player.is_ready():
            return False
    return True

def find_player_id():
    global players

    for i in range(len(players)):
        if players[i] is None:
            return i+1
    players.append(None)
    return len(players)

def create_json(method : str, param : Any):
    data = {"jsonrpc": "2.0", "method": method,"params": param}
    return json.dumps(data).encode()

def create_json_dict(method : str, param : dict):
    data = {"jsonrpc": "2.0", "method": method,"params": param}
    return json.dumps(data).encode()
    
def read_json(data : bytes):
    
    dict= json.loads(data.decode())
    value = dict["params"]
    return value

if __name__ == '__main__':
    with socket(AF_INET, SOCK_STREAM) as sock_listen:
        sock_listen.bind(('', PORT))
        sock_listen.listen(5)
        print(f"Listening on port {PORT}")
        load_list_of_words()
        while True:
            sock_service, client_addr = sock_listen.accept()
            index = find_player_id()
            print(f"- Player {index} arrived")
            players[index-1] = Player(index, sock_service)
            players[index-1].start()
