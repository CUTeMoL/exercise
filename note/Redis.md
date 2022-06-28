# Redis

## 一、安装

```shell
yum -y install gcc gcc-c++ kernel-devel
wget http://download.redis.io/releases/redis-5.0.4.tar.gz
tar zxf redis-5.0.4.tar.gz && mv redis-5.0.4/ /usr/local/redis
cd /usr/local/redis && make && make install
```

## 二、备份策略

### RDB

dump.rdb

在指定的时间间隔内将内存中的数据集快照写入磁盘， 也就是行话讲的Snapshot快照，它恢复时是将快照文件直接读到内存里

**优势**:

- 适合大规模的数据恢复
- 对数据完整性和一致性要求不高更适合使用
- 节省磁盘空间
- 恢复速度快

**劣势**:

- Fork的时候，内存中的数据被克隆了一份，大致2倍的膨胀性需要考虑
- 虽然Redis在fork时使用了**写时拷贝技术**,但是如果数据庞大时还是比较消耗性能
- 在备份周期在一定间隔时间做一次备份，所以如果Redis意外down掉的话，就会丢失最后一次快照后的所有修改

### AOF:

appendonly.aof

以**日志**的形式来记录每个写操作（增量保存）

只许追加文件但不可以改写文件

优势:

- 备份机制更稳健，丢失数据概率更低
- 可读的日志文本，通过操作AOF稳健，可以处理误操作。

劣势:

- 比起RDB占用更多的磁盘空间
- 恢复备份速度要慢
- 每次读写都同步的话，有一定的性能压力
- 存在个别Bug，造成恢复不能

## 三、systemd

/usr/lib/systemd/system/redis.service

```shell
[Unit]
Description=Redis persistent key-value database
After=network.target
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/redis-server /usr/local/redis/redis.conf --supervised systemd #启动
ExecStop=/usr/libexec/redis-shutdown #shutdown脚本
Type=notify
User=redis # 要创建用户
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

/usr/libexec/redis-shutdown

```shell
#!/bin/bash
#
# Wrapper to close properly redis and sentinel
test x"$REDIS_DEBUG" != x && set -x

REDIS_CLI=/usr/local/bin/redis-cli

# Retrieve service name
SERVICE_NAME="$1"
if [ -z "$SERVICE_NAME" ]; then
   SERVICE_NAME=redis
fi

# Get the proper config file based on service name
CONFIG_FILE="/usr/local/redis/$SERVICE_NAME.conf"

# Use awk to retrieve host, port from config file
HOST=`awk '/^[[:blank:]]*bind/ { print $2 }' $CONFIG_FILE | tail -n1`
PORT=`awk '/^[[:blank:]]*port/ { print $2 }' $CONFIG_FILE | tail -n1`
PASS=`awk '/^[[:blank:]]*requirepass/ { print $2 }' $CONFIG_FILE | tail -n1`
SOCK=`awk '/^[[:blank:]]*unixsocket\s/ { print $2 }' $CONFIG_FILE | tail -n1`

# Just in case, use default host, port
HOST=${HOST:-127.0.0.1}
if [ "$SERVICE_NAME" = redis ]; then
    PORT=${PORT:-6379}
else
    PORT=${PORT:-26739}
fi

# Setup additional parameters
# e.g password-protected redis instances
[ -z "$PASS"  ] || ADDITIONAL_PARAMS="-a $PASS"

# shutdown the service properly
if [ -e "$SOCK" ] ; then
        $REDIS_CLI -s $SOCK $ADDITIONAL_PARAMS shutdown
else
        $REDIS_CLI -h $HOST -p $PORT $ADDITIONAL_PARAMS shutdown
fi
```



## 四、Redis主从复制

master:

```shell
daemonize yes
bind 127.0.0.1 192.168.1.1
requirepass 123456 # 设置master连接密码，slave可省略
masterauth 123456 # slave连接master密码，master可省略
```

slave:

```shell
daemonize yes
bind 127.0.0.1 192.168.1.2
replicaof 192.168.1.1 6379
requirepass 123456 # 设置master连接密码，slave可省略
masterauth 123456 # slave连接master密码，master可省略
# slave-read-only yes #可选
```

```shell
info replication # 查看redis主从复制情况
```

## 五、哨兵模式(sentinel)

### 特点

当master挂了以后，sentinel会在slave中选择一个做为master，并修改它们的配置文件，其他slave的配置文件也会被修改，比如slaveof属性会指向新的master

当master重新启动后，它将不再是master而是做为slave接收新的master的同步数据

sentinel因为也是一个进程有挂掉的可能，所以sentinel也会启动多个形成一个sentinel集群

多sentinel配置的时候，sentinel之间也会自动监控

当主从模式配置密码时，sentinel也会同步将配置信息修改到配置文件中

一个sentinel或sentinel集群可以管理多个主从Redis，多个sentinel也可以监控同一个redis

sentinel最好不要和Redis部署在同一台机器，不然Redis的服务器挂了以后，sentinel也挂了

当使用sentinel模式的时候，客户端就不要直接连接Redis，而是连接sentinel的ip和port，由sentinel来提供具体的可提供服务的Redis实现，这样当master节点挂掉以后，sentinel就会感知并将新的master节点提供给使用者。

### 启动哨兵

1.新建sentinel.conf(所有运行哨兵的Node)

```shell
daemonize yes
logfile "/usr/local/redis/sentinel.log" # 哨兵的日志
dir "/usr/local/redis/sentinel" # 工作目录
sentinel monitor mymaster 192.168.1.1 6379 1 # 哨兵 监视 redis_master_name MASTER_IP PORT 至少n个哨兵进程同意迁移
sentinel auth-pass mymaster 123456 #master密码
sentinel down-after-milliseconds mymaster 30000 #主观下线时间（毫秒）
```

2.创建工作目录

```shell
mkdir /usr/local/redis/sentinel 
chown -R redis:redis /usr/local/redis
```

3.启动哨兵进程

```shell
redis-sentinel  /myredis/sentinel.conf 
```

### 哨兵事件

·       +reset-master ：主服务器已被重置。

·       +slave ：一个新的从服务器已经被 Sentinel 识别并关联。

·       +failover-state-reconf-slaves ：故障转移状态切换到了 reconf-slaves 状态。

·       +failover-detected ：另一个 Sentinel 开始了一次故障转移操作，或者一个从服务器转换成了主服务器。

·       +slave-reconf-sent ：领头（leader）的 Sentinel 向实例发送了 [SLAVEOF](/commands/slaveof.html) 命令，为实例设置新的主服务器。

·       +slave-reconf-inprog ：实例正在将自己设置为指定主服务器的从服务器，但相应的同步过程仍未完成。

·       +slave-reconf-done ：从服务器已经成功完成对新主服务器的同步。

·       -dup-sentinel ：对给定主服务器进行监视的一个或多个 Sentinel 已经因为重复出现而被移除 —— 当 Sentinel 实例重启的时候，就会出现这种情况。

·       +sentinel ：一个监视给定主服务器的新 Sentinel 已经被识别并添加。

·       +sdown ：给定的实例现在处于主观下线状态。

·       -sdown ：给定的实例已经不再处于主观下线状态。

·       +odown ：给定的实例现在处于客观下线状态。

·       -odown ：给定的实例已经不再处于客观下线状态。

·       +new-epoch ：当前的纪元（epoch）已经被更新。

·       +try-failover ：一个新的故障迁移操作正在执行中，等待被大多数 Sentinel 选中（waiting to be elected by the majority）。

·       +elected-leader ：赢得指定纪元的选举，可以进行故障迁移操作了。

·       +failover-state-select-slave ：故障转移操作现在处于 select-slave 状态 —— Sentinel 正在寻找可以升级为主服务器的从服务器。

·       no-good-slave ：Sentinel 操作未能找到适合进行升级的从服务器。Sentinel 会在一段时间之后再次尝试寻找合适的从服务器来进行升级，又或者直接放弃执行故障转移操作。

·       selected-slave ：Sentinel 顺利找到适合进行升级的从服务器。

·       failover-state-send-slaveof-noone ：Sentinel 正在将指定的从服务器升级为主服务器，等待升级功能完成。

·       failover-end-for-timeout ：故障转移因为超时而中止，不过最终所有从服务器都会开始复制新的主服务器（slaves will eventually be configured to replicate with the new master anyway）。

·       failover-end ：故障转移操作顺利完成。所有从服务器都开始复制新的主服务器了。

·       +switch-master ：配置变更，主服务器的 IP 和地址已经改变。 这是绝大多数外部用户都关心的信息。

·       +tilt ：进入 tilt 模式。

·       -tilt ：退出 tilt 模式。

## 六、Cluster模式

### 特点

存储的数据进行分片，根据一定的规则分配到多台机器

多个redis节点网络互联，数据共享

所有的节点都是一主一从（也可以是一主多从），其中从不提供服务，仅作为备用

支持在线增加、删除节点

客户端可以连接任何一个主节点进行读写

缺点: 不支持同时处理多个key（如MSET/MGET），因为redis需要把key均匀分布在各个节点上，并发量很高的情况下同时创建key-value会降低性能并导致不可预测的行为

### 启动Cluster

1.创建集群工作目录(每一台)

```shell
mkdir /usr/local/redis/cluster #集群工作目录
cp /usr/local/redis/redis.conf /usr/local/redis/cluster/redis.conf
chown -R redis:redis /usr/local/redis
mkdir -p /data/redis/cluster/redis # 数据存储目录
```

2.设置/usr/local/redis/cluster/redis.conf(每一台)

```shell
bind 192.168.1.1 #自己的集群通信IP
port 7001 #自己的集群通信PORT
daemonize yes
pidfile "/var/run/redis.pid"
logfile "/usr/local/redis/cluster/redis.log"
dir "/data/redis/cluster/redis" # 数据存储目录
masterauth 123456
requirepass 123456
appendonly yes
cluster-enabled yes #开启集群模式
cluster-config-file nodes.conf #节点配置文件，cluster自动生成在数据存储目录
cluster-node-timeout 15000 #通信超时时间
```

3.启动redis服务(启动每一台)

4.安装ruby[高版本省略]

```shell
#!/bin/bash
yum -y groupinstall "Development Tools"
yum install -y gdbm-devel libdb4-devel libffi-devel libyaml libyaml-devel ncurses-devel openssl-devel readline-devel tcl-devel
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
wget http://cache.ruby-lang.org/pub/ruby/2.2/ruby-2.2.3.tar.gz -P ~/rpmbuild/SOURCES
wget http://raw.githubusercontent.com/tjinjin/automate-ruby-rpm/master/ruby22x.spec -P ~/rpmbuild/SPECS
rpmbuild -bb ~/rpmbuild/SPECS/ruby22x.spec
rpm -ivh ~/rpmbuild/RPMS/x86_64/ruby-2.2.3-1.el7.x86_64.rpm
gem install redis                 #目的是安装这个，用于配置集群
cp /usr/local/redis/src/redis-trib.rb /usr/bin/
redis-trib.rb create --replicas 1 192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 192.168.1.4:7004 192.168.1.5:7005 192.168.1.6:7006 

```

5.创建集群

```shell
redis-cli -a 123456 --cluster create 192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 192.168.1.4:7004 192.168.1.5:7005 192.168.1.6:7006 --cluster-replicas 1
```

输入yes，接受配置

会自动生成nodes.conf文件

6.登陆集群

```shell
redis-cli -c -h 192.168.1.1 -p 7001 -a 123456
-c 集群方式登陆
-h 主机任意
-p 跟随主机
```

查看CLUSTER信息

```shell
CLUSTER INFO #集群状态
CLUSTER NODES #列出节点信息
```

### 新增节点

1.设置/usr/local/redis/cluster/redis.conf(每一台)

2.redis-cli中

```shell
CLUSTER MEET 192.168.1.7 7007
```

3.修改节点身份

```shell
redis-cli -c -h 192.168.1.8 -p 7008 -a 123456 cluster replicate $node_id
```

### 删除节点

```shell
CLUSTER FORGET $node_id
```

### 保存节点信息

```shell
CLUSTER SAVECONFIG
```

### 其他

槽(slot)

```shell
cluster addslots <slot> [slot ...] # 将一个或多个槽（ slot）指派（ assign）给当前节点。
cluster delslots <slot> [slot ...] # 移除一个或多个槽对当前节点的指派。
cluster flushslots # 移除指派给当前节点的所有槽，让当前节点变成一个没有指派任何槽的节点。
cluster setslot <slot> node <node_id># 将槽 slot 指派给 node_id 指定的节点，如果槽已经指派给另一个节点，那么先让另一个节点删除该槽>，然后再进行指派。
cluster setslot <slot> migrating <node_id> # 将本节点的槽 slot 迁移到 node_id 指定的节点中。
cluster setslot <slot> importing <node_id> # 从 node_id 指定的节点中导入槽 slot 到本节点。
cluster setslot <slot> stable # 取消对槽 slot 的导入（ import）或者迁移（ migrate）。

```

键

```shell
cluster keyslot <key> # 计算键 key 应该被放置在哪个槽上。
cluster countkeysinslot <slot> # 返回槽 slot 目前包含的键值对数量。
cluster getkeysinslot <slot> <count> # 返回 count 个 slot 槽中的键  
```

