import socket
import threading

class ChatClient:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 5555):
        self.address = (HOST, PORT)
        print("first test")
        self.connectToServer()
        print("second test")
        self.createRecievingThread()
        print("third test")
        self.chat()

    def connectToServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        print("conn test")
        self.sendMessage("test")
        self.recieveMessage()
        print("conn test 2")
    
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
            print("Choose to send rock, paper, or scissors\n")
            print("(type r, p, or s and then enter)\n")
            message = input()
            self.sendMessage(message)
            if message == "{quit}": break

if __name__ == '__main__':
    ChatClient()
