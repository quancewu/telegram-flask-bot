import logging
import os,time
import queue
import threading
from .sqlite_db import SQLite
from lib.util.util import exist_or_create_dir,get_data_dir,get_db_name
from lib.util.sys_config import File

class SQLiteManager(threading.Thread):
    _save_queue = queue.Queue(maxsize=600)

    @classmethod
    def _call(cls,file_type,unique_code,data,data_format=None):
        cls._save_queue.put(
            (file_type,unique_code,data,data_format)
        )

    @classmethod
    def _get_date(cls,file_type,unique_code,data,data_format,condition):
        cls._save_queue.put(
            (file_type,unique_code,data,data_format,condition)
        )

    @classmethod
    def select_data(cls,unique_code,data,data_format,condition):
        cls._get_date('sqlite_select',unique_code,data,data_format,condition)

    @classmethod
    def insert_data(cls,unique_code,data,data_format):
        cls._call('sqlite_insert',unique_code,data,data_format)
    
    @classmethod
    def update_data(cls,unique_code,data,data_format):
        cls._call('sqlite_update',unique_code,data,data_format)

    @classmethod
    def delete_data(cls,unique_code,data,data_format):
        cls._call('sqlite_delete',unique_code,data,data_format)
    
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        logging.info('SQLite3 api upload init ...')

    def run(self):
        while 1:
            obj = SQLiteManager._save_queue.get()
            if len(obj) == 5:
                sql_type, unique_code, data, data_format, condition = obj
                if sql_type == 'sqlite_select':
                    data_dir = get_data_dir(
                        File.save_dir,*unique_code
                    )
                    exist_or_create_dir(data_dir)
                    filename = get_db_name(*unique_code)
                    file_path = os.path.join(data_dir,"{}.db".format(filename))
                    try:
                        local_sql = SQLite(file_path)
                        data_array = local_sql.data_select('data',data_format,condition)
                        if data_array != []:
                            data.put(data_array)
                        else:
                            data.put('no data')
                        logging.info(f'select data from sqlite db name {filename}')
                    except Exception as e:
                        logging.error(f'can not select data from sqlite db name {filename} with error {e}')
                else:
                    logging.error(f'sql_type ({sql_type}) not found')
            elif len(obj) == 4:
                sql_type, unique_code, data, data_format = obj
                if sql_type=='sqlite_insert':
                    data_dir = get_data_dir(
                        File.save_dir,*unique_code
                    )
                    exist_or_create_dir(data_dir)
                    filename = get_db_name(*unique_code)
                    file_path = os.path.join(data_dir,"{}.db".format(filename))
                    try:
                        local_sql = SQLite(file_path)
                        local_sql.upload_data('data',data,data_format)
                        # logging.info(f"data save path {file_path}")
                        # logging.info(f"data save to sqlite db name {filename}")
                    except Exception as e:
                        logging.error(f"data save path {file_path}")
                        logging.error(f"data save to sqlite db name {filename} with error {e}")
                elif sql_type == 'sqlite_update':
                    data_dir = get_data_dir(
                        File.save_dir,*unique_code
                    )
                    exist_or_create_dir(data_dir)
                    filename = get_db_name(*unique_code)
                    try:
                        file_path = os.path.join(data_dir,"{}.db".format(filename))
                        local_sql = SQLite(file_path)
                        local_sql.update_data('data',data,data_format)
                        # logging.info(f"data update path {file_path}")
                        # logging.info(f"data update to sqlite db name {filename}")
                    except Exception as e:
                        logging.error(f"data save path {file_path}")
                        logging.error(f"data can not update to sqlite db name {filename} with error {e}")
                else:
                    logging.error(f'sql_type ({sql_type}) not found')