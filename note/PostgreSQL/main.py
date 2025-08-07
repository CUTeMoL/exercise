#!/bin/python3
# -*- encoding: utf-8 -*-
import subprocess
import sys
import os
import re
import logging
import logging.config
import json
import traceback
import pwd
from read_conf import read_ini
from exec_command import exec_cmd, Command
from dependencies import Soft
from exec_error import *
from file_processing import File
from string_convert import string_to_sha512

## 全局变量设置 ##

# 脚本工作路径
WORK_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(WORK_PATH)

# 安装设置读取
INSTALL_CONFIG_FILE = os.path.join(WORK_PATH,"conf/install.json")
with open(INSTALL_CONFIG_FILE, "r") as INSTALL_CONFIG_FILE_HANDLER:
    INSTALL_CONFIG = json.loads(INSTALL_CONFIG_FILE_HANDLER.read())

# 编译参数
PARAMETER_CONFIG_FILE = os.path.join(WORK_PATH,"conf/configure_parameter.conf")
with open(PARAMETER_CONFIG_FILE, "r") as PARAMETER_CONFIG_FILE_HANDLER:
    PARAMETER_CONFIG = PARAMETER_CONFIG_FILE_HANDLER.read().strip().replace("\r\n","\n").split("\n")

PREFIX_REGULAR = re.compile("['|\"]?--prefix=(?P<prefix>.*)['|\"]?")
PREFIX = [PREFIX_REGULAR.search(i).group("prefix")  for i in PARAMETER_CONFIG if PREFIX_REGULAR.match(i) ][-1]

# 下载包临时保存目录设置,主要为了代码和下载包分开来
TMP_PATH = os.path.join(WORK_PATH,"tmp") if not INSTALL_CONFIG.get("tmp_path", None) else INSTALL_CONFIG["tmp_path"]
if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)

# 日志
logging.config.fileConfig('conf/logging.conf')
LOGGER = logging.getLogger('POSTGRESQL_INSTALL')

# 编译工作路径
COMPILE_PATH = os.path.join(TMP_PATH, "postgresql-%s"%(INSTALL_CONFIG["version"]))
# 源码包信息生成
PACKAGE_NAME = "postgresql-%s%s"%(INSTALL_CONFIG["version"],INSTALL_CONFIG["file_name_extension"])
PACKAGE_PATH = os.path.join(TMP_PATH, PACKAGE_NAME)


## 函数 ##
def read_dependencies():
    '''获取依赖文件集合'''
    LOGGER.info("读取依赖列表...")
    requirements_file = os.path.join(os.path.dirname(sys.argv[0]),"dependencies.txt")
    if os.path.exists(requirements_file):
        with open(requirements_file, "r") as f:
            requirements = [line for line in f.read().replace("\r\n","\n").split("\n") if not line.startswith("#") and line != ""]
        if len(requirements) == 0:
            LOGGER.error("依赖列表为空,请检查.")
            raise DependenciesListError(2)
        return requirements
    else:
        LOGGER.error("没获取到依赖列表.")
        raise DependenciesListError(1)


def check_dependencies(requirements):
    '''
    检查依赖是否存在
    '''
    match_line = re.compile("(?P<soft_name>.*)\s*(?P<operator>>=|<=|==)\s*(?P<Required>.*)")
    for requirement in requirements:
        if match_line.match(requirement):
            match_soft = match_line.match(requirement)
            requirement_soft = Soft(match_soft.group("soft_name"))
            LOGGER.info("当前检查 %s: %s存在"%(requirement_soft.name, "" if requirement_soft.exist else "不"))
            for i in range(1,3):
                if requirement_soft.exist is False or (not requirement_soft.compare_versions(match_soft.group("Required"),match_soft.group("operator")) and i < 2):
                    LOGGER.warning("依赖软件%s版本检查异常,执行安装依赖软件..."%(requirement_soft.name))
                    requirement_soft.install()
                elif requirement_soft.exist is False and i == 2 :
                    LOGGER.error("依赖软件版本检查异常,执行安装依赖软件失败,退出.")
                    raise DependenciesMismatched(requirement_soft.name,requirement_soft.Version)
                elif  not requirement_soft.compare_versions(match_soft.group("Required"),match_soft.group("operator")) and i == 2 :
                    LOGGER.error("依赖软件版本检查失败,需求版本:%s%s,实际版本:%s,退出."%(match_soft.group("operator"),match_soft.group("Required"),requirement_soft.Version))
                    raise DependenciesMismatched(requirement_soft.name,requirement_soft.Version)

                elif requirement_soft.exist is True and requirement_soft.compare_versions(match_soft.group("Required"),match_soft.group("operator")):
                    LOGGER.info("[%s]%s %s %s"%(requirement_soft.name,requirement_soft.Version,match_soft.group("operator"),match_soft.group("Required")))
                    break
        else:
            LOGGER.error("没获取到依赖软件,%s"%(requirement))
            raise DependenciesListError(2)
    LOGGER.info("依赖检查完成.")
    return True


def download_package(base_url,version,file_name_extension):
    '''
    下载源码包
    base_url: 下载的基本链接地址(不带版本)
    version: 下载的版本号
    FilenameExtension: 文件后缀
    destination: 保存路径
    '''
    try:
        # package_name = "postgresql-%s%s"%(version,file_name_extension)
        # package_path = os.path.join(TMP_PATH,package_name)
        package_md5file_name = "postgresql-%s%s.md5"%(version,file_name_extension)
        package_md5file_path = os.path.join(TMP_PATH,package_md5file_name)
        download_package_url = "%sv%s/%s"%(base_url,version,PACKAGE_NAME)
        download_md5_url = "%sv%s/%s"%(base_url,version,package_md5file_name)
        package_md5file = File(package_md5file_path)
        package = File(PACKAGE_PATH)
        LOGGER.info("开始下载源码包MD5文件%s"%(package_md5file_path))
        package_md5file.download(download_md5_url)
        with open(package_md5file_path,"r") as package_md5_f:
            package_md5_require = package_md5_f.read().split()[0].strip().lower()
        LOGGER.info("开始下载源码包文件%s"%(PACKAGE_PATH))
        package.download(download_package_url)
        LOGGER.info("下载源码包文件%s完成"%(PACKAGE_PATH))
    except Exception as err:
        error_msg = traceback.format_exc()
        for line in error_msg.replace("\r\n","\n").split("\n"):
            LOGGER.error(line)
        raise DownloadError(10001,str(err),PACKAGE_PATH)
    LOGGER.info("源码包%s开始验证MD5"%(PACKAGE_PATH))
    if package.md5sum() == package_md5_require:
        LOGGER.info("源码包%s验证MD5:[%s]通过"%(PACKAGE_PATH,package_md5_require))
        return True
    else:
        raise DownloadError(10002,"md5sum neq %s"%(package_md5_require))
        

def extract_source_package(extract_path,file_name_extension):
    '''
    解压源码包
    '''
    package = File(PACKAGE_PATH)
    LOGGER.info("开始解压源码包")
    code, msg = package.extract(extract_path,file_name_extension)
    if code != 0:
        LOGGER.error("解压失败,详见以下错误信息:")
        for line in msg.strip().split("\n"):
            LOGGER.error(line)
        raise ExtractError(10003,msg,PACKAGE_PATH)
    LOGGER.info("解压源码包完成")
    return True


def make_install():
    '''
    编译安装
    '''

    PARAMETER_CONFIG.insert(0, os.path.join(COMPILE_PATH,"configure"))
    for cmd in [PARAMETER_CONFIG,"make",["make", "all"],["make", "install"],["su",INSTALL_CONFIG["superuser"],"-c","%s/bin/initdb -D %s"%(PREFIX,INSTALL_CONFIG["datadir"])]]:
        install_command = Command(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=COMPILE_PATH)
        LOGGER.info(" ".join(install_command.args))
        for line in iter(install_command.stdout.readline, b""):
            LOGGER.info(line.decode("utf8").replace("\n",""))
        install_command.wait()
        if install_command.returncode != 0:
            err_msg = install_command.stderr.read()
            raise InstallError(10004," ".join(install_command.args),err_msg)

    return True


def systemd_contrl():
    '''
    建立systemd启动配置
    '''
    service_file = os.path.join("/etc/systemd/system/","%s.service"%(INSTALL_CONFIG["systemd_name"]))
    config = read_ini("conf/postgresql.service")
    config["User"] = INSTALL_CONFIG["superuser"]
    config["ExecStart"] = "%s/bin/postgres -D %s "%(PREFIX,INSTALL_CONFIG["datadir"])
    
    with open(service_file, "w") as f:
        config.write(f)
    return True


def create_superuser():
    '''
    创建一个系统用户,用来运行postgresql
    '''
    try:
        superuser = pwd.getpwnam(INSTALL_CONFIG["superuser"])
        if superuser.pw_shell not in  ["/usr/sbin/nologin","/sbin/nologin"]:
            LOGGER.warning("%s是可登录用户,最好请另外选择一个用户或修改用户为不可登录(usermod -r -s /sbin/nologin %s)."%(INSTALL_CONFIG["superuser"],INSTALL_CONFIG["superuser"]))

    except KeyError as err:
        cmd = ["useradd","-r", "-s", "/bin/bash", INSTALL_CONFIG["superuser"], "-U", "-d", INSTALL_CONFIG["datadir"], "-p", string_to_sha512(INSTALL_CONFIG["superuserpasswd"])]
        create_user_command = Command(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=COMPILE_PATH)
        LOGGER.info(" ".join(create_user_command.args))
        for line in iter(create_user_command.stdout.readline, b""):
            LOGGER.info(line.decode("utf8").replace("\n",""))
        create_user_command.wait()
        if create_user_command.returncode != 0:
            err_msg = create_user_command.stderr.read()
            LOGGER.error("code:%s,msg:%s"%(create_user_command.returncode,err_msg))
            raise CreateUserError(10005," ".join(create_user_command.args),err_msg)


def chown_path(p,u,g=None):
    chown_cmd = "chown -R %s %s"%(u,":%s"%(g) if g else "",p)
    code,msg = exec_cmd(chown_cmd)
    if code != 0:
        raise ChownPathError(10006," ".join(create_user_command.args),msg)
    return True

def env_ensure():
    '''
    检查系统环境因素(用户,数据目录是否已存在)
    '''
    # 用户
    create_superuser()
    for check_path in [INSTALL_CONFIG["datadir"],PREFIX]
        if  os.path.exists(check_path) and len(check_path) >= 0:
            raise NotEmptyError(10007,check_path)

        if not  os.path.exists(check_path) :
            os.makedirs(check_path)
    # 启动项配置
    if "--with-systemd" in PARAMETER_CONFIG:
        systemd_contrl()
    # 路径授权
    chown_path(INSTALL_CONFIG["datadir"],INSTALL_CONFIG["superuser"])

    return True

def main():
    try:
        # 检查依赖
        check_dependencies(read_dependencies())
        # envcheck
        envcheck()
        # 下载
        download_package(INSTALL_CONFIG["base_url"],INSTALL_CONFIG["version"],INSTALL_CONFIG["file_name_extension"])
        # 解压
        extract_source_package(TMP_PATH,INSTALL_CONFIG["file_name_extension"])
        # 编译安装
        make_install()


    except Exception as err:
        error_msg = traceback.format_exc()
        for line in error_msg.strip().split("\n"):
            LOGGER.error(line)
        raise err

if __name__ == '__main__':
    # main()
    # create_superuser()

