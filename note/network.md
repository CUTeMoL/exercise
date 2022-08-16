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