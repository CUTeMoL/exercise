# network

## 一、网络接口层



## 二、网络层





## 三、传输层

| 协议  | 说明                                                           |
| --- | ------------------------------------------------------------ |
| TCP | Transmission control protocol 传输控制协议,可靠的、面向连接的协议传输效率低，类似于打电话 |
| UDP | User datagram protocol 用户数据报协议,不可靠、无连接的服务传输效率高，类似于群聊         |

#### tcp

##### 三次握手

1.主动方发送SYN包

SYN包中包含seq=(例如为2307338027)和ack=0，同时通知被动方下一个seq为2307338028

2.被动方发送SYN及ACK包

SYN及ACK包中包含seq=(例如为840465765)和ack=2307338028(这是回应主动方SYN-seq+1的序号)，同时通知主动方下一个seq为840465766

3.主动方发送ack包

ACK包中包含seq=(例如为2307338028)和ack=840465766(这是回应被动方SYN-seq+1的序号),同时通知被动方下一个seq为2307338028

##### TCP会话确认

对每个数据包都会进行确认

1.主动方发送seq=1 ack=1 data=9字节

2.被动方发送seq=1 ack=10 data=20字节

3.主动方发送seq=10 ack=21 data=12字节

4.被动方发送seq=21 ack=22 data=16字节

##### 四次挥手

1.主动方发送ACK(回应上一次的)以及FIN(终止信号)请求

2.被动方接受后，发送ACK，确认接受到终止信号

3.被动方发送FIN请求，断开连接

4.主动方发送ACK

##### TIME_WAIT作用

四次挥手中的第四次，主动关闭一方等待MSL(超时时间)时间再释放连接，这个状态就是TIME_WAIT。

由于TIME_WAIT的存在，短连接时关闭的socket会长时间占据大量的tuple空间

## 四、应用层


## 五、神奇操作

### 1. 创建命名空间隔离网络并赋予命名空间真实网卡mac(伪造mac地址)

```shell
#!/bin/bash

# ===== 可配置变量 =====
HOST_IF="eth0"                   # 宿主机物理出口网卡（根据实际修改）
NS_NAME="ns_1"                # 网络命名空间名称
VETH_HOST="veth_${HOST_IF}"            # 宿主机端虚拟网卡名
VETH_NS="veth_${NS_NAME}"                # 命名空间端虚拟网卡名
MAC_ADDR="00:16:3e:2c:e3:25"    # 要设置的 MAC 地址
NS_IP="10.200.0.2/24"           # 命名空间内 IP/掩码
HOST_IP="10.200.0.1/24"         # 宿主机端 IP/掩码
NET_PREFIX="10.200.0.0/24"      # NAT 源地址段
# ======================



# 清理旧环境
sudo ip netns delete "${NS_NAME}" 2>/dev/null
sudo ip link delete "${VETH_HOST}" 2>/dev/null

# 1. 重新创建空间
sudo ip netns add "${NS_NAME}"

# 2. 创建网卡对
sudo ip link add "${VETH_HOST}" type veth peer name "${VETH_NS}"

# 3. 将网卡塞入空间
sudo ip link set "${VETH_NS}" netns "${NS_NAME}"

# 4. 【核心关键】直接将物理机 MAC 赋予隔离空间内的网卡
sudo ip netns exec "${NS_NAME}" ip link set dev "${VETH_NS}" address "${MAC_ADDR}"

# 5. 配置空间内网卡 IP 为 ${NS_IP}
sudo ip netns exec "${NS_NAME}" ip address add "${NS_IP}" dev "${VETH_NS}"
sudo ip netns exec "${NS_NAME}" ip link set dev "${VETH_NS}" up
sudo ip netns exec "${NS_NAME}" ip link set lo up

# 6. 配置宿主机端网卡 IP
sudo ip address add "${HOST_IP}" dev "${VETH_HOST}"
sudo ip link set dev "${VETH_HOST}" up

# 7. 配置空间内默认网关（宿主机端 IP 作为网关）
sudo ip netns exec "${NS_NAME}" ip route add default via "${HOST_IP%/*}"  # 去掉掩码部分

# 8. 开启 IP 转发
sudo sysctl -w net.ipv4.ip_forward=1

# 9. 配置 NAT 转发（注意出口网卡为 ${HOST_IF}）
sudo iptables -t nat -A POSTROUTING -s "${NET_PREFIX}" -o "${HOST_IF}" -j MASQUERADE
sudo iptables -A FORWARD -i "${VETH_HOST}" -o "${HOST_IF}" -j ACCEPT
sudo iptables -A FORWARD -i "${HOST_IF}" -o "${VETH_HOST}" -m state --state RELATED,ESTABLISHED -j ACCEPT

# 10. DNS 配置
sudo mkdir -p /etc/netns/"${NS_NAME}"
echo "nameserver 8.8.8.8" | sudo tee /etc/netns/"${NS_NAME}"/resolv.conf
echo "nameserver 114.114.114.114" | sudo tee -a /etc/netns/"${NS_NAME}"/resolv.conf

# 11. 测试命名空间内访问 https://www.lxw.com
sudo ip netns exec "${NS_NAME}" curl -I -m 5 https://www.lxw.com
```