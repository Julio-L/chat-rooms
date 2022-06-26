import commands
import settings
import errors

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

    def send(self, msg):
        bytes_to_send = len(msg) 
        self.conn.send(bytes_to_send.to_bytes(8, "little"))
        self.conn.send(msg.encode(settings.FORMAT))

    
    def recieve(self,bytes_to_read, decode=False):
        if not decode:
            return int.from_bytes(self.conn.recv(bytes_to_read), "little")

        return self.conn.recv(bytes_to_read).decode(settings.FORMAT)


class UsersManager:
    def __init__(self):
        self.registered_users = {}

    def isvalidname(self, name):
        self.valid = name not in self.registered_users
        return self.valid
    
    def addUser(self, name, user):
        self.registered_users[name] = user

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
            raise errors.DisconnectedException
        elif command.startswith(commands.VALIDATE_USERNAME):
            username = command[len(commands.VALIDATE_USERNAME)+1:]
            user.username = username
            valid = user.validate(self.usersManager)
            if valid:
                user.send(commands.VALID_USERNAME)
            else:
                user.send(commands.INVALID_USERNAME)
                raise errors.InvalidUsernameException


