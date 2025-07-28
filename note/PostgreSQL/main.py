#!/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import sys
import os
import re
import logging
import logging.config
import json
import traceback
from exec_command import exec_cmd,Command
from dependencies import Soft
from exec_error import DependenciesListError, DependenciesMismatched, DownloadError, ExtractError
from file_processing import File

## 全局变量设置 ##
WORK_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(WORK_PATH)
TMP_PATH = os.path.join(WORK_PATH,"tmp")
if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)
logging.config.fileConfig('conf/logging.conf')
LOGGER = logging.getLogger('POSTGRESQL_INSTALL')
INSTALL_CONFIG_FILE = os.path.join(WORK_PATH,"conf/install.json")
with open(INSTALL_CONFIG_FILE, "r") as INSTALL_CONFIG_FILE_HANDLER:
    INSTALL_CONFIG = json.loads(INSTALL_CONFIG_FILE_HANDLER.read())
PARAMETER_CONFIG_FILE = os.path.join(WORK_PATH,"conf/configure_parameter.conf")
with open(PARAMETER_CONFIG_FILE, "r") as PARAMETER_CONFIG_FILE_HANDLER:
    PARAMETER_CONFIG = PARAMETER_CONFIG_FILE_HANDLER.read().strip().replace("\r\n","\n").split("\n")


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
                if requirement_soft.exist is False or (not requirement_soft.compare_versions(match_soft.group("Required"),match_soft.group("operator")) and i <= 2):
                    LOGGER.warning("依赖软件%s版本检查异常,执行安装依赖软件..."%(requirement_soft.name))
                    requirement_soft.install()
                elif requirement_soft.exist is False or (not requirement_soft.compare_versions(match_soft.group("Required"),match_soft.group("operator")) and i == 2 ):
                    LOGGER.error("依赖软件版本检查异常,执行安装依赖软件失败,退出.")
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
        package_name = "postgresql-%s%s"%(version,file_name_extension)
        package_path = os.path.join(TMP_PATH,package_name)
        package_md5file_name = "postgresql-%s%s.md5"%(version,file_name_extension)
        package_md5file_path = os.path.join(TMP_PATH,package_md5file_name)
        download_package_url = "%sv%s/%s"%(base_url,version,package_name)
        download_md5_url = "%sv%s/%s"%(base_url,version,package_md5file_name)
        package_md5file = File(package_md5file_path)
        package = File(package_path)
        LOGGER.info("开始下载源码包MD5文件%s"%(package_path))
        package_md5file.download(download_md5_url)
        with open(package_md5file_path,"r") as package_md5_f:
            package_md5_require = package_md5_f.read().split()[0].strip().lower()
        LOGGER.info("开始下载源码包文件%s"%(package_path))
        package.download(download_package_url)
    except Exception as err:
        error_msg = traceback.format_exc()
        for line in error_msg.replace("\r\n","\n").split("\n"):
            LOGGER.error(line)
        raise DownloadError(10001,str(err),package_path)
    LOGGER.info("源码包%s验证MD5"%(package_path))
    if package.md5sum() == package_md5_require:
        LOGGER.info("源码包%s验证MD5:[%s]通过"%(package_path,package_md5_require))
        return True
    else:
        raise DownloadError(10002,"md5sum neq %s"%(package_md5_require))
        

def extract_source_package(package_path,version,file_name_extension):
    '''
    解压源码包
    '''
    package = File(package_path)
    LOGGER.info("开始解压源码包")
    code, msg = package.extract(TMP_PATH,file_name_extension)
    if code != 0:
        LOGGER.error("解压失败,详见以下错误信息:")
        LOGGER.error(msg)
        raise ExtractError(10003,msg,package_path)
    LOGGER.info("解压源码包完成")
    return True

def main():
    # requirements = read_dependencies()
    check_dependencies(read_dependencies())
    destination = os.path.join(TMP_PATH,"postgresql-%s%s"%(INSTALL_CONFIG["version"],INSTALL_CONFIG["file_name_extension"]))
    download_package(INSTALL_CONFIG["base_url"],INSTALL_CONFIG["version"],INSTALL_CONFIG["file_name_extension"])
    extract_source_package(destination,INSTALL_CONFIG["version"],INSTALL_CONFIG["file_name_extension"])


if __name__ == '__main__':
    main()
