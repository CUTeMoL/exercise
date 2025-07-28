#!/bin/python3
# -*- encoding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import subprocess
import concurrent
import platform
import locale
import sys
import shlex
from typing import Union, List, AnyStr
import shutil


class Command(subprocess.Popen):
    '''
    命令格式化后再提交
    '''
    tty_coding = locale.getdefaultlocale()[1]
    def __init__(self, cmd: Union[str, List[AnyStr]], **kwargs):
        # 先把strings格式化成list
        cmd = self.check_args(cmd)
        super().__init__(cmd, **kwargs)
    
    @staticmethod
    def check_args(cmd):
        # 先把strings格式化成list
        if isinstance(cmd, list):
            cmd = cmd
        elif sys.version_info.major == 2 and isinstance(cmd, str):
            cmd = shlex.split(cmd.encode(tty_coding))
        elif isinstance(cmd, str):
            cmd = shlex.split(cmd)
        else:
            raise ValueError("Command please use [list] or 'strings'.")
        if shutil.which(cmd[0]) is None:
            raise ValueError("%s not found."%(cmd[0]))
        else:
            cmd[0] = shutil.which(cmd[0])
        return cmd



def exec_cmd(cmd: Union[str, List[AnyStr]], stdin=None):
    '''
    快速执行外部命令(等待获取结果)
    '''
    tty_coding = locale.getdefaultlocale()[1]
    if sys.version_info.major == 2:
        cmd = cmd.encode(tty_coding)
    cmd = shlex.split(cmd) if type(cmd) is str else cmd
    # print(cmd)
    p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input=stdin)
    if p.returncode != 0:
        return p.returncode, stderr.decode(tty_coding).replace("\r\n","\n")
    return p.returncode, stdout.decode(tty_coding).replace("\r\n","\n")


def exec_cmd_timeout(cmd: Union[str|List[AnyStr]], stdin=None, timeout=None):
    '''
    快速执行外部命令(超时终止)
    '''
    try:
        stdout = b""
        stderr = b""
        pool = ThreadPoolExecutor(2)
        tty_coding = locale.getdefaultlocale()[1]
        cmd = shlex.split(cmd) if type(cmd) is str else cmd
        # stderr 重定向到 stdout
        p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        pool.submit(p.wait).result(timeout)
        stdout, stderr = p.communicate(input=stdin)
        if p.returncode != 0:
            return p.returncode, stderr.decode(tty_coding).replace("\r\n","\n")
        return p.returncode, stdout.decode(tty_coding).replace("\r\n","\n")

    except concurrent.futures._base.TimeoutError as e:
        stdouts = iter(p.stdout.readline, b'')
        # stderr = p.stderr.readline()
        if platform.system().lower() == "windows":
            kill_cmd = "taskkill /T /F /pid %s"%(p.pid)
        else:
            kill_cmd = "kill -9 %s"%(p.pid)
        exec_cmd(kill_cmd)
        for line in stdouts:
            stdout = stdout + line
        # if p.returncode != 0:
        #     return p.returncode, stderr.decode(tty_coding).replace("\r\n","\n")
        return p.returncode, stdout.decode(tty_coding).replace("\r\n","\n")

if __name__ == "__main__":
    # 一些测试数据
    print(exec_cmd_timeout("ping -c 15 127.0.0.1", stdin=None, timeout=1))
    p = Command("ping -c 15 127.0.0.1",shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout.readline())
    import time
    time.sleep(5)
    print(p.stdout.readline())
    # print(p.communicate())
