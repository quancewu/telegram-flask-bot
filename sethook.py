import configparser
import os
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters ,Updater

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.ini'))
TOKEN = (config['TELEGRAM']['ACCESS_TOKEN'])
HOOK = 'hook'
PORT = 443
HOST = 'quance.ideasky.app' #'140.115.36.130'
CERT = '/media/quance/black_03/nginx_docker/ssl/cert.pem'
bot = telegram.Bot(TOKEN)
bot.setWebhook(url='https://%s:%s/%s' % (HOST, PORT, HOOK))

# bot.setWebhook(url='https://%s:%s/%s' % (HOST, PORT, HOOK),
#                    certificate=open(CERT, 'rb'))