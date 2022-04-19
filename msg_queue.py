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
    @staticmethod
    def estimate_time(self,thread):
        eta = 0 
        # amount of seconds for one char
        char_rate = 0.089
        # amount of seconds for one evidence
        evidence_rate = 2
        total_chars = 0
        evidences = 0
        for item in thread :
            total_chars += len(item.text_content)
            # Populates character length
            if not item.evidence_path == None:
                evidences += 1
                # Populates evidences 
        time_from_chars = char_rate * total_chars
        time_from_evidence = evidence_rate * evidences
        eta += time_from_chars
        eta += time_from_evidence
        return round(float(eta) , 2)

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
        # Thread is populated
        output_filename = str(self.chatId) + '.mp4'
        self.updater.bot.send_chat_action(self.chatId, ChatAction.RECORD_VIDEO)
        eta_secs = self.estimate_time(self,thread)
        self.updater.bot.send_message(
            self.chatId,
            text=(
                'Started processing video.\n\n'
                f'ETA: {int(eta_secs/60)} min(s) {round(eta_secs%60,2)} secs.'))
        render_comment_list(thread, output_filename=output_filename, resolution_scale=2)
        self.updater.bot.send_message(
            self.chatId,
            text=('Finished processing video. Uploading ... '))
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
