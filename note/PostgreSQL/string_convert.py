#!/bin/python3
# -*- encoding: utf-8 -*-
import hashlib

def string_to_sha512(text: str) -> str:
    """将字符串转换为SHA512哈希值"""
    sha512 = hashlib.sha512()
    sha512.update(text.encode('utf-8'))
    return sha512.hexdigest()