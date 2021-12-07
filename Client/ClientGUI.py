import socket
import threading
import PySimpleGUI as sg

# client code
class ClientGUI:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 5555):
        self.address = (HOST, PORT)
        self.gameTitle = "RPS"
        self.connectToServer()
        # self.createRecievingThread()
        self.main()

    def connectToServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        self.recieveMessage()

    # def createRecievingThread(self):
    #     self.thread = threading.Thread(target=self.recieveMessages)
    #     self.thread.daemon = True
    #     self.thread.start()

    # def recieveMessages(self):
    #     while True:
    #         self.recieveMessage()

    def recieveMessage(self):
        message = self.socket.recv(1028).decode('utf-8')
        return message

    def sendMessage(self, message: str):
        self.socket.send(message.encode('utf-8'))

    def main(self):
        self.loginInit()
        while True:
            sendString = ""
            event, values = self.window.read()
            sendString = self.eventsCheck(event, values)
            if(sendString != ""):
                self.sendMessage(sendString)
                msg = self.recieveMessage()
                self.messageChecker(msg) 

    #gui code
    def messageChecker(self, message):
        # login menu
        if (message == "Incorrect username/password" or message == "User already exists!"):
            sg.popup(message)

        # room menu
        if (message[0:34] == "Which room would you like to join?"):
            self.homeInit(message)

        if (message[0:7] == "Joining"):
            if (message[24:31] == "Waiting"):
                self.gameWaiting()
            else:
                self.gameInit()

        # multi menu
        if(message[2:6] == "Wins"):
            sg.Popup(message)


    def loginInit(self):
        sg.theme('DarkAmber')
        layout = [  [sg.Text('Welcome to RPS\nEnter your Username and Password to login\nOr register')],
                    [sg.Text('Enter your Username: '), sg.InputText()],
                    [sg.Text('Enter your Password: '), sg.InputText()],
                    [sg.Button('Quit'), sg.Button('Register'), sg.Button('Login')]]
        
        self.window = sg.Window(self.gameTitle, layout)


    def homeInit(self, text):
        sg.theme('DarkAmber')
        text = text.split("\n")
        layout = [  [sg.Text("Current Rooms:\n" + text[1])],
                    [sg.Text('Enter the room you want to join: '), sg.InputText()],
                    [sg.Button('Quit'), sg.Button('Stats'), sg.Button('Reload'), sg.Button('Join Room')] ]

        # Create the Window
        self.window.close()
        self.window = sg.Window(self.gameTitle, layout)


    def gameInit(self):
        sg.theme('DarkAmber')
        layout = [  [sg.Text('Welcome to the Game Screen')],
                    [sg.Button('Rock'), sg.Button('Paper'), sg.Button('Scissors')] ]

        # Create the Window
        self.window.close()
        self.window = sg.Window(self.gameTitle, layout)


    def gameWaiting(self):
        sg.theme('DarkAmber')
        layout = [  [sg.Text('Waiting for another player...')],
                    [sg.Button('Leave')]]

        # Create the Window
        self.window.close()
        self.window = sg.Window(self.gameTitle, layout)


    def eventsCheck(self, event, values):
        sendString = ""

        # if user closes window or clicks quit
        if event == 'Quit' or event == sg.WIN_CLOSED: 
            self.sendMessage('{quit}')
            exit()

        # login screen
        if event == 'Login':
            sendString = f"login {values[0]} {values[1]}"
        if event == 'Register':
            sendString = f"register {values[0]} {values[1]}"

        # room menu
        if event == 'Join Room':
            sendString = values[0]

        if event == 'Stats':
            sendString = "{stats}"

        if event == 'Reload':
            sendString = "{reload}"

        if event == 'Leave':
            sendString = "{leave}"

        return sendString

if __name__ == '__main__':
    ClientGUI()
