from objection_engine.beans.comment import Comment
from telegram import Update
import re

class Message:
    def __init__(self, update: Update, updater):
        if (len(update.message.photo) > 0):
            possible_text = update.message.caption
            photo = get_closest(update.message.photo, [85, 85])
            file_id = photo.file_id
            self.downloadEvidence(updater, file_id, photo.file_unique_id)
        elif (update.message.sticker is not None):
            possible_text = None
            self.downloadEvidence(updater, update.message.sticker.file_id, update.message.sticker.file_unique_id)
        else:
            possible_text = update.message.text
            self.evidence = None
        self.text = re.sub(r'(https?)\S*', '(link)', possible_text or '...')
        self.user = User(update.message.forward_from or update.message.forward_sender_name)

    def downloadEvidence(self, updater, file_id, unique_id):
        newFile = updater.bot.get_file(file_id)
        file_name = unique_id + '.png'
        newFile.download(file_name)
        self.evidence = file_name
    
    def to_message(self):
        return Comment(text_content=self.text, user_id=self.user.id, user_name=self.user.name, evidence_path=self.evidence)

class User:
    def __init__(self, user):
        if (isinstance(user, str)):
            self.name = user
            self.id = None
        else:
            self.name = user.first_name
            self.id = user.id

# From python-telegram-bot documentation
def get_closest(photos, desired_size):
    def diff(p): return p.width - desired_size[0], p.height - desired_size[1]
    def norm(t): return abs(t[0] + t[1] * 1j)
    return min(photos, key=lambda p:  norm(diff(p)))
