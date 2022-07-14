import filecmp
dir_left = "D:/soft"
dir_right = "D:/CUTeMoL"
print("左边的文件:",filecmp.dircmp(dir_left, dir_right).left_list)
print("右边的文件:",filecmp.dircmp(dir_left, dir_right).right_list)
print("左右共同存在的内容(不检验文件内容):", filecmp.dircmp(dir_left, dir_right).common)
print("左边独有的:", filecmp.dircmp(dir_left, dir_right).left_only)
print("右边独有的:", filecmp.dircmp(dir_left, dir_right).right_only)
print("两边目录都存在的子目录", filecmp.dircmp(dir_left, dir_right).common_dirs)
print("两边目录都存在的子文件", filecmp.dircmp(dir_left, dir_right).common_files)
print("左右共同存在的内容,检查文件的内容", filecmp.dircmp(dir_left, dir_right).same_files)
print("左右共同存在, 但内容不匹配的", filecmp.dircmp(dir_left, dir_right).diff_files)
