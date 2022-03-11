import json
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from typing import Any
from xmlrpc.client import boolean

PORT = 0x2BAD
SERVER = "127.0.0.1"

def create_json(method : str, param : Any):
    data = {"jsonrpc": "2.0", "method": method, "params": [param]}
    return json.dumps(data).encode()

def read_json(data : Any):
    dict = json.loads(data)
    value = dict["params"]
    return value

if __name__ == '__main__':
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((SERVER, PORT))
        num = read_json(sock.recv(4096).decode())
        print(f"You're player {num}")
        isReady = False
        gameEnded = False
        while (not isReady):
                print("Veuillez appuyer sur R pour confirmer")
                content = input().lower()
                if(content == "r"):
                    isReady = True
                    sock.send(create_json("playerStatus", isReady))
        while not gameEnded:
            first_letter = read_json(sock.recv(4096).decode('utf-8'))#FIRST_LETTER RECEPTION
            wordIsCorrect = False
            while (not wordIsCorrect):
                content = input(f"Veuillez rentrer un mot commençant par {first_letter} \n").lower()
                sock.send(create_json("Mot",content))#MOT ENVOI

                dataSocket : dict = read_json(sock.recv(4096).decode())
                wordCode = dataSocket["WordStatus"]
                score: int = dataSocket["intScore"]

                if(wordCode == "0"):
                    print("Mot correct")
                    wordIsCorrect = True
                elif(wordCode == "1"):
                    print("Mauvaise première lettre")
                elif(wordCode == "2"):
                    print("Le mot n'existe pas, il ne fallait pas sécher les cours de français au collège en classe de 6ème B (la classe basket).")
                elif(wordCode == "3"):
                    print("Vous avez gagner la partie !")
                    timer = dataSocket["timer"]
                    print(f"Vous avez mis {timer} secondes")
                    gameEnded = True
                    break
                print("--------------------------")
                print(f"Votre score est de {score}")
        
        sock.close()

