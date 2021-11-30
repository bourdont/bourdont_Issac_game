import socket
import threading
import PySimpleGUI as sg

#client code
class ChatClient:
    def __init__(self, HOST: str = socket.gethostname(), PORT: int = 5555):
        self.address = (HOST, PORT)
        #self.connectToServer()
        #self.createRecievingThread()
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
        window = homeInit()
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
                break
            if event == 'Enter':
                print('You entered ', values[0])
                #self.sendMessage(values[0])
            if event == 'Next Page':
                window = gameInit(window)
                
            

#gui code
def homeInit():
    sg.theme('DarkAmber')
    layout = [  [sg.Text('Welcome to RPS')],
                [sg.Text('Enter your Username: '), sg.InputText()],
                [sg.Button('Enter'), sg.Button('Quit'), sg.Button('Next Page')] ]

    # Create the Window
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


if __name__ == '__main__':
    ChatClient()
