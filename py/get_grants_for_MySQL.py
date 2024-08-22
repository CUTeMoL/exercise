#!/bin/python2
# -*- encoding: utf-8 -*-

import base64
import json
import optparse
import os
import re
import logging
import logging.handlers
import MySQLdb.cursors
import json
# import pymysql.cursors as MySQLdb.cursors

'''
使用方法:
python get_grants_for_Mysql.py --host="填实例IP" --port="填实例端口" --user="连数据库的的用户比如：root" --passwd="连数据库的密码"  --includeusers="以逗号分隔的需要导出的用户权限,比如:emoney,enmoney168,biggamesys,emoneyshop" --excludeusers="排除要寻找的用户权限"

可选项:
--socket="本地socket路径",存在则port不生效,给通过socket链接的数据库使用

注意事项:
如果存在includeusers,则excludeusers不会生效
如果要导出全部,则不使用--includeusers,--excludeusers=""
已经排除'mysql.sys','mysql.session','mysql.infoschema', '', ' ' 这些默认权限

'''

WORK_PATH = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(WORK_PATH, "get_grants_for_MySQL.log")
# 定义Filter
# filter_object = logging.Filter("get_gratns_for_MySQL")
# 定义formatter
formatter_object = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s")

# 定义handler
to_streamhandler = logging.StreamHandler(stream=None)
to_streamhandler.setLevel(logging.INFO)
to_streamhandler.setFormatter(formatter_object)

to_filehandler = logging.FileHandler(filename=log_path, mode='a', encoding=None, delay=False)
to_filehandler.setLevel(logging.DEBUG)
to_filehandler.setFormatter(formatter_object)
# to_filehandler.addFilter(filter_object)
# 定义日志logger
to_main_log = logging.getLogger("get_grants_for_MySQL")
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


def main(host,port,user,passwd,socket,excludeusers=None,includeusers=None):
    try:
        res = {}
        db = None
        for _k,_v in locals().items():
            if _k not in [ "socket", "excludeusers", "includeusers", "db"] and _v is None:
                raise ArgsError("%s error"%(_k))
            if _k == "port" and _v is None and socket is None:
                raise ArgsError("%s error"%(_k))

        
        to_main_log.debug("Args: host=%s,port=%s,user=%s,passwd=%s,socket=%s"%(host,port,user,passwd,socket))
        if excludeusers not in [ None, ""]:
            excludeusers = ",".join("'%s'"%(user) for user in excludeusers.split(","))
        else:
            excludeusers = "''"
        if includeusers not in [ None, ""]:
            includeusers = ",".join("'%s'"%(user) for user in includeusers.split(","))
        else:
            includeusers = None

        if socket is not None:
            db = MySQLdb.connect(host=host, user=user, passwd=passwd, unix_socket=socket, cursorclass=MySQLdb.cursors.DictCursor)
        else:
            db = MySQLdb.connect(host=host, user=user, passwd=passwd, port=int(port),  cursorclass=MySQLdb.cursors.DictCursor)

        cursor = db.cursor()
        if includeusers is not None:
            to_main_log.debug("select user,host,authentication_string from mysql.user where  user in (%s);"%(includeusers))
            msg = cursor.execute("select user,host,authentication_string from mysql.user where user in (%s);"%(includeusers))
        else:
            # 排除系统内置用户
            to_main_log.debug("select user,host,authentication_string from mysql.user where user not in ('mysql.sys','mysql.session','mysql.infoschema', '', ' ', %s) ;"%(excludeusers))
            msg = cursor.execute("select user,host,authentication_string from mysql.user where user not in ('mysql.sys','mysql.session','mysql.infoschema', '', ' ', %s) ;"%(excludeusers))


        for i in range(0,msg):
            result = (cursor.fetchone())
            account = "'%s'@'%s'"%(result["user"],result["host"])
            res[account] = {"passwd": result["authentication_string"], "grants": []}
        # 获取数据库版本
        msg = cursor.execute("select version() as version;")
        for i in range(0,msg):
            result = cursor.fetchone()
            version = result["version"].split("-")[0]


        
        for account in sorted([i for i in res.keys()]):
            print("-- %s -- "%(account))
            user_usage = ""
            if (int(version.split(".")[0]) >= 5 and int(version.split(".")[1]) >= 7 ) or int(version.split(".")[0]) == 8 :
                # 5.7以上系统使用show create user创建用户
                msg = cursor.execute("show create user %s ;"%(account))
                for i in range(0,msg):
                    result = cursor.fetchone()
                    for k in result.keys():
                        user_usage = user_usage + "%s;\n"%result[k]
            else:
                user_usage = user_usage + "\n"

            # 获取该账号的权限
            line = cursor.execute("show grants for %s;"%(account))
            for i in range(line):
                result = cursor.fetchone()
                for k in result.keys():
                    rep_line = "%s;"%result[k]
                    user_usage = user_usage + rep_line + "\n"
                    res[account]["grants"].append(result[k])
            print(user_usage)
        print("flush privileges;")


        to_main_log.debug("execute finish.")
        
    except Exception as err:
        to_main_log.error(err)
        raise err
    finally:
        if db is not None:
            db.close()
    

if __name__ == "__main__":

    Parser = optparse.OptionParser()
    Parser.add_option("--host", dest="host")
    Parser.add_option("--port", dest="port")
    Parser.add_option("--user", dest="user")
    Parser.add_option("--passwd", dest="passwd")
    Parser.add_option("--excludeusers", dest="excludeusers",default="")
    Parser.add_option("--includeusers", dest="includeusers",default="")
    Parser.add_option("--socket", dest="socket", default=None)
    (opt, args) = Parser.parse_args()
    main(
        getattr(opt,"host"),
        getattr(opt,"port"),
        getattr(opt,"user"),
        getattr(opt,"passwd"),
        getattr(opt,"socket"),
        getattr(opt,"excludeusers"),
        getattr(opt,"includeusers"),
    )
    