import difflib
file1 = input("对比文件1路径: ")
file2 = input("对比文件2路径: ")
file3 = input("生成diff.html路径: ")
with open(file1, "r", encoding="utf8") as f1:
    f1lines = f1.read().splitlines(True)
with open(file2, "r", encoding="utf8") as f2:
    f2lines = f2.read().splitlines(True)
result_message = difflib.HtmlDiff().make_file(f2lines, f1lines)
with open(file3, "w", encoding="utf8") as f3:
    f3.write(result_message)
