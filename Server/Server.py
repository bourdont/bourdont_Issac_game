import socket
import threading
import json

class Server:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 5555):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

        self.clients = {} # { socket: {'username': username, 'room': room_number(0 if not in room)} }
        self.rooms = {} # { room_number: {'players': [P1_Socket, P2_Socket], 'moves': {P1_Socket: 'r/p/s', P2_Socket: 'r/p/s'}, 'currentPlayers': 0, 'maxPlayers': 2} }

        self.file = 'Users.json'

        with open(self.file, 'r') as f:
            self.users = json.load(f) # { "username": {"Password": "", "Wins": 0, "Losses": 0, "Ties": 0, "Total Games": 0}}

        self.startServer()

    def startServer(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'Server running on {self.host}:{self.port}')
        self.createRooms()
        self.createConnectionThreads()

    # create the multiple rooms a player can join
    def createRooms(self):
        number_of_rooms = 2

        for i in range(number_of_rooms):
            self.rooms[i+1] = {'players': [], 'moves': {}, 'currentPlayers': 0, 'maxPlayers': 2}

    # create a seperate thread for every player
    def createConnectionThreads(self):
        while True:
            socket, address = self.socket.accept() # address is unused
            thread = threading.Thread(target=self.handleConnection, args=[socket])
            thread.start()

    def handleConnection(self, client: socket.socket()):
        username = self.checkLogin(client)
        self.clients[client] = {'username': username, 'room': 0}
        self.joinRoom(client)

    
    def joinRoom(self, client):
        # will just send the dict to give the GUI raw data to move around
        roomInfo = {}
        for i in range(len(self.rooms)):
            roomInfo[i+1] = {'currentPlayers': self.rooms[i+1].get('currentPlayers'), 'maxPlayers': self.rooms[i+1].get('maxPlayers')}

        self.sendMessageToClient(client, f'Which room would you like to join? Type {{stats}} to view your stats, {{reload}} to reload room list and {{quit}} to quit.\n{roomInfo}')

        while True:
            room = self.recieveMessage(client)

            if room == '{reload}':
                for i in range(len(self.rooms)):
                    roomInfo[i+1] = {'currentPlayers': self.rooms[i+1].get('currentPlayers'), 'maxPlayers': self.rooms[i+1].get('maxPlayers')}
                self.sendMessageToClient(client, roomInfo)
                continue

            if room == '{stats}':
                self.sendStats(client)
                continue

            if room == '{quit}':
                self.closeConnection(client)

            if not room.isnumeric():
                self.sendMessageToClient(client, 'Input was not a number')
                continue

            room = int(room)

            if room < 1 or room > len(self.rooms):
                self.sendMessageToClient(client, 'Invalid room')
                continue

            elif self.rooms[room].get('currentPlayers') == self.rooms[room].get('maxPlayers'):
                self.sendMessageToClient(client, 'Room is full')
                continue

            else:
                self.sendMessageToClient(client, f'Joining room number {room}...')
                self.clients[client]['room'] = room
                self.rooms[room]['players'].append(client)
                self.rooms[room]['currentPlayers'] += 1
                break

        self.handleGame(client)

    def leaveRoom(self, client, room):
        room['currentPlayers'] -= 1
        room['players'].remove(client)


    # check if users login information was correct, information stored in json. returns username
    def checkLogin(self, client: socket.socket()) -> str:
        # sends message asking for login credentials, or to make a new account
        # waits to receive message, if account exists will login, if pw incorrect will kick out, if does not exist will create new account
        # Example messages: "login Chris 1234" -> login "login Chris 4321" -> Try again "register Tre 1234" -> create new account
        self.sendMessageToClient(client, 'Login/Register with credentials (login/register [username] [password]')

        # infinite loop until correct login
        while True:
            msg = self.recieveMessage(client)
            msg = msg.split(' ')

            # check if user sent 3 parameters (l/r username and pass)
            if len(msg) != 3 or (msg[0] != 'login' and msg[0] != 'register'): 
                self.sendMessageToClient(client, 'Incorrect syntax')
                continue

            username = msg[1]
            password = msg[2]

            # register a new account
            if msg[0] == 'register': 
                if self.createNewAccount(client, username, password): 
                    self.sendMessageToClient(client, 'Successfully created a new account!\n')
                    break
                else: 
                    continue
            
            # logging into existing account
            user = self.users.get(username)

            # incorrect info
            if not user or password != user.get('Password'):
                self.sendMessageToClient(client, 'Incorrect username/password')
                continue

            # success
            self.sendMessageToClient(client, 'Successfully logged in!\n')
            break

        return username


    # create new user and store in Users.json. returns whether operation was successful or not
    def createNewAccount(self, client: socket.socket(), username: str, password: str) -> bool:
        if self.users.get(username):
            self.sendMessageToClient(client, 'User already exists!')
            return False

        self.users[username] = {"Password": password, "Wins": 0, "Losses": 0, "Ties": 0, "Total Games": 0}

        with open(self.file, "w") as f:
            json.dump(self.users, f, indent="")

        return True

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

    def sendStats(self, client: socket.socket()):
        user = self.users[self.clients[client]['username']]
        stats = {'Wins': user['Wins'], 'Losses': user['Losses'], 'Ties': user['Ties'], 'Total Games': user['Total Games']}

        self.sendMessageToClient(client, stats)

    # game code
    def handleGame(self, client):
        room = self.rooms[self.clients[client]['room']]
        if room == 0: return

        # waiting for another player
        opponent = self.waitForPlayer(client, room)
        opponentName = self.clients[opponent]["username"]

        while room['currentPlayers'] == room['maxPlayers']:
            # play your move, type {quit} to quit
            room['moves'][client] = ''
            self.sendMessageToClient(client, '(R)ock, (P)aper, or (S)cissors? Type {leave} to leave, {stats} for stats, or {quit} to quit.')

            # confirm move
            while True:
                msg = self.recieveMessage(client).lower()

                if msg == '{quit}': 
                    room['moves'][client] = 'quit'
                    self.leaveRoom(client, room)
                    self.closeConnection(client)

                if msg == '{leave}': 
                    room['moves'][client] = 'quit'
                    self.leaveRoom(client, room)
                    self.joinRoom(client)
                    return

                if msg == '{stats}': 
                    self.sendStats(client)
                    continue

                if msg == 'r':
                    room['moves'][client] = 'rock'

                elif msg == 'p':
                    room['moves'][client] = 'paper'

                elif msg == 's':
                    room['moves'][client] = 'scissors'

                else:
                    self.sendMessageToClient(client, 'Invalid move')
                    continue

                break

            # wait until opponent makes a move
            if not room['moves'][opponent]:
                self.sendMessageToClient(client, 'Waiting for opponents move...')
                while not room['moves'][opponent]:
                    continue

            if room["moves"][opponent] == 'quit':
                self.sendMessageToClient(client, f'{opponentName} has left the game.')
                break

            self.sendMessageToClient(client, f'{opponentName} chose {room["moves"][opponent]}')

            winlose = self.determineWinner(client, opponent, room)

            # adjust win/lose/total counters
            self.users[self.clients[client]['username']][winlose] += 1
            self.users[self.clients[client]['username']]['Total Games'] += 1

            with open(self.file, "w") as f:
                json.dump(self.users, f, indent="")
        
        self.handleGame(client)

    def waitForPlayer(self, client, room) -> socket.socket():
        if room['currentPlayers'] != room['maxPlayers']:
            self.sendMessageToClient(client, 'Waiting for another player. Type {leave} to leave')
            # TODO FIX: First player to join room must send a message in order to stop this loop
            while room['currentPlayers'] != room['maxPlayers']:
                msg = self.recieveMessage(client)
                if msg == '{leave}':
                    room['moves'][client] = 'quit'
                    self.leaveRoom(client, room)
                    self.joinRoom(client)
                    return
            self.sendMessageToClient(client, f'{self.clients[room["players"][1]]["username"]} has joined the game!')
            return room["players"][1]
        else:
            self.sendMessageToClient(client, f'{self.clients[room["players"][0]]["username"]} is your opponent!')
            return room["players"][0]

    # returns win, lose, or tie
    # I am really ashamed of this code but it works so idc enough to fix it
    def determineWinner(self, client, opponent, room) -> str:
        if room['moves'][client] == room['moves'][opponent]:
            self.sendMessageToClient(client, "It's a tie!")
            return 'Ties'

        elif room['moves'][client] == "rock":
            if room['moves'][opponent] == "scissors":
                self.sendMessageToClient(client, "Rock smashes scissors! You win!\n")
                return 'Wins'
            else:
                self.sendMessageToClient(client, "Paper covers rock! You lose.\n")
                return 'Losses'

        elif room['moves'][client] == "paper":
            if room['moves'][opponent] == "rock":
                self.sendMessageToClient(client, "Paper covers rock! You win!\n")
                return 'Wins'
            else:
                self.sendMessageToClient(client, "Scissors cuts paper! You lose.\n")
                return 'Losses'

        elif room['moves'][client] == "scissors":
            if room['moves'][opponent] == "paper":
                self.sendMessageToClient(client, "Scissors cuts paper! You win!\n")
                return 'Wins'
            else:
                self.sendMessageToClient(client, "Rock smashes scissors! You lose.\n")
                return 'Losses'

    # close client connection and remove from dict
    def closeConnection(self, socket: socket.socket()):
        self.clients.pop(socket)
        socket.close()


if __name__ == '__main__':
    Server()
