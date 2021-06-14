import threading
from telegram import Update
from message import Message
from objection_engine.renderer import render_comment_list
from typing import List
import os
from telegram.ext import Updater
from telegram import ChatAction


class Queue:
    def __init__(self, update: Update, chatList, updater: Updater):
        self.update = update
        self.messages: List[Message] = []
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
        self.chatList[self.chatId] = None
        for message in self.messages:
            thread.append(message.to_message())
        output_filename = str(self.chatId) + '.mp4'
        self.updater.bot.send_chat_action(self.chatId, ChatAction.RECORD_VIDEO)
        render_comment_list(thread, output_filename=output_filename)
        with open(output_filename, 'rb') as video:
            self.updater.bot.send_chat_action(self.chatId, ChatAction.UPLOAD_VIDEO)
            self.update.message.reply_video(video, timeout=120)
        self.clean(output_filename, thread)
    def clean(self, output_filename: str, thread: list):
        try:
            os.remove(output_filename)
        except Exception as e:
            print(e)
        for msg in thread:
            try:
                os.remove(msg.evidence_path)
            except Exception as e:
                print(e)