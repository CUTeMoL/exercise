#!/bin/python3
# -*- encoding: utf-8 -*-
import configparser
import os
import io

def read_ini(file):
    '''
    读取ini文件
    '''
    config_dict = {}
    if not os.path.exists(file):
        # return False
        raise InvalidResponse({'code': 1, 'message': "script crash, reason: no such %s"%(file)})
    config = configparser.ConfigParser(allow_no_value=True)
    # 重写覆盖optionxform避免ConfigParser的option变成小写
    config.optionxform = lambda option: option
    # 用IO读取避免UTF8编码不识别
    try:
        with io.open(file,mode="r",encoding="utf8") as f:
            config.read_file(f)
    except UnicodeDecodeError as err:
        try:
            with io.open(file,mode="r",encoding="gbk") as f:
                config.readfp(f)
        except Exception as err:
            config.read(file)

    return config

if __name__ == "__main__":
    config = read_ini("/code/CUTeMoL/exercise/note/PostgreSQL/conf/postgresql.service")
    print(config["Service"]["User"])