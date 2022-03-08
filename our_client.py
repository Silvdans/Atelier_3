from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from xmlrpc.client import boolean

PORT = 0x2BAD
SERVER = "127.0.0.1"

if __name__ == '__main__':
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((SERVER, PORT))
        num = unpack('!i', sock.recv(4))[0]
        print(f"You're player {num}")
        isReady = False
        gameEnded = False
        while (not isReady):
                print("Veuillez appuyer sur R pour confirmer")
                content = input().lower()
                if(content == "r"):
                    isReady = True
                    sock.send(pack('?', isReady))
        while not gameEnded:
            first_letter = sock.recv(4096).decode('utf-8')
            wordIsCorrect = False
            while (not wordIsCorrect):
                content = input(f"Veuillez rentrer un mot commençant par {first_letter} \n").lower()
                sock.send(content.encode())
                wordCode = unpack('!i', sock.recv(4))[0]  #Reception code associé au mot
                score = unpack('!i', sock.recv(4))[0]
                if(wordCode == 0):
                    print("Mot correct")
                    wordIsCorrect = True
                elif(wordCode == 1):
                    print("Mauvaise première lettre")
                elif(wordCode == 2):
                    print("Le mot n'existe pas, il ne fallait pas sécher les cours de français au collège en classe de 6ème B (la classe basket).")
                elif(wordCode == 3):
                    print("Vous avez gagner la partie !")
                    timer = unpack('!f', sock.recv(4))[0]
                    print(f"Vous avez mis {timer} secondes")
                    gameEnded = True
                    break
                print("--------------------------")
                print(f"Votre score est de {score}")
        
        sock.close()