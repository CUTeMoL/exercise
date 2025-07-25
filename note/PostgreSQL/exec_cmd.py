from concurrent.futures import ThreadPoolExecutor
import subprocess
import concurrent
import platform
import locale
import sys

def exec_cmd(cmd, stdin=None):
    '''
    执行外部命令(等待获取结果)
    '''
    tty_coding = locale.getdefaultlocale()[1]
    if sys.version_info.major == 2:
        cmd = cmd.encode(tty_coding)
    cmd = cmd.split() if type(cmd) is str else cmd
    # print(cmd)
    p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input=stdin)
    if p.returncode != 0:
        return p.returncode, stderr.decode(tty_coding).replace("\r\n","\n")
    return p.returncode, stdout.decode(tty_coding).replace("\r\n","\n")


def exec_cmd_timeout(cmd, stdin=None, timeout=None):
    '''
    执行外部命令(超时终止)
    '''
    try:
        stdout = b""
        stderr = b""
        pool = ThreadPoolExecutor(2)
        tty_coding = locale.getdefaultlocale()[1]
        cmd = cmd.split() if type(cmd) is str else cmd
        p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        pool.submit(p.wait).result(int(timeout))
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
    print(exec_cmd_timeout("ping -c 15 127.0.0.1", stdin=None, timeout=3))
