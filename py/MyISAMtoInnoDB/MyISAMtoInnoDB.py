import os
import time
import platform
import logging
import logging.handlers
import functools
import subprocess
import ipaddress

'''
改进计划
1.logging配置文件化
2.数据库对象使用配置文件或输入的方式
3.日志写入mongodb
'''

__author__ = "lxw"
__last_modify_date__ = "2023.01.25"
__modify__ = "重写日志输出格式,函数改为类"



log_path = r"%s/%s_%s.log" %(os.path.dirname(__file__), platform.node(),time.strftime('%Y-%m-%d', time.localtime()))

formatter_object = logging.Formatter("{'datetime': '%(asctime)s', 'level': '%(levelname)s', 'message': %(message)s}")

streamhandler_object = logging.StreamHandler(stream=None)
streamhandler_object.setLevel(logging.INFO)
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
            exec_result = {
                "task": text,
                "func_result": func_result,
                "runnning_time": "%.3f" %(running_time)
            }
            return exec_result
        return exectimes
    return timecalc


class database_object(object):
    platform_system = platform.system()
    def __init__(self, hostname, port, user, passwd, dbname):
        self.__host = hostname
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__dbname = dbname


    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, ipaddr):
        if isinstance(ipaddr, (ipaddress.ip_address, str)):
            self.__host = ipaddr
        else:
            raise ValueError('Must be an ipaddress.')


    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, dbport):
        if isinstance(dbport, (int, )) and dbport > 0 and dbport <= 65525 :
            self.__port = dbport
        else:
            raise ValueError('Must be a number(1-65535).')


    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, dbuser):
        if isinstance(dbuser, (str, )):
            self.__user = dbuser
        else:
            raise ValueError('Must be a string.')


    @property
    def passwd(self):
        return self.__passwd

    @passwd.setter
    def passwd(self, dbpasswd):
        if isinstance(dbpasswd, (str, )):
            self.__passwd = dbpasswd
        else:
            raise ValueError('Must be a string.')


    @property
    def dbname(self):
        return self.__dbname

    @dbname.setter
    def dbname(self, dbname):
        if isinstance(dbname, (str, )):
            self.__dbname = dbname
        else:
            raise ValueError('Must be a string.')


    def query_dbinfo(self):
        dbinfo = {
            "dbhost": self.__host,
            "dbport": self.__port,
            "dbuser": self.__user,
            "dbpasswd": self.__passwd,
            "dbname":  self.__dbname
        }
        return dbinfo


    def get_MyISAM_tables(self, mysql):
        get_tables_command = '''{} -h{} -P{} -u{} -p{} {} -s -N -e "SELECT TABLE_NAME from information_schema.TABLES WHERE TABLE_SCHEMA='{}' and ENGINE='MyISAM';"'''.format(
            mysql,
            self.host,
            self.port,
            self.user,
            self.passwd,
            self.dbname,
            self.dbname
        )
        if self.platform_system == "Windows":
            get_tables = subprocess.run(get_tables_command, shell=True, capture_output=True, encoding="ansi")
        else:
            get_tables = subprocess.run(get_tables_command, shell=True, capture_output=True, encoding="utf-8")
        if get_tables.returncode == 0:
            self.MyISAM_tables = get_tables.stdout.split()
        else:
            self.MyISAM_tables = None
            get_MyISAM_tables_result = {
            "commandline": get_tables.args,
            "returncode": get_tables.returncode,
            "stdout": get_tables.stdout,
            "stderr": get_tables.stderr
        }
            logger_object.error(get_MyISAM_tables_result)
        return self.MyISAM_tables


    @run_log(('CHANGE ENGINE=InnoDB'))
    def MyISAM_to_InnoDB(self, mysql, MyISAM_table):
        alter_table_command = '{} -h{} -P{} -u{} -p{} -e "ALTER TABLE {}.{} ENGINE=InnoDB;"'.format(
            mysql,
            self.host,
            self.port,
            self.user,
            self.passwd,
            self.dbname,
            MyISAM_table
        )
        if self.platform_system == "Windows":
            alter_table_result = subprocess.run(alter_table_command, shell=True, capture_output=True, encoding="ansi")
        else:
            alter_table_result = subprocess.run(alter_table_command, shell=True, capture_output=True, encoding="utf-8")
        MyISAM_to_InnoDB_result = {
            "commandline": alter_table_result.args,
            "returncode": alter_table_result.returncode,
            "stdout": alter_table_result.stdout,
            "stderr": alter_table_result.stderr
        }
        return MyISAM_to_InnoDB_result




if __name__ == "__main__":
    workpath=os.path.dirname(__file__)
    os.chdir(workpath)
    db_object = database_object("localhost", 3311, "root", "123456", "cq1")
    if platform.system() == "Windows":
        mysql_path = "{}\\bin\\mysql.exe".format(workpath)
    else:
        mysql_path = r"{}/bin/mysql".format(workpath)

    if os.path.isfile(mysql_path):
        logger_object.debug("{'PROCESS': 'RUNNING'}")
        tables = db_object.get_MyISAM_tables(mysql_path)
        if tables:
            for table in tables:
                result =  db_object.MyISAM_to_InnoDB(mysql_path, table)
                if result["func_result"]["returncode"] != 0 :
                    logger_object.error(result)
                else:
                    logger_object.debug(result)
        logger_object.debug("{'PROCESS': 'STOP'}")
    else:
        logger_object.debug("mysql not found")
