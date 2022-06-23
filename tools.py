import commands
import settings

class InvalidUsernameException(Exception):
    pass

class DisconnectedException(Exception):
    pass

class Room:
    pass

class User:
    def __init__(self, conn, addr, username=""):
        self.username = username
        self.valid = False
        self.conn = conn
        self.addr = addr
        self.room = None
    
    def validate(self, usersManager):
        if usersManager.isvalidname(self.username):
            self.valid = True
        
        return self.valid
    
    def recieve(self,bytes_to_read, decode=False):
        if not decode:
            return int.from_bytes(self.conn.recv(bytes_to_read), "little")

        return self.conn.recv(bytes_to_read).decode(settings.FORMAT)


class UsersManager:
    def __init__(self):
        self.registered_users = {}

    def isvalidname(self, name):
        return name not in self.registered_names

class ChatManager:
    def __init__(self, total_rooms):
        self.usersManager = UsersManager()
        self.rooms = {room_number:Room() for room_number in range(total_rooms)}
    def exec_command(self, user, command):
        # if not user.valid:
        #     raise InvalidUsernameException
        if command.startswith(commands.CHAT):
            print("[USER", user.addr, "]" + command)
        elif command.startswith(commands.DISCONNECT):
            raise DisconnectedException

