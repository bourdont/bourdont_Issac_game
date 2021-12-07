import socket
import threading

class ClientCLI:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 5555):
        self.address = (HOST, PORT)

        self.connectToServer()
        self.createRecievingThread()
        self.interact()

    def connectToServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

        self.recieveMessage()

        login = input()
        self.sendMessage(login)

    def recieveMessage(self):
        message = self.socket.recv(1028).decode('utf-8')
        print(message)

    def sendMessage(self, message: str):
        self.socket.send(message.encode('utf-8'))

    def createRecievingThread(self):
        thread = threading.Thread(target=self.recieveIncomingMessages)
        thread.daemon = True
        thread.start()

    def recieveIncomingMessages(self):
        while True:
            self.recieveMessage()

    def interact(self):
        while True:
            message = input()
            self.sendMessage(message)
            if message == "{quit}": break

if __name__ == '__main__':
    ClientCLI()