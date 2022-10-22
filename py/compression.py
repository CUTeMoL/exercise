import os
import tarfile
import sys
def compression(source, target):
    file_path, file_basename = os.path.split(os.path.abspath(source))
    os.chdir(file_path)
    with tarfile.open(os.path.abspath(target), "w:gz", compresslevel=9) as tarfile_object:
        tarfile_object.add(file_basename)

if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 3:
        if not os.path.exists(os.path.split(os.path.abspath(sys.argv[2]))[0]):
            print("target dir path is wrong")
        elif os.path.exists(sys.argv[1]):
            compression(sys.argv[1], sys.argv[2])
        else:
            print("source path is wrong")
    else:
        print(f"format: {sys.argv[0]} source target")