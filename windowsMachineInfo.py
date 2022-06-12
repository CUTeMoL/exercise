import os
import time
import psutil
import platform


# WINDOWS


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


def cpu_info():
    print("-----CPU相关信息-----")
    print(f"\tcpu核心数(包含逻辑cpu): {psutil.cpu_count(logical=True)}")
    # print(f"总状态百分比: {psutil.cpu_times_percent()}")
    # print(f"总状态: {psutil.cpu_times()}")
    print("\t用户进程使用: %.2f, 百分比: %.2f " % (psutil.cpu_times().user,
                                          psutil.cpu_times().user * 100 / (
                                                      psutil.cpu_times().idle +
                                                      psutil.cpu_times().user +
                                                      psutil.cpu_times().system)))
    print("\t系统进程使用: %.2f, 百分比: %.2f " % (psutil.cpu_times().system,
                                          psutil.cpu_times().system * 100 / (
                                                      psutil.cpu_times().idle +
                                                      psutil.cpu_times().user +
                                                      psutil.cpu_times().system)))
    print("\t空闲: %.2f, 百分比: %.2f " % (psutil.cpu_times().idle,
                                      psutil.cpu_times().idle * 100 / (
                                                  psutil.cpu_times().idle +
                                                  psutil.cpu_times().user +
                                                  psutil.cpu_times().system)))
    # print(f"进程等待: {psutil.cpu_times().iowait}, 百分比: {psutil.cpu_times_percent().iowait}")
    # print(f"硬中断处理时间: {psutil.cpu_times().irq}, 百分比: {psutil.cpu_times_percent().irq}")
    # print(f"软中断处理时间: {psutil.cpu_times().softirq}, 百分比: {psutil.cpu_times_percent().softirq}")
    # print(f"系统运行在虚拟机中的时候，被其他虚拟机占用的 CPU 时间: {psutil.cpu_times().steal}, "
    #       f"百分比: {psutil.cpu_times_percent().steal}")
    # print(f"运行虚拟机占用的 CPU 时间: {psutil.cpu_times().guest}, "
    #       f"百分比: {psutil.cpu_times_percent().guest}")
    # print(f"以低优先级运行虚拟机的时间: {psutil.cpu_times().guest_nice}, "
    #       f"百分比: {psutil.cpu_times_percent().guest_nice}")
    print("---每一个cpu运行情况---")
    for cpu_time in psutil.cpu_times(percpu=True):
        print(f"\t用户进程使用: {cpu_time.user}, 系统进程使用: {cpu_time.system}, 空闲:{cpu_time.idle}")


def mem_info():
    print("-----内存相关信息-----")
    print("物理内存使用情况: ")
    print(f"\t内存总量: {psutil.virtual_memory().total / 1024 / 1024} MB "
          f"剩余可用量: {psutil.virtual_memory().available / 1024 / 1024} MB "
          f"已使用百分比: {psutil.virtual_memory().percent} % \n"
          f"swap内存使用情况：\n"
          f"\tswap内存总量: {psutil.swap_memory().total / 1024 / 1024} MB   "
          f"swap内存剩余可用: {psutil.swap_memory().free / 1024 / 1024} MB   "
          f"swap内存已用: {psutil.swap_memory().used / 1024 / 1024} MB   "
          f"百分比: {psutil.swap_memory().percent} % ")


def disk_info():
    print("-----磁盘的分区相关信息-----")
    for partition in psutil.disk_partitions():
        print(f"分区: {partition.device}\t挂载点: {partition.mountpoint}\t文件系统: {partition.fstype}", end="\t")
        print(f"总量: {psutil.disk_usage(partition.mountpoint).total / 1024 / 1024 / 1024} GB\t"
              f"已用: {psutil.disk_usage(partition.mountpoint).used / 1024 / 1024 / 1024} GB\t"
              f"已用百分比: {psutil.disk_usage(partition.mountpoint).percent} %\t"
              f"剩余: {psutil.disk_usage(partition.mountpoint).free / 1024 / 1024 / 1024} GB\t")
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
