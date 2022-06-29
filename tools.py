from re import L
import commands
import settings
import errors

class Room:
    def __init__(self, name_id):
        self.name_id = name_id
        self.users = {}
    
    def addUser(self, user):
        if user.username in self.users:
            print("[SERVER] TRIED ADDING USER TO ROOM " + self.name_id + ", BUT USER[", (user.conn, user.addr), "] IS ALREADY IN THE ROOM.")
            return False
        else:
            print("[SERVER] ADDED USER[", (user.conn, user.addr), "] TO ROOM " + self.name_id)
            self.users[user.username] = user
        return True

    def removeUser(self, user):
        print("[SERVER] REMOVED USER[", (user.conn, user.addr), "] FROM ROOM " + self.name_id)
        self.users.pop(user.username, None)
        return True

    def sendToAll(self, msg):
        pass        

class User:
    def __init__(self, conn, addr, username=""):
        self.username = username
        self.valid = False
        self.conn = conn
        self.addr = addr
        self.room = None
    
    def validate(self, usersManager):
        print("[SERVER] VALIDATING USER", self.addr)
        if usersManager.isvalidname(self.username):
            self.valid = True
        
        return self.valid

    def __str__(self):
        return "USER[" + str((self.conn, self.addr)) + "]"

    def send(self, msg):
        bytes_to_send = len(msg) 
        self.conn.send(bytes_to_send.to_bytes(8, "little"))
        print("[SERVER -> USER:'", self.addr, "'] HAS SENT '", bytes_to_send, "' BYTES AS A HEADER.")
        self.conn.send(msg.encode(settings.FORMAT))
        print("[SERVER -> USER:'", self.addr, "'] HAS SENT '", msg, "'.")
    
    
    def recieve(self,bytes_to_read, decode=False):
        if not decode:
            print("[USER:'",self.addr   ,"' -> SERVER] RECIEVED '", bytes_to_read,"' BYTES AS A HEADER." )
            res = int.from_bytes(self.conn.recv(bytes_to_read), "little")
            return res

        res = self.conn.recv(bytes_to_read).decode(settings.FORMAT)
        print("[USER:'",self.addr   ,"' -> SERVER] RECIEVED A MESSAGE '", res ,"'." )

        return res


class UsersManager:
    def __init__(self):
        self.registered_users = {}

    def isvalidname(self, name):
        self.valid = name not in self.registered_users
        return self.valid
    
    def addUser(self, user):
        self.registered_users[user.username] = user
    
    def removeUser(self, user):
        self.registered_users.pop(user.username, None)

class RoomsManager:
    def __init__(self, init_room_count):
        #Fix hardcoded values
        self.default_names = ["General", "Manga/Anime", "Random"]
        self.rooms = {self.default_names[room_number]:Room(str(room_number)) for room_number in range(init_room_count)}

    def comma_sep_room_names(self):
        return ",".join(self.rooms)

    def addUser(self, user, room):
        if not room in self.rooms:
            print("[SERVER] TRIED ADDING " + user + " TO ROOM " + room + ", BUT IT DOES NOT EXIST")
            return False
        room = self.rooms[room]
        room.addUser(user)
        return True
    
    def removeUser(self, user, room):
        if not room in self.rooms:
            print("[SERVER] TRIED REMOVING " + user + " TO ROOM " + room + ", BUT IT DOES NOT EXIST")
            return False
        room = self.rooms[room]
        room.removeUser(user)



class ChatManager:
    def __init__(self, total_rooms):
        self.usersManager = UsersManager()
        self.roomsManager = RoomsManager(total_rooms)
        
    def exec_command(self, user, command):
        # if not user.valid:
        #     raise InvalidUsernameException
        if command.startswith(commands.CHAT):
            pass
        elif command.startswith(commands.DISCONNECT):
            self.usersManager.removeUser(user)
            raise errors.DisconnectedException
        elif command.startswith(commands.VALIDATE_USERNAME):
            username = command[len(commands.VALIDATE_USERNAME)+1:]
            user.username = username
            valid = user.validate(self.usersManager)
            if valid:
                print("[SERVER] VALIDATION SUCCESSFUL FOR USER", user.addr)
                self.usersManager.addUser(user)
                user.send(commands.VALID_USERNAME)
                user.send(commands.SEND_ROOMS + " " + self.roomsManager.comma_sep_room_names())
            else:
                print("[SERVER] VALIDATION UNSUCCESSFUL FOR USER", user.addr)
                user.send(commands.INVALID_USERNAME)
                raise errors.InvalidUsernameException
        elif command.startsWith(commands.JOIN_ROOM):
            pass
        elif command.startsWith(commands.LEAVE_ROOM):
            pass



