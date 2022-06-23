import socket
import threading
import tools
import commands

SERVER=socket.gethostbyname('localhost')
PORT = 5050
ADDR = (SERVER, PORT)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(usersManager, conn, addr):
    print("[NEW CONNECTION]", addr, " connected. Waiting validation ...")
    user = tools.User(conn, addr)
    connected = True
    
            





def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(start=handle_client, args=(usersManager, conn, addr))

usersManager = tools.UsersManager()
print("[STARTING] server is starting ...")
start(server)

