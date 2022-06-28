from ctypes import alignment
from pickle import encode_long
from PyQt5.QtWidgets import QApplication, QFrame, QScrollArea, QGridLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont, QColor
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
    update_rooms = pyqtSignal(str)
    def __init__(self, conn, addr, user):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.user = user

    def run(self):
        connected=True

        #Validate Username from server
        self.user.sendMessage(commands.VALIDATE_USERNAME + " " + self.user.name)
        while connected:
            try:
                bytes_to_read = self.user.recieve(settings.HEADER, False)
                if bytes_to_read == 0:
                    raise errors.ConnectionLostException

            except(errors.ConnectionLostException):
                connected = False
                continue

            msg = self.user.recieve(bytes_to_read, True)

            if msg.startswith(commands.INVALID_USERNAME):
                connected = False
                print("[USER", self.addr, "] USERNAME VALIDATION FAILED.")
            elif msg.startswith(commands.VALID_USERNAME):
                self.user.validated = True
                self.switch_to_menu.emit()
                print("[USER", self.addr, "] USERNAME VALIDATION SUCCEEDED.")
            elif msg.startswith(commands.SEND_ROOMS):
                room_names = msg[len(commands.SEND_ROOMS)+1:]
                self.update_rooms.emit(room_names)

        print("[USER", self.addr, "] CONNECTION CLOSED.")
        self.conn.close()
                


class ChatState(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.user = User()
        self.init_window = InitWindow(self.onConnect)
        self.menu_window = MenuWindow(self)
        self.addWidget(self.init_window)
        self.addWidget(self.menu_window)
        self.setGeometry(100, 110, settings.WINDOWWIDTH, settings.WINDOWHEIGHT)

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
        self.connection.update_rooms.connect(self.update_rooms)
        self.connection.start()

    def update_rooms(self, rooms):
        print("[CLIENT-GUI] UPDATING ROOMS ...")
        self.menu_window.update_rooms(rooms.split(","))

    def switch_to_menu(self):
        print("[CLIENT-GUI] SWITCHING TO MENU ...")
        self.switchTo(Window.MENU.value)


    def clientSend(self, msg):
        self.user.send(msg)
        

    def switchTo(self, window):
        self.widget(window).prep()
        self.setCurrentIndex(window)
        

class InitWindow(QWidget):
    def __init__(self, onConnect):
        super().__init__()
        self.onConnect=onConnect
        self.initUI()

    def prep(self):
        pass

    def initUI(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
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


class RoomDisplay(QScrollArea):
    def __init__(self):
        super().__init__()
        self.rooms = set()
        self.initUI()
        
    
    def initUI(self):
        self.widget = QFrame()
        self.widget.setStyleSheet('''border: 3px solid white; border-radius: 10px''')
        self.layout = QVBoxLayout(self.widget)
        self.setWidgetResizable(True)
        self.widget.setAutoFillBackground(True)
        p = self.widget.palette()
        p.setColor(self.backgroundRole(), QColor.fromRgb(32, 32, 32))
        self.widget.setPalette(p)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)
        self.setWidget(self.widget)


    def update_rooms(self, rooms):
        room_cards = RoomFactory.buildRooms(rooms)
        for i, card in enumerate(room_cards):
            self.layout.addWidget(card)


class RoomCard(QFrame):
    def __init__(self, room_name, color):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.setStyleSheet('''border: 3px solid grey; border-radius: 10px''')
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.label = QLabel("ROOM: " + room_name)
        self.label.setStyleSheet('''border:None; font-size: 18px''')
        self.layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.layout.addWidget(self.label)
        self.setColor(color)

    def setColor(self, color):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)


class RoomFactory:
    @staticmethod
    def buildRooms(rooms):
        res = []
        color = [QColor(128, 128, 128), QColor(160, 160, 160)]
        pos = 0
        for room in rooms:
            res.append(RoomCard(room, color[pos]))
            pos = (pos+1)%2
        return res



class RoomButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.connect_btn = QPushButton("Connect")
        self.create_room_btn = QPushButton("Create Room")
        self.layout.addWidget(self.connect_btn)
        self.layout.addWidget(self.create_room_btn)

class UsersOnline(QScrollArea):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWidgetResizable(True)
        self.widget = QFrame()
        self.widget.setStyleSheet('''background-color: rgb(0, 0, 0); border: 3px solid white; border-radius: 10px;''')
        self.label = QLabel("Users Online")
        self.label.setStyleSheet('''border:None; color:white''')
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.layout.addWidget(self.label)

        self.setWidget(self.widget)


class MenuWindow(QWidget):
    def __init__(self, chat_state):
        super().__init__()
        self.chat_state = chat_state
        self.layout = QGridLayout(self)
        self.room_controls = RoomButtons()
        self.rooms_display = RoomDisplay()
        self.users_online = UsersOnline()
        
        self.initUI()
    def initUI(self):

        self.layout.setContentsMargins(40, 40, 40, 40)
        self.heading= QLabel("[Rooms]")
        self.heading.setStyleSheet('''border:None; font-size: 32px''')

        self.layout.addWidget(self.heading, 0, 2, 1, 1)
        self.layout.addWidget(self.rooms_display, 1, 0, 4, 4)
        self.layout.addWidget(self.room_controls, 6, 0, 1, 4)
        self.layout.addWidget(self.users_online, 1, 6, 4, 2)


        # self.layout.setColumnStretch(6, 5)
        # self.layout.setRowStretch(1, 5)
        # self.layout.setColumnStretch(0, 10)
        # self.layout.setColumnStretch(3, 8)


        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
    
    def update_rooms(self, rooms):
        self.rooms_display.update_rooms(rooms)


    
    def prep(self):
        pass
        # self.info.setText("Connected with username: " + self.chat_state.user.name)

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
                res = self.conn.recv(bytes_to_read).decode(settings.FORMAT)
                print("[USER", self.addr, "] Recieved message: '", res, "' from server.")
                return res
            
            res = int.from_bytes(self.conn.recv(bytes_to_read), "little")
            print("[USER", self.addr, "] Recieved a header of '", res, "' bytes from the server.")

            return res
        except: 
            print("[USER", self.addr, "] Has lost connection to the server")
            raise errors.ConnectionLostException

    
    def sendMessage(self, msg):
        bytes_to_send = len(msg)
        self.conn.send(bytes_to_send.to_bytes(8, "little"))
        print("[USER", self.addr, "] Has sent '", bytes_to_send, "' bytes as a header to the server.")
        self.conn.send(msg.encode(settings.FORMAT))
        print("[USER", self.addr, "] Has sent '", msg, "' to the server.")
    



