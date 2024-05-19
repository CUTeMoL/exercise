#!/bin/python2
# -*- encoding: utf-8 -*-

import base64
import json
import optparse
import os
import sys
import logging
import logging.handlers
import pymysql
import json


WORK_PATH = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(WORK_PATH, "get_gratns_for_MySQL.log")
# 定义Filter
# filter_object = logging.Filter("get_gratns_for_MySQL")
# 定义formatter
formatter_object = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s")

# 定义handler
to_streamhandler = logging.StreamHandler(stream=None)
to_streamhandler.setLevel(logging.INFO)
to_streamhandler.setFormatter(formatter_object)

to_filehandler = logging.FileHandler(filename=log_path, mode='w', encoding=None, delay=False)
to_filehandler.setLevel(logging.DEBUG)
to_filehandler.setFormatter(formatter_object)
# to_filehandler.addFilter(filter_object)
# 定义日志logger
to_main_log = logging.getLogger("get_gratns_for_MySQL")
to_main_log.setLevel(logging.DEBUG) # 级别最好为DEBUG,因为这个设置不是被后面handlers的覆盖,而是先过滤后才转给handlers
to_main_log.addHandler(to_streamhandler)
to_main_log.addHandler(to_filehandler)
# to_main_log.addFilter(filter_object)


class ArgsError(Exception):
    def __init__(self, message):
        self.message = message
 
    def __str__(self):
        return "ArgsError: {}".format(self.message)
 

class MysqlConnectError(Exception):
    def __init__(self, message):
        self.message = message
 
    def __str__(self):
        return "MysqlConnectError: {}".format(self.message)


def main(host,port,user,passwd,socket):
    try:
        res = {}
        for _k,_v in locals().items():
            if _k != "socket" and _v is None:
                raise ArgsError("%s error"%(_k))
            if _k == "port" and _v is None and socket is None:
                raise ArgsError("%s error"%(_k))
        to_main_log.debug("Args: host=%s,port=%s,user=%s,passwd=%s,socket=%s"%(host,port,user,passwd,socket))

        db = pymysql.connect(host=host, user=user, password=passwd, port=int(port), unix_socket=socket, cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        msg = cursor.execute("select user,host,authentication_string from mysql.user where user not in ('root','mysql.sys','mysql.session','mysql.infoschema');")
        for i in range(0,msg):
            result = (cursor.fetchone())
            account = "'%s'@'%s'"%(result["user"],result["host"])
            res[account] = {"passwd": result["authentication_string"], "grants": []}

        
        for account in res.keys():
            line = cursor.execute("show create user %s;"%(account))
            for i in range(line):
                result = cursor.fetchone()
                for k in result.keys():
                    print("%s;"%(result[k]))
            
            line = cursor.execute("show grants for %s;"%(account))
            for i in range(line):
                result = cursor.fetchone()
                for k in result.keys():
                    print("%s;"%(result[k]))
                    res[account]["grants"].append(result[k])
        to_main_log.debug(json.dumps(res,indent=4,ensure_ascii=False))
        to_main_log.debug("execute finish.")
        
    except Exception as err:
        to_main_log.error(err)
        raise err
    
    

if __name__ == "__main__":
    # logger = game_logger.GameLogger(os.path.join(WORK_PATH,"test.log"), "info", 1, 60, need_stdout=False)
    Parser = optparse.OptionParser()
    Parser.add_option("--host", dest="host")
    Parser.add_option("--port", dest="port")
    Parser.add_option("--user", dest="user")
    Parser.add_option("--passwd", dest="passwd")
    Parser.add_option("--socket", dest="socket", default=None)
    (opt, args) = Parser.parse_args()
    main(
        getattr(opt,"host"),
        getattr(opt,"port"),
        getattr(opt,"user"),
        getattr(opt,"passwd"),
        getattr(opt,"socket"),
    )
    