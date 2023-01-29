import os
import time
import psutil
import platform

'''
重写计划
需求1:统计CPU占用最高的进程
需求2:统计内存占用最高的进程
需求3:占用端口的进程名及pid
需求4:文件查找,按日期,按大小,按类别

'''
listen_list = []
process_list = []
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
    cpu_percent = psutil.cpu_times_percent(interval=5)
    print('''
%s的当前系统为%s %s

当前cpu使用情况:
用户进程占用 %.2f %%,系统占用 %.2f %%, 剩余空闲 %.2f %% 
当前内存使用情况:
总量 %.2f GB, 已使用 %.2f GB 占比 %.2f %%, 剩余 %.2f GB
'''
        %(
        platform.node(),
        platform.system(), platform.architecture()[0],
        cpu_percent.user,
        cpu_percent.system,
        cpu_percent.idle,
        psutil.virtual_memory().total / 1024 / 1024 / 1024,
        psutil.virtual_memory().used / 1024 / 1024 / 1024,
        psutil.virtual_memory().percent,
        psutil.virtual_memory().available / 1024 / 1024 / 1024
        )
    )
    print("分区使用情况:")
    for partition in psutil.disk_partitions():
        print(
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
    print("CPU核心数: %d 逻辑线程数: %d 主频: %.2f Mhz"%(psutil.cpu_count(logical=False), psutil.cpu_count(logical=True), psutil.cpu_freq(percpu=False).current))
    load_avg = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
    print("CPU平均占用情况:\n1分钟: %.2f %% 5分钟: %.2f %% 15分钟: %.2f %%"%(load_avg[0], load_avg[1], load_avg[2]))
    cpu_percent = psutil.cpu_times_percent(interval=5)
    print("当前用户进程占用 %.2f %%,系统占用 %.2f %%, 剩余空闲 %.2f %%" 
        %(
            cpu_percent.user,
            cpu_percent.system,
            cpu_percent.idle
        )
    )
    for process in psutil.process_iter():
        # print(process.as_dict())
        process_list.append(
            {
                "exe": process.as_dict()["exe"],
                "memory_percent": process.as_dict()["memory_percent"],
                "cpu_percent": process.as_dict()["cpu_percent"],
                "create_time": process.as_dict()["create_time"]
            }
        )
    process_list.sort(key=lambda x:(x["cpu_percent"], x["memory_percent"]), reverse=True)
    print(process_list[0:10])


                                                                                                                                       
def mem_info():
    print("-----内存相关信息-----")
    print("总量 %.2f GB, 已使用 %.2f GB 占比 %.2f %%, 剩余 %.2f GB" 
        %(
            psutil.virtual_memory().total / 1024 / 1024 / 1024,
            psutil.virtual_memory().used / 1024 / 1024 / 1024,
            psutil.virtual_memory().percent,
            psutil.virtual_memory().available / 1024 / 1024 / 1024
        )
    )

def disk_info():
    print("-----磁盘的分区相关信息-----")
    for partition in psutil.disk_partitions():
        print(
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


def net_info():
    print("-----总网络流量信息-----")
    print("共接受 %.2f MB,发送 %.2f MB"
        %(
            int(psutil.net_io_counters().bytes_recv) / 1024 / 1024,
            int(psutil.net_io_counters().bytes_sent) / 1024 / 1024
        )
    )
    print("--每个网卡流量信息---")
    for if_name in psutil.net_io_counters(pernic=True):
        print("%s: 共接受 %.2f MB,发送 %.2f MB"
            %(
                if_name,
                int(psutil.net_io_counters(pernic=True)[if_name].bytes_recv) / 1024 / 1024,
                int(psutil.net_io_counters(pernic=True)[if_name].bytes_sent) / 1024 / 1024
            )
        )


def net_device():
    print("---每个网卡状态信息---")
    for if_name in psutil.net_if_addrs():
        print("%s\nstatus: %s "%(if_name, psutil.net_if_stats()[if_name].isup), end="")
        for i in range(len(psutil.net_if_addrs()[if_name])):
            if psutil.net_if_addrs()[if_name][i].family.value == -1:
                print("MAC: %s "%(psutil.net_if_addrs()[if_name][i].address), end="")
            elif psutil.net_if_addrs()[if_name][i].family.value == 2:
                print("IPV4address: %s "%(psutil.net_if_addrs()[if_name][i].address), end="")
            elif psutil.net_if_addrs()[if_name][i].family.value == 23:
                print("IPV6address: %s "%(psutil.net_if_addrs()[if_name][i].address), end="")
        print("\n")

def connect_info():
    print("---当前连接情况---")
    for connection in psutil.net_connections():
        if connection.status == "LISTEN":
            if connection.family.name == "AF_INET":
                listen_list.append(
                    {
                        "protocol": "TCP" if (connection.type.name == "SOCK_STREAM") else "UDP",
                        "pid": connection.pid,
                        "process": psutil.Process(connection.pid).name(),
                        "port": "%s:%s"%(connection.laddr.ip,connection.laddr.port)
                    }
                )
            elif connection.family.name == "AF_INET6":
                listen_list.append(
                    {
                        "protocol": "TCP6" if (connection.type.name == "SOCK_STREAM") else "UDP6",
                        "pid": connection.pid,
                        "process": psutil.Process(connection.pid).name(),
                        "port": "%s:%s"%(connection.laddr.ip,connection.laddr.port)
                    }
                )

    listen_list.sort(key=lambda x:(x["protocol"],x["port"]))
    print("%-10s %-20s %-10s %-6s"%("protocol","listen","pid","process"))
    for listen_object in listen_list:
        print("%-10s %-20s %-10s %-6s"%(listen_object["protocol"],listen_object["port"],listen_object["pid"],listen_object["process"]))


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
