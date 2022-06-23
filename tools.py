import commands

class InvalidUsernameException(Exception):
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
        if decode:
            return self.conn.recieve(bytes_to_read)

        return self.conn.recieve(bytes_to_read).decode(commands.FORMAT)


class UsersManager:
    def __init__(self):
        self.registered_users = {}

    def isvalidname(self, name):
        return name not in self.registered_names

class ChatState:
    def __init__(self, total_rooms):
        self.usersManager = UsersManager()
        self.rooms = {room_number:Room() for room_number in range(total_rooms)}
        