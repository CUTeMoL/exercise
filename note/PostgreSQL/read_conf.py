#!/bin/python3
# -*- encoding: utf-8 -*-
import configparser
import os
import io

def read_ini(file):
    '''
    读取ini文件,输出字典格式的信息
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
    for s in config.sections():
        config_dict[s] = {}
        for o in config.options(s):
            config_dict[s][o] = config.get(s,o)
    return config_dict

if __name__ == "__main__":
    print(read_ini("/code/CUTeMoL/exercise/note/PostgreSQL/conf/postgresql.service"))