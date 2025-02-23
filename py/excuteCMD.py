#!/usr/bin/env python3
#-*- coding: utf-8 -*- 

import subprocess
import locale
import sys
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures._base
import platform



def exec_cmd(cmd, stdin=None):
    '''
    执行外部命令
        适应window、linux
        适应python2.7、python3.6以上版本
    Args:
        cmd: 要执行的命令
        stdin: 如果命令需要交互时输入的内容
    Returns:
        p.returncode: 命令运行结果的标志, 0 成功, 其他失败
        stdout.decode(tty_coding): 命令返回结果,输出到管道1的结果
        stderr.decode(tty_coding): 命令返回结果,输出到管道2的结果
    example:
        exec_cmd("echo 你好")
    Raises:

    '''
    # 获取当前终端的环境编码
    tty_coding = locale.getdefaultlocale()[1]

    # python2需要转编码为当前环境的编码
    if sys.version_info.major == 2:
        cmd = cmd.encode(tty_coding)

    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input=stdin)
    if p.returncode != 0:
        return p.returncode, stderr.decode(tty_coding)
    return p.returncode, stdout.decode(tty_coding)

def exec_cmd_timeout(cmd, stdin=None, timeout=None):
    '''
    执行外部命令带有超时终止
        适应window、linux
        适应python2.7、python3.6以上版本
    Args:
        cmd: 要执行的命令
        stdin: 如果命令需要交互时输入的内容
    Returns:
        p.returncode: 命令运行结果的标志, 0 成功, 其他失败
        stdout.decode(tty_coding): 命令返回结果,输出到管道1的结果
        stderr.decode(tty_coding): 命令返回结果,输出到管道2的结果
    example:
        exec_cmd("echo 你好")
    Raises:

    '''
    try:
        pool = ThreadPoolExecutor(1)
        tty_coding = locale.getdefaultlocale()[1]
        if sys.version_info.major == 2:
            cmd = cmd.encode(tty_coding)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if timeout is not None:
            exec_cmd_future = pool.submit(p.wait).result(timeout)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        msg = stdout + b"\n" + stderr
        return p.returncode, msg.decode(tty_coding).replace("\r\n","\n")
    except concurrent.futures._base.TimeoutError as e:
        if platform.system().lower() == "windows":
            kill_cmd = "taskkill /T /F /pid %s"%(p.pid)
        else:
            kill_cmd = "kill -9 %s"%(p.pid)
        exec_cmd(kill_cmd)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        msg = stdout + b"\n" + stderr
        return p.returncode, msg.decode(tty_coding).replace("\r\n","\n")
