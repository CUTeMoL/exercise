#!/usr/bin/env python3
import ftplib
import os

filename = "e:/tmp/t.txt"
targethost = "127.0.0.1"
targetport = 21
targetuser = "anonymous"
targetpasswd = "anonymous"
targetdir = "/"
ftp_object = ftplib.FTP()
ftp_object.connect(host=targethost, port=targetport)
ftp_object.login(user=targetuser, passwd=targetpasswd)

def ftp_upload(ftp_object, sourcefile, targetdir="/"):
    sourcefile_object = open(sourcefile,'rb')
    source_file_basename = os.path.basename(sourcefile)
    targetdir = targetdir.strip()
    try:
        if targetdir[-1] == "/":
            ftp_object.storbinary(f"STOR {targetdir}{source_file_basename}", sourcefile_object)
        else:
            ftp_object.storbinary(f"STOR {targetdir}/{source_file_basename}", sourcefile_object)
        return True
    except:
        return False
    finally:
        sourcefile_object.close()
if __name__ == "__main__":
    ftp_upload(ftp_object , filename, targetdir)
    ftp_object.quit()
