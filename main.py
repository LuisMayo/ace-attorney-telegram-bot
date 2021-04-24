#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import sys
sys.path.insert(0, './ace-attorney-reddit-bot')

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from msg_queue import Queue

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

queueList = {}


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! This is a bot that will transform a group of Telegram messages into Ace Attorney scenes. Just forward me the messages')


def about_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Made with ❤ by @TLuigi003.\nSource code in https://github.com/LuisMayo/ace-attorney-telegram-bot\n\nDo you like my work? You could thank me by buying me a [ko-fi](https://ko-fi.com/luismayo)', parse_mode="Markdown")


def getMessage(update: Update, context: CallbackContext) -> None:
    global updater
    if (not update.message.chat.id in queueList or queueList[update.message.chat.id] == None):
        queueList[update.message.chat.id] = Queue(update, queueList, updater)
    queueList[update.message.chat.id].addMessage(update)

def main():
    with open('token.txt', 'r') as tokenFile:
        token = tokenFile.read().replace('\r', '').replace('\n', '')
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    global updater
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("about", about_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler((Filters.text | Filters.photo) & ~Filters.command, getMessage))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
