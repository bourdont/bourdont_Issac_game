import socket
import threading
import PySimpleGUI as sg

#client code
class ChatClient:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 5555):
        self.address = (HOST, PORT)
        self.connectToServer()
        self.createRecievingThread()
        self.chat()

    def connectToServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        self.recieveMessage()

    def recieveMessage(self):
        message = self.socket.recv(1028).decode('utf-8')
        print("what")
        return message

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
        window = loginInit()
        while True:
            sendString = ""
            event, values = window.read()
            sendString = eventsCheck(event, values)
            if(sendString != ""):
                self.sendMessage(sendString)
                window = messageChecker(self.recieveMessage(), window)
            

#gui code
def messageChecker(message,window):
    print("here?")
    if(message[0:34] == "Which room would you like to join?"):
        window = homeInit(window, message)
    if(message[2:6] == "Wins"):
        print("pop")
        sg.Popup(message)
    return window
                
def loginInit():
    sg.theme('DarkAmber')
    layout = [  [sg.Text('Welcome to RPS\nEnter your Username and Password to login\nOr click register')],
                [sg.Text('Enter your Username: '), sg.InputText()],
                [sg.Text('Enter your Password: '), sg.InputText()],
                [sg.Button('Enter'), sg.Button('Quit'), sg.Button('Register')]]
    
    window = sg.Window('RPS Game', layout)
    return window    


def homeInit(window, text):
    sg.theme('DarkAmber')
    text = text.split("\n")
    layout = [  [sg.Text("Current Rooms:\n" + text[1])],
                [sg.Text('Enter the room you want to join: '), sg.InputText()],
                [sg.Button('Stats'), sg.Button('Quit'), sg.Button('Join Room')] ]

    # Create the Window
    window.close()
    window = sg.Window('RPS Game', layout)
    return window

def gameInit(window):
    sg.theme('DarkAmber')
    layout = [  [sg.Text('Welcome to the Game Screen')],
                [sg.Button('Rock'), sg.Button('Paper'), sg.Button('Scissors')] ]

    # Create the Window
    window.close()
    window = sg.Window('RPS Game', layout)
    return window

def eventsCheck(event, values):
    sendString = ""
    if event == 'Quit': # if user closes window or clicks cancel
        #exit()
        pass
    if event == 'Enter':
        sendString = "login " + values[0] + " " + values[1]
    if event == 'Register':
        window = regInit(window)
    if event == 'Join Room':
        sendString = values[0]
    if event == 'Stats':
        sendString = "{stats}"
    return sendString

if __name__ == '__main__':
    ChatClient()
