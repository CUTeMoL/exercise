#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import socket
import time
import re
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support

__author__ = "lxw"
__last_mod_date__ = "2022.11.22"
__modify__ = "解决KeyboardInterrupt不能停止脚本的问题"
ip_addrs = []
ports = [port for port in range(1, 65536)] # 多进程传多参数不支持列表生成式直接传参...

def port_test(ip_addr, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
        telnet_object.settimeout(1)
        result = telnet_object.connect_ex((ip_addr, port))
    return ip_addr, port, result


def process_run(ip_ports):
    test_ip, test_ports = ip_ports
    with ThreadPoolExecutor(max_workers=6000) as tpool:
        thread_results = [ tpool.submit(port_test, test_ip, test_port) for test_port in test_ports ]
        for thread_result in thread_results:
            if thread_result.result()[2] == 0:
                print("{}:{} is open.".format(thread_result.result()[0], thread_result.result()[1]))
            # elif thread_result.result()[2] == 10035:
            #     print(f"{thread_result.result()[0]}:{thread_result.result()[1]} is close.")
    return test_ip


if __name__ == "__main__":
    freeze_support() # windows下打包为exe需要
    print("{}最后一次修改于{}".format(__author__, __last_mod_date__))
    print("更新了：{}".format(__modify__))
    print("下一次可以更新的内容为, 1.引入Ipy实现网段的扫描")

    try:
        while True:
            ip_addr = input("Input [ipaddress] to add the scan list until input [start] to run process: \n")
            if ip_addr.strip() == "start":
                break
            else:
                if re.match("127\.([0-9]{1,3}\.){2}[0-9]{1,3}", ip_addr.strip()):
                    print("use \"netstat -nao\" or \"netstat -natlp\".")
                elif re.match("([0-9]{1,3}\.){1,3}[0-9]{1,3}", ip_addr.strip()):
                    ip_addrs.append(ip_addr.strip())
                else:
                    print("\nPlease enter the correct ip address and try again")
                    continue
    except KeyboardInterrupt:
        print("exit.")
        sys.exit()

    start = time.time()
    try:
        with ProcessPoolExecutor() as ppool:
            process_results = [ ppool.submit(process_run, (ip_addr, ports)) for ip_addr in ip_addrs ]
            for process_result in as_completed(process_results):
                print("\nScan {} is completed.".format(process_result.result()))
    except KeyboardInterrupt:
        sys.exit()
    finally:
        end = time.time()
        print("cost %.2fs"%(end - start))
        input("exit.")
