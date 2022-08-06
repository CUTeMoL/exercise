import psutil
import re


process_name = "QQ" # 例如定义要查询的进程名为QQ
process_dicts = {} # 空字典

for pid in psutil.pids():
    # 正则匹配名为process_name定义的进程，加入字典
    if re.search(".*{}.*".format(process_name), psutil.Process(pid).name()):
        process_dicts[psutil.Process(pid).pid] = [psutil.Process(pid).name(), psutil.Process(pid).ppid()]

for connection in psutil.net_connections():
    # 如过connection的pid在进程keys中则表示pid对应上了，删除这个key
    if connection.pid in process_dicts.keys():
        del process_dicts[connection.pid]

# 打印没匹配到的字典，里面剩下的就是卡死进程的真实的pid
print("pid\t\tprocess\t\t\tppid")
for key, value in process_dicts.items():
    print(f"{key}\t\t{value[0]}\t\t{value[1]}")

