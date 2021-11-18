# This is the code I used for the ChatRoom Client

import socket
import threading

class ChatClient:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 1234):
        self.address = (HOST, PORT)

        self.connectToServer()
        self.createRecievingThread()
        self.chat()

    def connectToServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

        self.recieveMessage()

        username = input()
        self.sendMessage(username)

    def recieveMessage(self):
        message = self.socket.recv(1028).decode('utf-8')
        print(message)

    def sendMessage(self, message: str):
        self.socket.send(message.encode('utf-8'))

    # used in order for client to be recieving all chat messages
    def createRecievingThread(self):
        thread = threading.Thread(target=self.recieveChatMessages)
        thread.daemon = True
        thread.start()

    def recieveChatMessages(self):
        while True:
            self.recieveMessage()

    # used for client to be sending chat messages
    def chat(self):
        while True:
            message = input()
            self.sendMessage(message)
            if message == "{quit}": break

if __name__ == '__main__':
    ChatClient()