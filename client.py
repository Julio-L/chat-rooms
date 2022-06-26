from pickle import encode_long
from PyQt5.QtWidgets import QApplication, QGridLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from enum import Enum
from threading import Thread
import socket
import settings
import errors
import commands

class Window(Enum):
    INIT = 0
    MENU = 1
    ROOM = 2

class Worker(QThread):
    switch_to_menu = pyqtSignal()
    def __init__(self, conn, addr, user):
        super().__init__()
        
        self.conn = conn
        self.addr = addr
        self.user = user

    def run(self):
        connected=True
        

        #Check is username is valid
        self.user.sendMessage(commands.VALIDATE_USERNAME + " " + self.user.name)

        while connected:
            try:
                bytes_to_read = self.user.recieve(settings.HEADER, False)
            except(errors.ConnectionLostException):
                connected = False
                continue
            if bytes_to_read == 0:
                continue

            msg = self.user.recieve(bytes_to_read, True)
            print("BYTES TO READ", bytes_to_read)
            if msg.startswith(commands.INVALID_USERNAME):
                connected = False
            elif msg.startswith(commands.VALID_USERNAME):
                self.user.validated = True
                self.switch_to_menu.emit()
        self.conn.close()
                


class ChatState(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.user = User()
        self.init_window = InitWindow(self.onConnect)
        self.menu_window = MenuWindow(self)
        self.addWidget(self.init_window)
        self.addWidget(self.menu_window)

    def closeEvent(self, event):
        if self.user.conn:
            self.user.sendMessage(commands.DISCONNECT)
    
    def onConnect(self):        
        SERVER = socket.gethostbyname('localhost')
        ADDR = (SERVER, settings.PORT)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)

        username = self.init_window.user_input.text()
        self.user.name = username

        self.user.conn = client
        self.user.addr = ADDR

        self.connection = Worker(client, ADDR, self.user)
        self.connection.switch_to_menu.connect(self.switch_to_menu)
        self.connection.start()

    def switch_to_menu(self):
        self.switchTo(Window.MENU.value)


    def clientSend(self, msg):
        self.user.send(msg)
        

    def switchTo(self, window):
        self.setCurrentIndex(window)
        

class InitWindow(QWidget):
    def __init__(self, onConnect):
        super().__init__()
        self.onConnect=onConnect
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Username: ")
        self.user_input = QLineEdit()
        self.input_section = QWidget()
        self.input_layout = QHBoxLayout(self.input_section)
        self.input_layout.setSpacing(15)
    
        self.input_layout.addWidget(self.label)
        self.input_layout.addWidget(self.user_input)
        self.input_section.setFixedWidth(420)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.onConnect)
        self.connect_button.setFixedWidth(100)
        self.user_input.setFixedWidth(200)
        self.input_layout.addWidget(self.connect_button)


        self.heading_section = QWidget()
        self.heading_layout = QVBoxLayout(self.heading_section)
        self.heading = QLabel("[Chat Rooms]")
        self.font = QFont("Times", 50, QFont.Bold)
        self.heading.setFont(self.font)

        self.dev = QLabel("Developed by: Julio Lima")
        self.dev_font = QFont("Times", 20, QFont.Bold)
        self.dev.setFont(self.dev_font)

        self.heading_layout.addWidget(self.heading)
        self.heading_layout.addWidget(self.dev)
        self.heading_layout.setSpacing(10)
        self.heading.setContentsMargins(0, 0, 0, 0)
        self.dev.setContentsMargins(0, 0, 0, 0)
        self.heading_layout.setAlignment(Qt.AlignCenter)


        self.layout.addWidget(self.heading_section)
        self.layout.addWidget(self.input_section)
        self.layout.setSpacing(50)
        self.layout.setAlignment(Qt.AlignCenter)

        self.setFixedHeight(700)
        self.setFixedWidth(700)




class MenuWindow(QWidget):
    def __init__(self, chat_state):
        super().__init__()
        self.layout = QGridLayout(self)
        self.chat_state = chat_state
        self.info = QLabel("Connected with username: " + self.chat_state.user.name)
        self.layout.addWidget(self.info, 0, 0)

class ChatWindow(QWidget):
    pass
    

class User:
    def __init__(self, name="", conn=None, addr=None):
        self.name = name
        self.conn = conn
        self.addr = addr
        self.validated = False
    
    def recieve(self, bytes_to_read, decode=False):
        try:
            if decode:
                return self.conn.recv(bytes_to_read).decode(settings.FORMAT)
            
            return int.from_bytes(self.conn.recv(bytes_to_read), "little")
        except: 
            raise errors.ConnectionLostException

    
    def sendMessage(self, msg):
        bytes_to_send = len(msg)
        self.conn.send(bytes_to_send.to_bytes(8, "little"))
        self.conn.send(msg.encode(settings.FORMAT))
    



