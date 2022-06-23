import socket 
import threading
import settings


SERVER = socket.gethostbyname('localhost')
ADDR = (SERVER, settings.PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

client.send(len("!CHAT Hello World!").to_bytes(8, 'little'))
client.send("!CHAT Hello World!".encode(settings.FORMAT))

client.send(len("!DISCONNECT").to_bytes(8, 'little'))
client.send("!DISCONNECT".encode(settings.FORMAT))