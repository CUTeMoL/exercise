#!/bin/python2
# -*- encoding: utf-8 -*-

import psutil
import sys
import os
import optparse
import signal
import time
import logging
import logging.handlers
import traceback
import re
import json
import itertools
import locale
import subprocess
import platform

class CmdParse(object):
    def __init__(self):
        Parser = optparse.OptionParser(description="list open files.")
        Parser.add_option("--process","-p", dest="process", default=None, help=u"指定程序pid来筛选")
        Parser.add_option("--kill","-k", dest="kill",action="store_true", default=False, help=u"杀进程")
        Parser.add_option("--yes","-y", dest="yes",action="store_true", default=False, help=u"杀进程无需确认")
        Parser.add_option("--mode","-m", dest="mode", default="simple", help=u"json/list模式")
        Parser.add_option("--verbose","-v", dest="verbose",action="store_true", default=False, help=u"配合list模式下详细输出该pid的所有的占用文件")
        Parser.add_option("--log", dest="log", default=os.path.join(os.path.dirname(sys.argv[0]),"logs", "lsof_%s.log"%(time.strftime('%Y%m%d', time.localtime(time.time())))), help=u"日志输出路径")
        self.options, self.args = Parser.parse_args()


def exec_cmd_binary(cmd,stdin=None):
    '''
    执行外部命令
    '''
    # windows 返回消息什么编码的都有，直接2进制返回
    # centos6 之前可能获取环境语言有异常,所以获取异常时
    tty_coding = locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1] not in [None, "", False] else "utf-8"
    if sys.version_info.major == 2:
        cmd = cmd.encode(tty_coding)
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input=stdin)
    return p.returncode,  bytes(stdout+b";"+stderr)


def lsof(pid=None,qfs=[]):
    '''
    文件占用
    '''
    pid = 0 if pid in [None,0,""] else int(pid)
    # processs = [p.as_dict() for p in  psutil.process_iter()]
    # 筛下数据,只保留一部分
    res = {}
    for p in  psutil.process_iter():
        try:
            info = p.as_dict(["pid","open_files","cmdline","username"])
            p_ofs = info["open_files"] if len(info["open_files"]) > 0 else []
            P_cmd = " ".join(info.get("cmdline", [""]) if info.get("cmdline", [""]) is not None else [""])
            p_user = info["username"]
            if pid == 0 or (pid != 0 and pid == info["pid"] ):
                if len(qfs) > 0 and len(p_ofs) > 0:
                    for qf in qfs:
                        #
                        if qf.lower() in [of.path.lower() for of in p_ofs]:
                            # mode 只有linux有统一下输出
                            res[str(info["pid"])] = {"open_files": [{"path": str(getattr(of,"path", "")), "fd":getattr(of,"fd", ""), "mode": getattr(of,"mode", "Nosupport")} for of in p_ofs],"cmd": P_cmd, "user": p_user}
                elif len(qfs) == 0:
                    res[str(info["pid"])] = {"open_files": [{"path": str(getattr(of,"path", "")), "fd":getattr(of,"fd", ""), "mode": getattr(of,"mode", "Nosupport")} for of in p_ofs],"cmd": P_cmd, "user": p_user}
        except TypeError as err:
            # 因为迭的太慢有些进行已经结束了,会object of type 'NoneType' has no len()
            pass
        # 无权限跳过
        # except WindowsError as err:
        #     pass

    return res


def main(p,k,y,m,v,log_path,args):
    if not os.path.exists(os.path.join(os.path.dirname(log_path),"logs")):
        os.makedirs(os.path.join(os.path.dirname(log_path),"logs"))
    # log_path = os.path.join(os.path.dirname(log),"logs", "lsof_%s.log"%(time.strftime('%Y%m%d', time.localtime(time.time()))))
    # 定义Filter
    # Filter = logging.Filter("lsof")
    tty_coding = locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1] not in [None, "", False] else "utf-8"
    # 定义formatter
    formatter_file = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s")
    formatter_stream = logging.Formatter("%(message)s")
    # 定义handler
    streamhandler = logging.StreamHandler(stream=sys.stdout)
    streamhandler.setLevel(logging.INFO)
    streamhandler.setFormatter(formatter_stream)
    filehandler = logging.FileHandler(filename=log_path, mode='a+', encoding=tty_coding,delay=False)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(formatter_file)


    # 定义日志logger
    logger = logging.getLogger("lsof")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(streamhandler)
    logger.addHandler(filehandler)
    # logger_object.addFilter(filter_object)
    logger.info("Begin...")
    result = lsof(p,args)
    # list输出
    returncode = 0
    if m == "list":
        logger.info(u"pid\tfd\tmode\topenfile\tuser\tcmd")
        if len(result) >=0:
            for pid in result.keys():
                for row in itertools.product([str(pid)],[result[pid]["cmd"]],[result[pid]["user"]],result[pid]["open_files"]):
                    if v is True:
                        logger.info(u"%s\t%s\t%s\t%s\t%s\t%s"%(row[0],row[3]["fd"],row[3]["mode"],row[3]["path"],row[2],row[1]))
                    elif v is False and ((len(args) > 0 and row[3]["path"].lower() in [ item.lower() for item in args ]) or len(args)==0):
                        logger.info(u"%s\t%s\t%s\t%s\t%s\t%s"%(row[0],row[3]["fd"],row[3]["mode"],row[3]["path"],row[2],row[1]))

    # json输出
    elif m == "json":
        logger.info(json.dumps(result))
    # 简洁输出
    elif len(result) > 0:
        logger.info(u" ".join(result.keys()))

    if k is True and len(args) > 0 :
        if y is not True:
            y = input("是否确认kill进程%s,y确认,其他跳过:\n"%(" ".join(result.keys())))
            if y == "y":
                y = True
        if y is True:
            if platform.system() == "Windows":
                cmd = "taskkill /f %s"%(" ".join(["/pid %s"%(p) for p in result.keys()]))
            else:
                cmd = "kill -9 /f %s"%(" ".join(result.keys()))
            logger.info(u"执行关闭%s"%(" ".join(result.keys())))
            code, msg = exec_cmd_binary(cmd)
            logger.info(u"已执行关闭%s"%(" ".join(result.keys())))
            logger.info("%s"%msg.decode(tty_coding) )
            time.sleep(30)
            for pid in result.keys():
                if psutil.pid_exists(int(pid)) and time.time() - psutil.Process(int(pid)).create_time() > 30:
                    returncode = 1
                    logger.error(u"强制关闭%s失败"%(pid))
        else:
            logger.info(u"不执行强杀进程")
    logger.info("End.")
    sys.exit(returncode)
    
if __name__ == "__main__":
    WORK_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    cp = CmdParse()
    main(
        getattr(cp.options,"process"),
        getattr(cp.options,"kill"),
        getattr(cp.options,"yes"),
        getattr(cp.options,"mode"),
        getattr(cp.options,"verbose"),
        getattr(cp.options,"log"),
        cp.args
    )