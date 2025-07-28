#!/bin/python3
# -*- encoding: utf-8 -*-
import sys
import os
import hashlib
import requests
import subprocess
import locale
from exec_command import exec_cmd,exec_cmd_timeout,Command
from tqdm import tqdm


class File():
    def __init__(self, file_path):
        self.path = os.path.normpath(file_path)
        self.name = os.path.basename(file_path)

    def download(self,url):
        # self.downloadcmd = Commamd(["wget","-c",url,"-O",self.path,"-o",logfile], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 检查已经下载的部分
        resume_header = {}
        if os.path.exists(self.path):
            file_size = os.path.getsize(self.path)
            resume_header = {'Range': 'bytes=%s-'%(file_size)}
        response = requests.get(url, headers=resume_header, stream=True)
        total_size = int(response.headers.get('content-length', 0)) + (file_size if 'Range' in resume_header else 0)
    
        progress_bar = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=os.path.basename(self.path),
            initial=file_size if 'Range' in resume_header else 0
        )
        mode = 'ab' if 'Range' in resume_header else 'wb'
        with open(self.path, mode) as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        progress_bar.close()
        return self


    def md5sum(self):
        container = hashlib.md5()
        with open(file=self.path,mode="rb") as f:
            data = f.read()
        container.update(data)
        self.md5 = container.hexdigest().lower()
        return self.md5

    def extract(self,destination,file_name_extension):
        self.file_name_extension = file_name_extension
        tty_coding = locale.getdefaultlocale()[1]
        extract_type = "-xjvf" if self.file_name_extension == ".tar.bz2" else "-xzvf"
        cmd = ["tar", extract_type, self.path, "-C", destination]
        extract_command = Command(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = extract_command.communicate()
        if extract_command.returncode != 0:
            return extract_command.returncode,stderr.decode(tty_coding).replace("\r\n","\n")
        return extract_command.returncode,stdout.decode(tty_coding).replace("\r\n","\n")


if __name__ == "__main__":
    a = File("postgresql-17.5.tar.gz")
    a.download("https://ftp.postgresql.org/pub/source/v17.5/postgresql-17.5.tar.gz")
