from PyQt5.QtWidgets import QApplication
from client import ChatState

app = QApplication([])

chat_state = ChatState()
chat_state.show()

app.exec()

