#!/bin/python3
# -*- encoding: utf-8 -*-
import re
from version_utils import VersionUtils
from exec_cmd import exec_cmd
import os

def check_dependencies():
    '''
    检查依赖是否安装成功(不使用)
    参考命令: dpkg -s readline-common |grep version
    '''
    pass


class Soft(object):
    def __init__(self, name):
        self.name = name
        self.Version = (-1,-1,-1)
        self.load_info()

    def load_info(self):
        '''载入软件信息'''
        code, msg = exec_cmd("dpkg -s %s"%(self.name))
        if code != 0:
            self.exist = False
            # self.install()
        else:
            self.exist = True
            self.info = msg
            for line in msg.replace("\r\n","\n").split("\n"):
                # print(line)
                match_key = re.compile("(?P<key>[0-9a-zA-Z]*):\s*(?P<value>.*)")
                if match_key.match(line):
                    soft_key = match_key.match(line).group("key")
                    setattr(self, soft_key, match_key.match(line).group("value"))
                else:
                    setattr(self, soft_key, getattr(self,soft_key)+"\n"+line)
        return self

    def install(self):
        '''安装软件'''
        code, msg = exec_cmd("apt install -y %s"%(self.name))
        if code != 0:
            self.exist = False
            self.error = msg
            print(code)
        else:
            self.load_info()
        return code

    def compare_versions(self, v2:str, operator:str=">="):
        '''对比版本是否合格 dpkg --compare_versions 判断时如果版本号存在":",则会判断失败,因此重写判断方式'''
        return VersionUtils.compare_versions(self.Version, v2, operator)


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__),"dependencies.txt")) as f:
        requirements = f.read().replace("\r\n","\n").split("\n")

    for requirement in requirements:
        if not requirement.startswith("#") and requirement != "":
            # print(requirement)
            requirement_soft = Soft(requirement.split(">=")[0])
            print("%s\t%s%s\t%s"%(requirement_soft.name,requirement_soft.Version,requirement.replace(requirement_soft.name,""),requirement_soft.compare_versions(requirement.split(">=")[1])))
            # print(requirement_soft.Version)
            # print(requirement_soft.compare_versions(requirement.split(">=")[1]))
