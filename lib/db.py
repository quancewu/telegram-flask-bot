import time
import threading
import logging
from lib.file_manager.sqliteapi import SQLiteManager
from lib.job import Job_Service

class SQLite_Service():
    def __init__(self):
        self.SQLiteapi = SQLiteManager()
        # self.process_pool = Job_Service()
    def run(self):
        self.SQLiteapi.start()
        logging.info('SQLite Service starting up ....')
        # self.process_pool.start()
        # logging.info('process_pool Service starting up ....')
