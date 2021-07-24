#! /media/quance/black_03/Telegram_bot/venv/bin/python3
import logging
import os
import json
# from flask import Flask, request
from telegram import message
from lib.app import *
from lib.util.sys_config import logging_config_init,logging_start

@app.route('/hook/apiv1', methods=['POST'])

def proxy_send():
    """ get update to send messge """
    if request.method == "POST":
        logging.info(msg='recive auto update: {}'.format(request.content_type))
        group = request.args['group']
        logging.info(msg=f'group name {group}')
        if request.content_type == 'application/json':
            bi_data = request.data
            data = json.loads(bi_data.decode('utf-8'))
            message_handler(group=group,message=data['message'])
            # auto_handler(message=data['message'])
        elif request.content_type == 'image/jpeg':
            bi_data = request.data
            # image_handler_old(image=bi_data)
            image_handler(group,bi_data)
        
    return 'ok'


@app.route('/hook/api', methods=['POST'])

async def auto_update():
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
    # a = await mytime(10)
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
    app.run(debug=True,host='0.0.0.0')