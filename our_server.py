import random
import time
from socket import socket, AF_INET, SOCK_STREAM
import string
from struct import pack, unpack
from threading import Thread, Event

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

        self._sock.send(pack('!i', self._id))
        isReady = self._sock.recv(1)
        self._choice = unpack("?", isReady)[0]
        if all_players_ready():
            starter_time = time.time()
            while True:
                first_letter = random.choice(string.ascii_letters).lower()                
                self._sock.send(first_letter.encode())
                wordIsCorrect = False
                while(not wordIsCorrect):
                    word = self._sock.recv(4096).decode()
                    if not (word[0] == first_letter):
                        #Si 1, mauvaise premiere lettre
                        self._sock.send(pack('!i', 1)) #Envoie code associé au mot
                    elif word in list_of_words:
                        #Si 0, mot conforme
                        self._nbletters += len(word) 
                        if self._nbletters > NB_LETTERS_WIN:
                            end_time = time.time() 
                            self._sock.send(pack('!i', 3))
                            self._sock.send(pack('!i', self._nbletters))
                            x = (end_time - starter_time)
                            self._sock.send(pack('!f',x))
                            print(f"- Player {self._id} left")
                            return  
                        else:
                            self._sock.send(pack('!i', 0))
                            wordIsCorrect = True 
                    else:
                        #Si 2 mot qui n'existe pas
                        self._sock.send(pack('!i', 2))
                    
                    self._sock.send(pack('!i', self._nbletters))
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
