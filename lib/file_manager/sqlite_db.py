import sqlite3
from threading import Condition

class SQLite:
    def __init__(self,filepath):
        self.filepath = filepath

    def _open_table_check(self,tablename,data_format):
        # print('open_check',tablename)
        self.db = sqlite3.connect(self.filepath)
        self.cur = self.db.cursor()
        self.exe = self.cur.execute
        self.fa = self.cur.fetchall
        self.tablename = tablename
        table_contants = ','.join([f'{key} {value}' for key, value in data_format['column'].items()])
        unique_constraint = ','.join(data_format['unique_constraint'])
        txt = f"create table if not exists {self.tablename} ( {table_contants}, unique({unique_constraint})  );"
        # print(txt)
        self.exe(txt)

    def _open(self,tablename):
        # print('open_not_check',tablename)
        self.db = sqlite3.connect(self.filepath)
        self.cur = self.db.cursor()
        self.exe = self.cur.execute
        self.fa = self.cur.fetchall
        self.tablename = tablename

    def insert(self,data):
        print(f'insert or ignore into {self.tablename} values ({data});')
        self.exe(f'insert or ignore into {self.tablename} values ({data});')

    def update(self,data,sql_id):
        # print(f'update {self.tablename} set {data} where {sql_id};')
        self.exe(f'update {self.tablename} set {data} where {sql_id};')
    def commit(self):
        self.db.commit()

    def close(self):
        # self.db.commit()
        self.db.rollback()
        self.db.close()

    def upload_data(self,tablename,data,data_format):
        self._open_table_check(tablename,data_format)
        for idata in data:
            insert_txt = ' ,'.join(['null'] + idata)
            print(insert_txt)
            self.insert(insert_txt)
            self.commit()
        self.close()

    def update_data(self,tablename,data,data_format):
        self.open(tablename)
        for idata in data:
            update_txt = ','.join([f'{key} = {value}' for key, value in zip(data_format[2::],idata[2::])])
            sql_id = f'{data_format[0]} = {idata[0]} and {data_format[1]} = {idata[1]}'
            self.update(update_txt,sql_id)
            self.commit()
        self.close()
    
    def data_select(self,tablename,data_format,condition):
        self._open(tablename)
        column = ','.join(data_format)
        self.exe(f'select {column} from {self.tablename} {condition};')
        data = self.fa()
        # print(data)
        self.close()
        return data