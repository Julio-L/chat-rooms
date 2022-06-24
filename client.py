from PyQt5.QtWidgets import QApplication, QGridLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from enum import Enum
from threading import Thread
import socket
import settings

class Window(Enum):
    INIT = 0
    MENU = 1
    ROOM = 2

class ChatState(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.init_window = InitWindow(self.onConnect)
        self.menu_window = MenuWindow()
        self.addWidget(self.init_window)
        self.addWidget(self.menu_window)
        self.user = UserManager()
    
    def onConnect(self):        
        SERVER = socket.gethostbyname('localhost')
        ADDR = (SERVER, settings.PORT)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)

        self.recieve = Thread(target=ChatState.clientRecieve, args=(self, client))
        self.recieve.start()
        self.recieve.join()
        client.close()


    def clientSend(self):
        pass
    
    def clientRecieve(chat_state, client):
        pass

    def switchToMenu(self):
        self.setCurrentIndex(Window.MENU.value)
        

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
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)


class ChatWindow(QWidget):
    pass
    

class UserManager:
    def __init__(self, name="", client=None):
        pass

