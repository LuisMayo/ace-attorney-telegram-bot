import threading
from comment_list_bridge import Comment
from collections import Counter 
from telegram import Update
from message import Message
import anim
import os
from telegram.ext import Updater
from telegram import ChatAction


class Queue:
    def __init__(self, update: Update, chatList, updater: Updater):
        self.update = update
        self.messages = []
        self.chatId = update.message.chat.id
        self.chatList = chatList
        self.lastSchedule = None
        self.updater = updater

    def addMessage(self, update):
        if (update.message.forward_from != None or update.message.forward_sender_name != None):
            self.messages.append(Message(update, self.updater))
            if (self.lastSchedule != None):
                self.lastSchedule.cancel()
            self.lastSchedule = threading.Timer(5.0, self.createVideo)
            self.lastSchedule.start()
        else:
            update.message.reply_text('You have to forward me a group of messages')
    
    def createVideo(self):
        self.updater.bot.send_chat_action(self.chatId, ChatAction.RECORD_VIDEO)
        thread = []
        users_to_names = {}
        counter = Counter()
        self.chatList[self.chatId] = None
        for message in self.messages:
            thread.append(Comment(message))
            users_to_names[message.user.id] = message.user.name
            counter.update({message.user.id: 1})
        if (len(users_to_names) >= 2): 
            most_common = [users_to_names[t[0]] for t in counter.most_common()]
            characters = anim.get_characters(most_common)
            output_filename = str(self.chatId) + '.mp4'
            self.updater.bot.send_chat_action(self.chatId, ChatAction.RECORD_VIDEO)
            anim.comments_to_scene(thread, characters, output_filename=output_filename)
            with open(output_filename, 'rb') as video:
                self.updater.bot.send_chat_action(self.chatId, ChatAction.UPLOAD_VIDEO)
                self.update.message.reply_video(video, timeout=120)
            self.clean(output_filename, thread)
        else:
            self.update.message.reply_text("There should be at least two people in the conversation")
            self.clean(output_filename, thread)
    def clean(self, output_filename: str, thread: list):
        try:
            os.remove(output_filename)
        except Exception as e:
            print(e)
        try:
            for msg in thread:
                os.remove(msg.evidence)
        except Exception as e:
            print(e)