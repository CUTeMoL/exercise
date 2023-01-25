#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import os
import time
import platform
import logging
import logging.handlers
import functools
import subprocess

'''
改进计划
1.重写计时器
2.logging配置文件化
3.多进程|多线程执行
'''

db_object = {
    "dbhost": "localhost",
    "dbport": 3312,
    "dbuser": "root",
    "dbpasswd": "123456",
    "dbname": "cq1"
}

__author__ = "lxw"
__last_modify_date__ = "2023.01.23"
__modify__ = "日志显示"


workpath=os.path.dirname(__file__)
os.chdir(workpath)
if platform.system() == "Windows":
    mysql_path = r"{}/bin/mysql.exe".format(workpath)
else:
    mysql_path = r"{}/bin/mysql".format(workpath)

log_path = r"%s/%s_%s.log" %(workpath, platform.node(),time.strftime('%Y-%m-%d', time.localtime()))

formatter_object = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

streamhandler_object = logging.StreamHandler(stream=None)
streamhandler_object.setLevel(logging.DEBUG)
streamhandler_object.setFormatter(formatter_object)

filehandler_object = logging.FileHandler(filename=log_path, mode='a', encoding="utf8", delay=False)
filehandler_object.setLevel(logging.DEBUG)
filehandler_object.setFormatter(formatter_object)

logger_object = logging.getLogger("_%s" %(time.strftime('%Y-%m-%d', time.localtime())))
logger_object.setLevel(logging.DEBUG)
logger_object.addHandler(streamhandler_object)
logger_object.addHandler(filehandler_object)


def run_log(text):
    def timecalc(func):
        @functools.wraps(func)
        def exectimes(*args, **kwargs):
            starttime = time.time()
            func_result = func(*args, **kwargs)
            endtime = time.time()
            running_time = endtime - starttime
            return text, func_result, running_time
        return exectimes
    return timecalc 


def get_MyISAM_tables(dbinfo, mysql, platform_system):
    get_tables_command = '''\
{} -h{} -P{} -u{} -p{} {} -s -N -e "SELECT TABLE_NAME from information_schema.TABLES WHERE TABLE_SCHEMA='{}' and ENGINE='MyISAM';"\
'''.format(
        mysql,
        dbinfo["dbhost"],
        dbinfo["dbport"],
        dbinfo["dbuser"],
        dbinfo["dbpasswd"],
        dbinfo["dbname"],
        dbinfo["dbname"]
    )
    if platform_system == "Windows":
        get_tables = subprocess.run(get_tables_command, shell=True, capture_output=True, encoding="ansi")
    else:
        get_tables = subprocess.run(get_tables_command, shell=True, capture_output=True, encoding="utf-8")
    if get_tables.returncode == 0:
        MyISAM_tables = get_tables.stdout.split()
    else:
        logger_object.debug(get_tables.stderr)
        MyISAM_tables = None
    return MyISAM_tables


@run_log(('alter table %s.' %(db_object["dbname"])))
def MyISAM_to_InnoDB(dbinfo, mysql, platform_system, MyISAM_table):
    alter_table_command = '''\
{} -h{} -P{} -u{} -p{} -e "ALTER TABLE {}.{} ENGINE=InnoDB;"\
        '''.format(
                    mysql,
                    dbinfo["dbhost"],
                    dbinfo["dbport"],
                    dbinfo["dbuser"],
                    dbinfo["dbpasswd"],
                    dbinfo["dbname"],
                    MyISAM_table
        )
    if platform_system == "Windows":
        alter_table_result = subprocess.run(alter_table_command, shell=True, capture_output=True, encoding="ansi")
    else:
        alter_table_result = subprocess.run(alter_table_command, shell=True, capture_output=True, encoding="utf-8")
    if alter_table_result.returncode != 0:
        logger_object.error(alter_table_result.stderr)
    return alter_table_result.returncode


if os.path.isfile(mysql_path):
    logger_object.debug("PROCESS RUNNING")
    tables = get_MyISAM_tables(db_object, mysql_path, platform.system())
    for table in tables:
        text, result, running_time = MyISAM_to_InnoDB(db_object, mysql_path, platform.system(), table)
        logger_object.debug("%s%s ENGINE=InnoDB; return: %s Runtime: %.2f s" %(text, table, result, running_time))
    logger_object.debug("PROCESS STOP")
else:
    logger_object.debug("mysql not found")
