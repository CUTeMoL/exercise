import hashlib
import os

def md5sumcheck(file_object):
    object = hashlib.md5()
    with open(file=file_object, mode="rb") as md5_object:
        data = md5_object.read()
        object.update(data)
    return object.hexdigest().upper()

if __name__ == "__main__":
    while 1 == 1:
        file_name = input("Input the full path for the source file or input q to exit: ")
        if not file_name:
            continue
        if file_name != "q":
            print(os.path.basename(file_name))
            print(md5sumcheck(file_name))
        else:
            exit()