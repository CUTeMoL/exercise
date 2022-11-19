import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

ip_addrs = ["150.158.93.164", "127.0.0.1", ]
ports = [port for port in range(1, 65536)]

def port_test(ip_addr, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as telnet_object:
            telnet_object.settimeout(1)
            result = telnet_object.connect_ex((ip_addr, port))
        return ip_addr, port, result
    except KeyboardInterrupt:
        raise



def ip_test(ip_ports):
    try:
        test_ip, test_ports = ip_ports
        with ThreadPoolExecutor() as tpool:
            futures = [ tpool.submit(port_test, test_ip, test_port) for test_port in test_ports ]
            for future in futures:
                if future.result()[2] == 0:
                    print(f"{future.result()[0]}:{future.result()[1]} is open.")
                # elif future.result()[2] == 10035:
                #     print(f"{future.result()[0]}:{future.result()[1]} is close.")
    except KeyboardInterrupt:
        raise

if __name__ == "__main__":
    start = time.time()
    try:
        p = Pool()
        for ip_addr in ip_addrs:
            p.apply_async(ip_test, [(ip_addr, ports)])

        p.close()
        p.join()
    except Exception:
        sys.exit()

    finally:
        end = time.time()
        print("cost %.2fs"%(end - start))
