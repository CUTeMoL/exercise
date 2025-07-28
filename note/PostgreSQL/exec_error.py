#!/bin/python3
# -*- encoding: utf-8 -*-

class DependenciesListError(ValueError):
    error_type = [
        "",
        "dependencies.txt missing.",
        "dependencies.txt context is null."
    ]
    def __init__(self,error_code):
        self.error_code = error_code
        self.msg = self.error_type[self.error_code],
        super().__init__(self.msg)


class DependenciesMismatched(ValueError):
    def __init__(self,soft_name,version):
        self.msg = "%s == %s is mismatched"%(soft_name,version)
        super().__init__(self.msg)


class DownloadError(OSError):
    def __init__(self,error_code,msg,filename):
        self.error_code = error_code
        self.msg = msg
        super().__init__(self.error_code,self.msg,filename)


class ExtractError(OSError):
    def __init__(self,error_code,msg,filename):
        self.error_code = error_code
        self.msg = "extract file failed."
        super().__init__(self.msg)

