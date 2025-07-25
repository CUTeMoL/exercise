#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import re
from typing import Optional, Tuple, Union

class VersionUtils:
    @staticmethod
    def parse_version(version_str: str) -> Tuple[Union[int, str], ...]:
        '''解析版本字符串为可比较的元组（支持语义化版本）'''
        version_str = version_str.lstrip('vV')
        parts = re.split(r'[.-]', version_str.split('-')[0].split(":")[-1].split("+")[0])  # 忽略预发布标签
        parsed = []
        for part in parts:
            try:
                parsed.append(int(part))
            except ValueError:
                parsed.append(part.lower())  # 字母部分转为小写
        return tuple(parsed)

    @staticmethod
    def compare_versions(v1:str, v2:str, operator:str=">=") -> bool:
        '''比较两个版本号,返回1/0/-1'''
        parsed_v1 = VersionUtils.parse_version(v1)
        parsed_v2 = VersionUtils.parse_version(v2)
        return eval("%s %s %s"%(parsed_v1,operator,parsed_v2))

    @staticmethod
    def is_valid(version_str: str) -> bool:
        '''验证版本号格式是否合法(不检查了,ubuntu下dpkg搜出来大多是不合规的)'''
        pattern = r'^[vV]?\d+(\.\d+)*(-[a-zA-Z0-9]+)?$'
        return bool(re.fullmatch(pattern, version_str))
