from telegram import Update
import re

class Message:
    def __init__(self, update: Update):
        self.user = User(update.message.forward_from or update.message.forward_sender_name)
        self.text = re.sub(r'(https?)\S*', '(link)', update.message.text)

class User:
    def __init__(self, user):
        if (isinstance(user, str)):
            self.name = user
            self.id = user
        else:
            self.name = user.first_name
            self.id = user.id