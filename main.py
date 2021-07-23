#! /usr/bin/python3
import logging
import os
import traceback
import html
import json
import telegram
from flask import Flask, request
from telegram.ext import jobqueue
# from telegram import ReplyKeyboardMarkup, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import (Updater, CommandHandler, MessageHandler,  CallbackQueryHandler,
#     Filters, CallbackContext, Dispatcher)
from lib.app import *
from lib.db import SQLite_Service
from lib.job import Job_Service
from lib.util.sys_config import Telegram_config,logging_config_init,logging_start

app = Flask(__name__)

DEVELOPER_CHAT_ID = Telegram_config.all_config['Telegram']['Developer_chat_id']

# db = SQLite_Service().run()
# process_pool = Job_Service().start()

@app.route('/hook/api', methods=['POST'])

def auto_update():
    """ get update to send messge """
    if request.method == "POST":
        logging.info(msg='recive auto update: {}'.format(request.content_type))
        if request.content_type == 'application/json':
            bi_data = request.data
            data = json.loads(bi_data.decode('utf-8'))
            auto_handler(message=data['message'])
        elif request.content_type == 'image/jpeg':
            bi_data = request.data
            image_handler(image=bi_data)
        
    return 'ok'

@app.route('/hook', methods=['POST'])

def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

if __name__ == "__main__":
    ex_path = os.path.dirname(os.path.abspath(__file__))
    logging_config_init(ex_path)
    logging_start(ex_path)
    db = SQLite_Service().run()
    process_pool = Job_Service().start()
    app.run(debug=True,host='0.0.0.0')