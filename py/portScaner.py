#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import socket
import time
import re
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support
from os import cpu_count
import ipaddress



__author__ = "lxw"
__last_mod_date__ = "2022.11.28"
__modify__ = "加入ipaddress模块,可以扫描网段"
ip_addrs = []
ports = [port for port in range(1, 65536)] # 多进程传多参数不支持列表推导式直接传参...


def port_TCP_test(ip_addr, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
        telnet_object.settimeout(1)
        result = telnet_object.connect_ex((ip_addr, port))
    return ip_addr, port, result


def process_run(ip_ports):
    test_ip, test_ports = ip_ports
    with ThreadPoolExecutor(max_workers=2000) as tpool:
        thread_results = [ tpool.submit(port_TCP_test, str(test_ip), test_port) for test_port in test_ports ]
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
    print("下一次可以更新的内容为, 1.加入xlsxwriter")
    try:
        while True:
            ip_addr = input("Input [ipaddress/subnet] or [ipaddress] to add the scan list until input [start] to run process: \n")
            if ip_addr.strip() == "start":
                print(ip_addrs)
                break
            else:
                if re.match("127\.([0-9]{1,3}\.){2}[0-9]{1,3}", ip_addr.strip()):
                    print("use \"netstat -nao\" or \"netstat -natlp\".")
                elif re.match("([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$", ip_addr.strip()):
                    ip_range = ipaddress.IPv4Network(ip_addr.strip(), False)
                    ip_addrs.extend(list(ip_range.hosts()))
                elif re.match("([0-9]{1,3}\.){3}[0-9]{1,3}$", ip_addr.strip()):
                    ip_addrs.append(ip_addr.strip())
                else:
                    print("\nPlease enter the correct ip address and try again.")
                    continue
    except KeyboardInterrupt:
        print("exit.")
        sys.exit()

    start = time.time()
    try:
        with ProcessPoolExecutor(max_workers=int(cpu_count()/2+1)) as ppool:
            process_results = [ ppool.submit(process_run, (ip_addr, ports)) for ip_addr in ip_addrs ]
            for process_result in as_completed(process_results):
                print("\nScan {} is completed.".format(process_result.result()))
    except KeyboardInterrupt:
        sys.exit()
    finally:
        end = time.time()
        print("Cost %.2fs"%(end - start))
        input("End.")
