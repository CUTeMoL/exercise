import filecmp
import os
import sys
import re
import shutil


tmp_list = []


def compareme(dir1, dir2):
    dir_comp = filecmp.dircmp(dir1, dir2) # 比对两个目录
    only_in_left = dir_comp.left_only # 只有左边有的
    diff_in_one = dir_comp.diff_files # 存在差异的
    for left in only_in_left:
        tmp_list.append(os.path.abspath(os.path.join(dir1, left))) #只有左边有的添加入传送列表
    for diff in diff_in_one:
        tmp_list.append(os.path.abspath(os.path.join(dir1, diff))) # 存在差异的添加入传送列表
    if len(dir_comp.common_dirs) > 0: #如果存在子目录
        for common_dir in dir_comp.common_dirs:
            compareme(os.path.abspath(os.path.join(dir1, common_dir)),
                      os.path.abspath(os.path.join(dir1, common_dir))) #子目录进行比较后添加进传送列表
    return tmp_list


def main():
    if len(sys.argv) > 2:
        dir1 = sys.argv[1]
        dir2 = sys.argv[2] #接受参数赋值
    else:
        print(f"Usage: {sys.argv[0]}, dataDir -> backupDir")
        sys.exit()
    source_files = compareme(dir1, dir2) # 比对目录,返回差异列表
    dir1 = os.path.abspath(dir1) #更新路径为绝对路径
    if not dir2.endswith("/"):
        dir2 = dir2 + "/" #保证目标目录的参数是目录格式
    dir2 = os.path.abspath(dir2) #获取目录的绝对路径
    destination_files = [] # 目的文件
    createdir_bool = False #是否创建目录符号
    for source_file in source_files: #遍历的差异列表中的文件后目录
        destination_dir = re.sub(dir1, dir2, source_file) #替换文件路径为backup目录
        destination_files.append(destination_dir)
        if os.path.isdir(source_file):
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir) # 如果是目录但backup目录不存在，则创建这个目录
                createdir_bool = True #修改创建目录的标志
    if createdir_bool:
        destination_files = []
        source_files.clear()
        source_files = compareme(dir1, dir2) #清空记录，重新遍历创建目录的内容
        for source_file in source_files: #遍历的差异列表中的文件后目录
            destination_dir = re.sub(dir1, dir2, source_file) #替换文件路径为backup目录
            destination_files.append(destination_dir)
    print(f"update item: \n{source_files}")
    copy_pairs = zip(source_files, destination_files) #顺序一致，将dir1和dir2打包成元组
    for copy_pair in copy_pairs:
        if os.path.isfile(copy_pair[0]):
            shutil.copyfile(copy_pair[0], copy_pair[1]) #复制文件


if __name__ == "__main__":
    main()
