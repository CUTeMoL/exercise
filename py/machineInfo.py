import os
import time
import psutil
import platform
import logging
import logging.handlers
'''
重写计划
需求1:统计CPU占用最高的进程
需求2:统计内存占用最高的进程
需求3:占用端口的进程名及pid
需求4:文件查找,按日期,按大小,按类别
需求5:查询结果日志记录
'''


os.chdir(os.path.dirname(__file__))
log_path = "%s_%s.log" %(platform.node(),time.strftime('%Y-%m-%d', time.localtime()))

formatter_object = logging.Formatter("%(message)s")

streamhandler_object = logging.StreamHandler(stream=None)
streamhandler_object.setLevel(logging.DEBUG)
streamhandler_object.setFormatter(formatter_object)


filehandler_object = logging.FileHandler(filename=log_path, mode='w', encoding="utf8", delay=False)
filehandler_object.setLevel(logging.INFO)
filehandler_object.setFormatter(formatter_object)

logger_object = logging.getLogger("machineInfo_%s" %(time.strftime('%Y-%m-%d', time.localtime())))
logger_object.setLevel(logging.DEBUG)
logger_object.addHandler(streamhandler_object)
logger_object.addHandler(filehandler_object)

def platform_info():
    print("-----系统硬件信息-----")
    print("\t您的系统为:" + platform.system())
    print("\t您的操作系统名称及版本号:" + platform.platform())
    print("\t您的操作系统版本号:" + platform.version())
    print("\t您的CPU生产商为:" + platform.machine())
    print("\t您的CPU信息为:" + platform.processor())
    print("\t获取操作系统的位数:", platform.architecture()[0])
    print("\t计算机名称:" + platform.node())
    format_boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time()))
    print("\t开机时间为{}".format(format_boot_time))
    # print("包含上面所有的信息汇总:" , platform.uname())

def total_info():
    logger_object.info(
'''
%s的当前系统为%s %s

当前cpu使用情况:
用户进程占用 %.2f %%,系统占用 %.2f %%, 剩余空闲 %.2f %% 
当前内存使用情况:
总量 %.2f GB, 已使用 %.2f GB 占比 %.2f %%, 剩余 %.2f GB
'''
        %(platform.node(),
        platform.system(), platform.architecture()[0],
        psutil.cpu_times().user * 100 / (psutil.cpu_times().idle + psutil.cpu_times().user + psutil.cpu_times().system),
        psutil.cpu_times().system * 100 / (psutil.cpu_times().idle + psutil.cpu_times().user + psutil.cpu_times().system),
        psutil.cpu_times().idle * 100 / (psutil.cpu_times().idle + psutil.cpu_times().user + psutil.cpu_times().system),
        psutil.virtual_memory().total / 1024 / 1024 / 1024,
        psutil.virtual_memory().used / 1024 / 1024 / 1024,
        psutil.virtual_memory().percent,
        psutil.virtual_memory().available / 1024 / 1024 / 1024
        )
    )
    logger_object.info("分区使用情况:")
    for partition in psutil.disk_partitions():
        logger_object.info(
            "分区: %s 挂载点: %s 文件系统: %s 总量: %.2f G 已用: %.2f G 占比 %.2f %% 剩余: %.2f G"
            %(
                partition.device,
                partition.mountpoint,
                partition.fstype,
                psutil.disk_usage(partition.mountpoint).total / 1024 / 1024 / 1024,
                psutil.disk_usage(partition.mountpoint).used / 1024 / 1024 / 1024,
                psutil.disk_usage(partition.mountpoint).percent,
                psutil.disk_usage(partition.mountpoint).free / 1024 / 1024 / 1024
            )
        )



def cpu_info():
    print("-----CPU相关信息-----")

def mem_info():
    print("-----内存相关信息-----")


def disk_info():
    print("-----磁盘的分区相关信息-----")

    print("---挂载的硬盘的IO信息---")
    for disk in psutil.disk_io_counters(perdisk=True):
        print("{}\t{}".format(str(disk).ljust(10, " "), psutil.disk_io_counters(perdisk=True)[disk]))


def net_info():
    print("-----总网络流量信息-----")
    print("\t共接受{}MB，发送{}MB".format(int(psutil.net_io_counters().bytes_recv) / 1024 / 1024,
                                    int(psutil.net_io_counters().bytes_sent) / 1024 / 1024))
    print("--每个网卡流量信息---")
    for if_name in psutil.net_io_counters(pernic=True):
        print("\t{}: 共接受{}MB，发送{}MB".format(str(if_name).ljust(15, " "),
                                            int(psutil.net_io_counters(pernic=True)[if_name].bytes_recv) / 1024 / 1024,
                                            int(psutil.net_io_counters(pernic=True)[if_name].bytes_sent) / 1024 / 1024))


def net_device():
    print("---每个网卡状态信息---")
    for if_name in psutil.net_if_addrs():
        print(f"{if_name} 启用状态：{psutil.net_if_stats()[if_name].isup} ")
        for i in range(len(psutil.net_if_addrs()[if_name])):
            print(f"\t{psutil.net_if_addrs()[if_name][i]}")


def connect_info():
    print("---当前连接情况---")
    for connection in psutil.net_connections():
        print(connection)


def login_info():
    print("-----登录的用户信息-----")
    print(f"有 {len(psutil.users())} 个用户登录到此机器")
    for user in psutil.users():
        print(
            f"已登录用户: {user.name} 来自: {user.host} "
            f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.started))} "
            f"终端进程id: {user.pid}")


# print("\033[31;1;38m-----打印每个进程相关信息-----\033[0m")
# for pid in psutil.pids():
#     print(psutil.Process(pid))

def search_big_files():
    dir_input = input("检索路径(例如 c:/ ): ")
    bytes_input = int(input("检索大于此大小的文件(MB)： "))
    for root, dirs, files in os.walk(dir_input, topdown=False):
        for name in files:
            try:
                if os.path.getsize(os.path.join(root, name)) >= (1024 * 1024 * bytes_input):
                    print("大于 %d MB的文件：%s 大小：%.2f MB"
                          % (bytes_input, os.path.join(root, name),
                             os.path.getsize(os.path.join(root, name)) / 1024 / 1024))
            except FileNotFoundError:
                pass
    # for name in dirs:
    #     print(os.path.join(root, name), os.path.getsize(os.path.join(root, name)))


def help_info():
    print('''
林大师(精简版)：
    1\t系统硬件信息
    2\tCPU信息
    3\t内存相信息
    4\t磁盘信息
    5\t网络信息
    6\t网卡状态、地址信息
    7\t连接情况
    8\t当前登录信息
    9\t查询大文件
    h\t获得此帮助信息
    其他任意键退出
    ''')

total_info()
help_info()
while True:
    print("\n")
    command_input = input("输入指令: ")
    if command_input == "1":
        platform_info()
    elif command_input == "2":
        cpu_info()
    elif command_input == "3":
        mem_info()
    elif command_input == "4":
        disk_info()
    elif command_input == "5":
        net_info()
    elif command_input == "6":
        net_device()
    elif command_input == "7":
        connect_info()
    elif command_input == "8":
        login_info()
    elif command_input == "9":
        search_big_files()
    elif command_input == "h":
        help_info()
    else:
        exit()
