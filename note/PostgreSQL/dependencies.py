#!/bin/python3
# -*- encoding: utf-8 -*-

from version_utils import VersionUtils

def check_dependencies():
    '''
    检查依赖是否安装成功
    参考命令: dpkg -s readline-common |grep version
    '''
    pass


class soft(object):
    def __init__(self, name, soft_type="dpkg"):
        self.name = name
        self.type = soft_type

    def is_exist(self):
        '''判断是否已存在软件'''
        