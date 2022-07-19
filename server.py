import socket
import threading
import tools
import commands
import settings
import errors

SERVER=socket.gethostbyname('localhost')
ADDR = (SERVER, settings.PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(chatManager, conn, addr):
    print("[NEW CONNECTION]", addr, " connected.")
    user = tools.User(conn, addr, chatManager)
    connected = True

    while connected:
        bytes_to_read = user.recieve(settings.HEADER, False)
        print(bytes_to_read)
        if bytes_to_read == 0:
            connected = False
            chatManager.exec_command(user, commands.DISCONNECT)
            break
        
        print("[USER", addr, "] has sent", bytes_to_read, " bytes")
        command = user.recieve(bytes_to_read, decode=True)

        try:
            print("[SERVER] EXECUTING COMMANS: '", command, "' FOR USER", user.addr)
            chatManager.exec_command(user, command)
        except (Exception, errors.InvalidUsernameException, errors.DisconnectedException):
            print("[USER", addr, "] DISCONNECTED.")
            connected = False
        
        if not user.connected:
            connected = False
            continue
            

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(chatManager, conn, addr))
        thread.start()


chatManager = tools.ChatManager(3)
print("[STARTING] server is starting ...")
start()

server.close()