import os
import time
import hashlib
import json
from datetime import datetime

def get_time_dir(source):
    return os.path.join(
        source,time.strftime('%Y_%m_%d')
    )

def get_time_dir_TEOM(source,datatime):
    return os.path.join(
        source,datatime.replace('-','_')
    )

def get_device_dir(source,code,y,m,identity):
    return os.path.join(
        source,"{}_{}_{}_{}".format(
            code,y,m,identity
        )
    )

def get_data_dir_with_time(source,datepath,code,y,m,identity):
    source = '/'.join([source,datepath])
    return get_device_dir(
        source,code,y,m,identity
    )

##   orignal
def get_data_dir(*args):
    root_path, serial_name, data_date = args
    data_date = data_date.strftime('%Y_%m_%d')
    return os.path.join(root_path, serial_name, data_date)

def get_db_name(*args):
    serial_name, data_date = args
    secure = hashlib.sha1()
    data = f"{serial_name}.{data_date:%Y-%m-%d}"
    secure.update(data.encode('utf-8'))
    return secure.hexdigest()

def exist_or_create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def exist_or_create_file(path):
    if ((not os.path.exists(path))
    or os.stat(path).st_size==0):
        with open(path,'w') as f:
            return f
    else:
        return path

def get_backup_path(path):
    o_dir = os.path.dirname(path)
    o_filename = os.path.basename(path)
    backup_file_path = os.path.join(o_dir,o_filename+'.bak')
    return backup_file_path

def get_log_path(source):
    filename = time.strftime('ideasky_sys_%Y_%m_%d.log')
    return os.path.join(source,filename)