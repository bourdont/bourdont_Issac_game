import socket
import threading

class Server:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 5555):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.clients = {} # { socket: {'username': username, 'room': room_number(0 if not in room)} }
        self.rooms = {} # { room_number: {'players': [P1_Socket, P2_Socket], 'currentPlayers': 0, 'maxPlayers': 2} }
        self.startServer()

    def startServer(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'Server running on {self.host}:{self.port}')
        self.createRooms()
        self.createConnectionThreads()

    # create the multiple rooms a player can join
    def createRooms(self):
        pass

    # game code
    def handleGame(self):
        pass

    # create a seperate thread for every player
    def createConnectionThreads(self):
        while True:
            socket, address = self.socket.accept() # address is unused
            thread = threading.Thread(target=self.handleConnection, args=[socket])
            thread.start()

    def handleConnection(self, client: socket.socket()):
        username = self.checkLogin()
        self.clients[client] = {'username': username, 'room': 0}

    # check if users login information was correct, information stored in json. returns username
    def checkLogin(self, username: str, password: str) -> str:
        # sends message asking for login credentials, or to make a new account
        # waits to receive message, if account exists will login, if pw incorrect will kick out, if does not exist will create new account
        # Example messages: "login Chris 1234" -> login "login Chris 4321" -> Try again "register Tre 1234" -> create new account
        pass

    # create new user and store in Users.json. returns username
    def createNewAccount(self, username: str, password: str) -> str:
        pass

    # recieve message from client
    def recieveMessage(self, client: socket.socket()) -> str:
        return client.recv(1028).decode('utf-8')

    # sends message from server to client
    def sendMessageToClient(self, client: socket.socket(), message: str):
        try:
            client.send(f'{message}'.encode('utf-8'))
        except:
            print(f'There was an error sending a message to {self.clients[client]["username"]}, terminating connection')
            self.closeConnection(client)

    # close client connection and remove from dict
    def closeConnection(self, socket: socket.socket()):
        self.clients.pop(socket)
        socket.close()


if __name__ == '__main__':
    Server()