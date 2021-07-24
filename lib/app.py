import logging
import queue
import time
import traceback
import html
import json
import telegram
from datetime import datetime
from telegram import ReplyKeyboardMarkup, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Updater, CommandHandler, MessageHandler,  CallbackQueryHandler,
    Filters, CallbackContext, Dispatcher)
from lib.file_manager.sqliteapi import SQLiteApi
from lib.job import Job_Service
from flask import Flask, request, current_app
from lib.lock import Lock
from flask_executor import Executor
# from telegram_bot import *
from lib.fn import mytimer

from lib.util.sys_config import Telegram_config,SQL_config

DEVELOPER_CHAT_ID = Telegram_config.all_config['Telegram']['Developer_chat_id']

bot = telegram.Bot(token=Telegram_config.all_config['Telegram']['Access_token'])

app = Flask(__name__)
app.lock = Lock.get_file_lock()

executor = Executor(app)
app.config['EXECUTOR_TYPE'] = 'thread'
# app.config['EXECUTOR_MAX_WORKERS'] = 5
SQLiteApi = SQLiteApi()

welcome_message = "Hello world it's quance's toys\n\n" \
                "You can see Qlog_sys log report in here\n\n" \
                "You can control me by sending these commands:\n\n" \
                "/start - see this manual\n" \
                "/register - register to this telegram bot\n" \
                "/group - subscrible message for user or group\n" \
                "/help - see this message"

group_dict = {  
                "group_01": "CAlab admin",
                "group_02": "Group 02",
                "group_03": "Group 03",
            }

reply_keyboard_markup = ReplyKeyboardMarkup([['Today Error log','Log',],
                                             ['is good ?','/group']])
Inline_keyboard_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("CAlab admin", callback_data='group_01'),
            InlineKeyboardButton("Group 02", callback_data='group_01'),
        ],
        [   InlineKeyboardButton("Group 03", callback_data='group_03')],
    ])

def start_handler(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    logging.info("User %s, %s started the conversation.", user.first_name,user.last_name)
    update.message.reply_text(welcome_message, reply_markup=reply_keyboard_markup)
    logging.info("chat id: %s",update.message.chat_id)
    
def help_handler(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(welcome_message, reply_markup=reply_keyboard_markup)

def register_handler(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    logging.info("User %s, %s register to system", user.first_name,user.last_name)
    update.message.reply_text(welcome_message)#, reply_markup=reply_keyboard_markup)
    logging.info("chat id: %s",update.message.chat_id)
    chat_type, chat_name = (0, 'null') if not update.message.chat.title else (1, update.message.chat.title)
    data = [[f"'{user.first_name}'",f"'{user.last_name}'",f"'{update.message.chat_id}'",f"'{chat_name}'",f"{chat_type}"]]
    # print(data)
    current_app.lock.acquire()  
    SQLiteApi.insert_data(('user',datetime(2020,1,1)),data,SQL_config.user_format)
    current_app.lock.release()
    
def group_handler(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /setgroup is issued."""
    user = update.message.from_user
    group_setup_message =  f"Hello {user.first_name}, {user.last_name}\n\n" \
                        "Here is auto bot "
    update.message.reply_text(group_setup_message, reply_markup=Inline_keyboard_markup)

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    group_reply = group_dict[query.data]

    user = update.callback_query.from_user
    logging.info("chat id: %s",user.id)
    chat_type, chat_name = (0, 'null') if not update.callback_query.message.chat.title \
                                        else (1, update.callback_query.message.chat.title)
    data = [[f"'{user.first_name}'",f"'{user.last_name}'",f"'{update.callback_query.message.chat_id}'",f"'{chat_name}'",f"{chat_type}"]]
    print(data)
    current_app.lock.acquire()  
    SQLiteApi.insert_data((f'{query.data}',datetime(2020,1,1)),data,SQL_config.group_format)
    current_app.lock.release()

    logging.info("User %s, %s register to group %s", user.first_name,user.last_name,group_reply)

    query.edit_message_text(text=f"Selected group: {group_reply}")

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def alarm(context):
    """Send the alarm message."""
    task = context.result()
    bot.send_message(task['chat_id'], text=task['message'])

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def mytime(times):
    time.sleep(times)
    return times

def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        
        # Job_Service.add_job(chat_id,due,alarm)
        executor.submit(mytimer,(chat_id,due)).add_done_callback(alarm)
        # job_removed = remove_job_if_exists(str(chat_id), context)
        # context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        
        # if job_removed:
        #     text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def message_handler(group=DEVELOPER_CHAT_ID, message='') -> None:
    current_app.lock.acquire()  
    chat_list = SQLiteApi.select_data((f'{group}',datetime(2020,1,1)),
                                SQL_config.group_format,
                                'order by 1')
    current_app.lock.release()
    print(chat_list)
    if chat_list != 'no data':
        for ichat in chat_list:
            bot.send_message(chat_id=ichat[3] ,text=message)

def auto_handler(message) -> None:
    # message = 'test for auto'
    bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message)
    # bot.send_message(chat_id='-1001275188916', text=message)

def image_handler(group, image) -> None:
    current_app.lock.acquire()
    chat_list = SQLiteApi.select_data((f'{group}',datetime(2020,1,1)),
                                SQL_config.group_format,
                                'order by 1')
    current_app.lock.release()
    print(chat_list)
    if chat_list != 'no data':
        for ichat in chat_list:
            bot.send_photo(chat_id=ichat[3], photo=image)

def image_handler_old(image):
    bot.send_photo(chat_id=DEVELOPER_CHAT_ID, photo=image)

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

def bad_command(update: Update, context: CallbackContext) -> None:
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()  # type: ignore[attr-defined]

dispatcher = Dispatcher(bot, None,workers=12)
# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('register', register_handler))
dispatcher.add_handler(CommandHandler('group', group_handler))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler('bad_command', bad_command))
dispatcher.add_handler(CommandHandler("set", set_timer))
dispatcher.add_handler(CommandHandler("unset", unset))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
dispatcher.add_error_handler(error_handler)
