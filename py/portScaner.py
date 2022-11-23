#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import socket
import time
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, freeze_support

__author__ = "lxw"
__last_mod_date__ = "2022.11.22"
__modify__ = "支持打包成EXE"
ip_addrs = []
ports = [port for port in range(1, 65536)] # 多进程传多参数不支持列表生成式...

def port_test(ip_addr, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
        telnet_object.settimeout(1)
        result = telnet_object.connect_ex((ip_addr, port))
    return ip_addr, port, result


def process_run(ip_ports):
    test_ip, test_ports = ip_ports
    with ThreadPoolExecutor(max_workers=6000) as tpool:
        futures = [ tpool.submit(port_test, test_ip, test_port) for test_port in test_ports ]
        for future in futures:
            if future.result()[2] == 0:
                print("{}:{} is open.".format(future.result()[0], future.result()[1]))
            # elif future.result()[2] == 10035:
            #     print(f"{future.result()[0]}:{future.result()[1]} is close.")


if __name__ == "__main__":
    freeze_support() # windows下打包为exe需要
    print("{}最后一次修改于{}".format(__author__, __last_mod_date__))
    print("更新了：{}".format(__modify__))
    print("下一次可以更新的内容为, 1.线程的异常处理 2.引入Ipy实现网段的扫描")

    try:
        while True:
            ip_addr = input("Input [ipaddress] to add the scan list until input [start] to run process: \n")
            if ip_addr == "start":
                break
            else:
                if re.match("127\.([0-9]{1,3}\.){2}[0-9]{1,3}", ip_addr):
                    print("use \"netstat -nao\" or \"netstat -natlp\".")
                elif re.match("([0-9]{1,3}\.){1,3}[0-9]{1,3}", ip_addr):
                    ip_addrs.append(ip_addr)
                else:
                    print("\nPlease enter the correct ip address and try again")
                    continue
    except KeyboardInterrupt:
        print("exit.")
        sys.exit()

    start = time.time()
    try:
        process_pool = Pool()
        for ip_addr in ip_addrs:
            # 只能传参一个所以使用元组打包地址和端口传入后再拆开
            process_pool.apply_async(process_run, ((ip_addr, ports), ))
            process_pool.close()
            time.sleep(10)
    except KeyboardInterrupt:
        process_pool.terminate()
    finally:
        process_pool.join() # 一旦join会屏蔽终止信号,等待子进程结束
        end = time.time()
        print("cost %.2fs"%(end - start))
        input("exit.")
