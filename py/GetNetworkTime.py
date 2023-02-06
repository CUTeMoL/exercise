import time
import socket
import struct
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b'\x23' + 47 * b'\0', ('ntp.aliyun.com', 123))
    result = s.recvfrom(1024)[0]
print(result) # 原始编码
print(struct.unpack(b'!12I', result)) # 解码
timestamp_network = struct.unpack(b'!12I', result)[10] - 2208988800 # 网络时间戳1900开始所以减70年
timestamp_local = time.time() #本地时间戳1970开始
print("network:",time.ctime(timestamp_network))
print("localtime:", time.ctime(timestamp_local))
print(timestamp_network, "-", timestamp_local, end=" ")
print(timestamp_network - timestamp_local)
print(timestamp_local, "-", timestamp_network, end=" ")
print(timestamp_local - timestamp_network)

# python -c "import time;import socket;import struct;s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM);s.sendto(b'\x23'+47*b'\0', ('ntp.aliyun.com', 123));result=s.recvfrom(1024)[0];s.close;print(struct.unpack(b'!12I', result)[10]-2208988800-time.time());"
