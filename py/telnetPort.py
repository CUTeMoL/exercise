import socket
from concurrent.futures import ThreadPoolExecutor
import time

ip_addrs = ["127.0.0.1", ]
ports = (port for port in range(1, 100))

def port_test(ip_addr, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
        telnet_object.settimeout(1)
        result = telnet_object.connect_ex((ip_addr, port))
    
    return ip_addr, port, result


if __name__ == "__main__":
    start = time.time()
    for ip_addr in ip_addrs:

        with ThreadPoolExecutor() as tpool:
            futures = [ tpool.submit(port_test, ip_addr, port) for port in ports ]
            for future in futures:
                if future.result()[2] == 0:
                    print(f"{future.result()[0]}:{future.result()[1]} is open.")
                # elif future.result()[2] == 10035:
                #     print(f"{future.result()[0]}:{future.result()[1]} is close.")
    end = time.time()
    print("cost %.2fs"%(end - start))
