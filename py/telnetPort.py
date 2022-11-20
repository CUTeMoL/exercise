#!/usr/bin/env python3
#-*- coding: utf-8 -*- 
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

__author__ = "lxw"
__last_mod_date__ = "2022.11.20"
ip_addrs = ["150.158.93.164", "127.0.0.1", "119.3.77.172", ]
ports = [port for port in range(1, 65536)] # 多进程传多参数不支持列表生成式...

def port_test(ip_addr, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
        telnet_object.settimeout(1)
        result = telnet_object.connect_ex((ip_addr, port))
    return ip_addr, port, result


def process_run(ip_ports):
    test_ip, test_ports = ip_ports
    with ThreadPoolExecutor(max_workers=50000) as tpool:
        futures = [ tpool.submit(port_test, test_ip, test_port) for test_port in test_ports ]
        for future in futures:
            if future.result()[2] == 0:
                print(f"{future.result()[0]}:{future.result()[1]} is open.")
            # elif future.result()[2] == 10035:
            #     print(f"{future.result()[0]}:{future.result()[1]} is close.")


if __name__ == "__main__":
    print(f"{__author__}最后一次修改于{__last_mod_date__}")
    print("下一次可以更新的内容为,线程的异常处理")
    start = time.time()
    process_pool = Pool()
    for ip_addr in ip_addrs:
        # 只能传参一个所以使用元组打包地址和端口传入后再拆开
        process_pool.apply_async(process_run, ((ip_addr, ports), ))
    process_pool.close()
    process_pool.join()
    end = time.time()
    print("cost %.2fs"%(end - start))
