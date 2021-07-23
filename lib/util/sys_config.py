import os
import yaml
import logging.config
from .util import exist_or_create_dir

class Telegram_config:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_dir = os.path.join(base_dir,'config')
    with open(os.path.join(config_dir,'config.yaml'),'r', encoding='utf-8') as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)
    all_config = config_file
    # config = config_file['config']
    # sql_data_format = config_file['sql_data_format']
    # def save_new_config(config):
    #     base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #     config_dir = os.path.join(base_dir,'config')
    #     with open(os.path.join(config_dir,'cn2_v2_config.yaml'),'r', encoding='utf-8') as f:
    #         old_config_file = yaml.load(f, Loader=yaml.FullLoader)
    #     old_config_file['config'] = config
    #     with open(os.path.join(config_dir,'cn2_v2_config.yaml'), 'w') as file:
    #         documents = yaml.dump(old_config_file, file, sort_keys=False)
    #     print('save config with cn2_v2_config')

class SQL_config:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_dir = os.path.join(base_dir,'config')
    with open(os.path.join(config_dir,'user_schema.yaml'),'r', encoding='utf-8') as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)
    user_format = config_file['sql_data_format']
    with open(os.path.join(config_dir,'group_schema.yaml'),'r', encoding='utf-8') as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)
    group_format = config_file['sql_data_format']

def logging_config_init(ex_path):
    # ex_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(ex_path,'config','logging.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config['handlers']['info_file_handler']['filename'] = os.path.join(ex_path,'log_file','debug.log')
    config['handlers']['error_file_handler']['filename'] = os.path.join(ex_path,'log_file','errors.log')
    with open(path, 'w') as file:
        documents = yaml.dump(config, file)

def logging_start(ex_path):
    # ex_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(ex_path,'config','logging.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        logging.config.dictConfig(config)
    logger = logging.getLogger('Telegram bot')

class File:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_dir = os.path.join(base_dir,'config')
    log_dir = os.path.join(base_dir,'log_file')
    fig_dir = os.path.join(base_dir,'fig')
    save_dir = os.path.join(base_dir,'data_file')
    script_dir = os.path.join(base_dir,'script_n_file')
    # with open(os.path.join(config_dir,'filepath.yaml'),'r', encoding='utf-8') as f:
    #     config_file = yaml.load(f, Loader=yaml.FullLoader)
    # data_dir = config_file['data_dir']

    exist_or_create_dir(base_dir)
    exist_or_create_dir(config_dir)
    exist_or_create_dir(log_dir)
    exist_or_create_dir(save_dir)