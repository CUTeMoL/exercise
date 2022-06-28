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
requirepass 123456 # 设置连接密码
masterauth 123456 # slave连接master密码
```

slave:

```shell
daemonize yes
bind 127.0.0.1 192.168.1.2
replicaof 192.168.1.1 6379
requirepass 123456
masterauth 123456
# slave-read-only yes #可选
```

```shell
info replication # 查看redis主从复制情况
```

### 原理

Slave启动成功连接到master后会发送一个sync命令

Master接到命令启动后台的存盘进程，同时收集所有接收到的用于修改数据集命令， 在后台进程执行完毕之后，master将传送整个数据文件到slave,以完成一次完全同步

全量复制：而slave服务在接收到数据库文件数据后，将其存盘并加载到内存中。

增量复制：Master继续将新的所有收集到的修改命令依次传给slave,完成同步

但是只要是重新连接master,一次完全同步（全量复制)将被自动执行

## 五、哨兵模式(sentinel)

### 特点

当master挂了以后，sentinel会在slave中选择一个做为master，并修改它们的配置文件，其他slave的配置文件也会被修改，比如slaveof属性会指向新的master

根据优先级别：slave-priority 决定主机 slave-priority值越小优先级越高

当master重新启动后，它将不再是master而是做为slave接收新的master的同步数据

sentinel因为也是一个进程有挂掉的可能，所以sentinel也会启动多个形成一个sentinel集群

多sentinel配置的时候，sentinel之间也会自动监控

当主从模式配置密码时，sentinel也会同步将配置信息修改到配置文件中

一个sentinel或sentinel集群可以管理多个主从Redis，多个sentinel也可以监控同一个redis

sentinel最好不要和Redis部署在同一台机器，不然Redis的服务器挂了以后，sentinel也挂了

当使用sentinel模式的时候，客户端就不要直接连接Redis，而是连接sentinel的ip和port，由sentinel来提供具体的可提供服务的Redis实现，这样当master节点挂掉以后，sentinel就会感知并将新的master节点提供给使用者。

### 启动哨兵

1.创建工作目录

```shell
mkdir /usr/local/redis/sentinel
```

2.新建/usr/local/redis/sentinel/sentinel.conf(所有运行哨兵的Node上，或需要运行哨兵的Node)

```shell
daemonize yes
logfile "/usr/local/redis/sentinel.log" # 哨兵的日志
dir "/usr/local/redis/sentinel" # 工作目录rdb或aof的存放路径
sentinel monitor mymaster 192.168.1.1 6379 1 # 哨兵 监视 redis_master_name MASTER_IP PORT 至少n个哨兵进程同意迁移
sentinel auth-pass mymaster 123456 # master密码
sentinel down-after-milliseconds mymaster 30000 #主观下线时间（毫秒）
```

3.启动哨兵进程

```shell
chown -R redis:redis /usr/local/redis
/usr/local/bin/redis-sentinel  /usr/local/bin/sentinel.conf 
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
```

2.设置/usr/local/redis/cluster/redis.conf(每一台)

```shell
bind 1270.0.1 192.168.1.1 #根据自己的集群通信IP改动
port 6379 #自己的集群通信PORT
daemonize yes
pidfile "/var/run/redis.pid"
logfile "/usr/local/redis/cluster/redis.log"
dir "/usr/local/redis/cluster" # 数据存储目录
masterauth 123456
requirepass 123456
appendonly yes
cluster-enabled yes #开启集群模式
cluster-config-file nodes.conf #节点配置文件，cluster自动生成在数据存储目录
cluster-node-timeout 15000 #通信超时时间
```

3.启动redis服务(启动每一台)

```shell
chown -R redis:redis /usr/local/redis
/usr/local/bin/redis-server /usr/local/redis/cluster/redis.conf
```

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
redis-trib.rb create --replicas 1 192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 
```

5.创建集群

```shell
redis-cli -a 123456 --cluster create 192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 --cluster-replicas 1
```

输入yes，接受配置

会自动生成nodes.conf文件

6.登陆集群

```shell
redis-cli -c -h 192.168.1.1 -p 6379 -a 123456
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
CLUSTER MEET 192.168.1.7 6379
```

3.修改节点身份

```shell
redis-cli -c -h 192.168.1.8 -p 6379 -a 123456 cluster replicate $node_id
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

## 七、redis配置

```shell
# 1k => 1000 bytes
# 1kb => 1024 bytes
# 1m => 1000000 bytes
# 1mb => 1024*1024 bytes
# 1g => 1000000000 bytes
# 1gb => 1024*1024*1024 bytes

# loadmodule /path/to/my_module.so
#添加的模块

#include /path/to/other.conf
#追加的配置

tcp-backlog 511
#tcp连接越大越好

timeout 0
#连接超时时间↑

tcp-keepalive 300
#心跳检测，是否存活

##通常↓
bind 127.0.0.1 
绑定的IP地址

protected-mode yes
#设为no才能远程连接↑

port 6379

daemonize no
#改yes后台启动

pidfile /var/run/redis_6379.pid
#pid存放位置

loglevel notice
#日志等级debug|verbose|notice|warning

#logfile ""
#路径

##性能↓
databases 16
#默认库数量

maxclients 10000
#最大连接数

maxmemory 7,516,192,768
#最大内存↑（7G）

# replica-ignore-maxmemory yes
# 是否开启salve的最大内存

# volatile-lru -> Evict using approximated LRU, only keys with an expire set.
#LRU但仅超出过期时间↑
# allkeys-lru -> Evict any key using approximated LRU.
#类似LRU↑
# volatile-lfu -> Evict using approximated LFU, only keys with an expire set.
#lfu仅过期↑
# allkeys-lfu -> Evict any key using approximated LFU.
#flu↑
# volatile-random -> Remove a random key having an expire set.
#随机仅超出过期时间
# allkeys-random -> Remove a random key, any key.
#随机
# volatile-ttl -> Remove the key with the nearest expire time (minor TTL)
#ttl最小
# noeviction -> Don't evict anything, just return an error on write operations.
#不进行移除，当写操作时只返回error

# maxmemory-samples 5
#移除是抽样决定的，检查样本数越多，性能消耗越大一般设置小一点3-7

# maxmemory-eviction-tenacity 10
驱逐处理有效性，写入流量大的话需要增加

lazyfree-lazy-eviction no
#针对redis内存使用达到maxmeory，并设置有淘汰策略时,开启后内存可能超过maxmeory
lazyfree-lazy-expire no
#针对TTL此场景建议开启，因TTL本身是自适应调整的速度。
lazyfree-lazy-server-del no
#针对有些指令在处理已存在的键时，如rename命令，当目标键已存在,redis会先删除目标键，如果这些目标键是一个big key,那就会引入阻塞删除的性能问题。 此参数设置就是解决这类问题，建议可开启。
slave-lazy-flush no
#针对slave进行全量数据同步，slave在加载master的RDB文件前，会运行flushall来清理自己的数据场景，参数设置决定是否采用异常flush机制。如果内存变动不大，建议可开启。可减少全量同步耗时，从而减少主库因输出缓冲区爆涨引起的内存使用增长。

##安全↓
requirepass 123456
#密码

rename-command CONFIG b840fc02d524045429941cc15f59e41cb7be6c52
#危险命令改名

rename-command CONFIG ""
#禁止命令

#RDB持久化↓
#save ""
#不开启RDB↑
save 900 1
#900s有1个修改
save 300 10
#300s有10个修改
save 60 10000
#60s有1w个修改

stop-writes-on-bgsave-error yes
#当RDB持久化出现错误后，是否依然进行继续进行工作，yes：不能进行工作，no：可以继续进行工作

rdbcompression yes
#开启压缩

rdbchecksum yes
#开启校验，关闭提升性能

dir /usr/local/redis/var
#指定数据库目录

dbfilename dump.rdb
#指定数据库名称

##aof持久化↓
appendonly yes
#开启

appendfilename "appendonly.aof"
#文件名

appendfsync always
#always 每一次写入 | no 操作系统决定 | everysec 每秒

no-appendfsync-on-rewrite no
# 设置为yes表示rewrite期间对新写操作不fsync,暂时存在内存中,等rewrite完成后再写入，默认为no（数据更安全），建议yes（性能更好）

auto-aof-rewrite-percentage 100
#重写备份文件超过的百分比

auto-aof-rewrite-min-size 64mb
#重写的最小文件大小（比百分比更优先）

aof-load-truncated yes
#自动修复aof文件

aof-use-rdb-preamble yes
#开启混合持久化

##复制↓

replicaof 192.168.1.1 6379
#主机端口

masterauth 123456
#master密码

replica-serve-stale-data yes
#继续响应客户端请求

replica-read-only yes
#只读

repl-diskless-sync no
#是否使用socket复制 两种模式disk|socket在磁盘速度缓慢，网速快的情况下推荐用socket方式。

repl-diskless-sync-delay 5
#复制延迟时间，等待更多的从机连接，因为一旦开始复制，就不再接受复制请求

repl-ping-slave-period 10
#从机发送ping时间间隔，判断主机的状态

repl-timeout 60
#复制连接超时时间。

repl-disable-tcp-nodelay no
#是否禁止复制tcp链接的tcp nodelay参数，可传递yes或者no。默认是no，即使用tcp nodelay。如果master设置了yes来禁止tcp nodelay设置，在把数据复制给slave的时候，会减少包的数量和更小的网络带宽。但是这也可能带来数据的延迟。默认我们推荐更小的延迟，但是在数据量传输很大的场景下，建议选择yes

repl-backlog-size 1mb
#复制缓冲区大小，这是一个环形复制缓冲区，用来保存最新复制的命令。如果可以执行部分同步，只需要把缓冲区的部分数据复制给slave，就能恢复正常复制状态。

repl-backlog-ttl 3600
# master没有slave一段时间会释放复制缓冲区的内存，repl-backlog-ttl用来设置该时间长度。单位为秒。

replica-priority 100
# 当master不可用，Sentinel会根据slave的优先级选举一个master。最低的优先级的slave，当选master。而配置成0，永远不会被选举

min-replicas-to-write 3
#redis提供了可以让master停止写入的方式，如果配置了min-replicas-to-write，健康的slave的个数小于N，mater就禁止写入。设置为0不写入

min-replicas-max-lag 10
#延迟小于min-replicas-max-lag秒的slave才认为是健康的slave。设置为0禁用这个特性

##REDIS CLUSTER↓
cluster-enabled yes
#开启

cluster-config-file nodes-6379.conf
#配置文件

cluster-node-timeout 15000
#节点互联超时时间

cluster-replica-validity-factor 10
#比较slave断开连接的时间和(node-timeout * slave-validity-factor) + repl-ping-slave-period

cluster-migration-barrier 1
# master的slave数量大于该值，slave才能迁移到其他孤立master上，如这个参数若被设为2，那么只有当一个主节点拥有2 个可工作的从节点时，它的一个从节点会尝试迁移

cluster-require-full-coverage yes
#默认情况下，集群全部的slot有节点负责，集群状态才为ok，才能提供服务。设置为no，可以在slot没有全部分配的时候提供服务。不建议打开该配置，这样会造成分区的时候，小分区的master一直在接受写请求，而造成很长时间数据不一致

##慢查询日志
slowlog-log-slower-than 10000
#单位us 1000000=1s 0=强制记录 -1=禁用

slowlog-max-len 128
#慢查询日志长度

##延迟监控↓
latency-monitor-threshold 0
#0关闭监视、只记录大于等于设置的值的操作

##高级设置↓

hash-max-ziplist-entries 512
# 数据量小于等于hash-max-ziplist-entries的用ziplist，大于hash-max-ziplist-entries用hash

hash-max-ziplist-value 64
# value大小小于等于hash-max-ziplist-value的用ziplist，大于hash-max-ziplist-value用hash

list-max-ziplist-size -2
#-5:最大大小：64 KB<--不建议用于正常工作负载
#-4:最大大小：32 KB<--不推荐
#-3:最大大小：16 KB<--可能不推荐
#-2:最大大小：8kb<--良好
#-1:最大大小：4kb<--良好

list-compress-depth 0
#0:禁用所有列表压缩
#1：深度1表示“在列表中的1个节点之后才开始压缩，
#从头部或尾部
#所以：【head】->node->node->…->node->【tail】
#[头部]，[尾部]将始终未压缩；内部节点将压缩。
#2:[头部]->[下一步]->节点->节点->…->节点->[上一步]->[尾部]
#2这里的意思是：不要压缩头部或头部->下一个或尾部->上一个或尾部，
#但是压缩它们之间的所有节点。
#3:[头部]->[下一步]->[下一步]->节点->节点->…->节点->[上一步]->[上一步]->[尾部]

set-max-intset-entries 512
# 数据量小于等于set-max-intset-entries用iniset，大于set-max-intset-entries用set

zset-max-ziplist-entries 128
#数据量小于等于zset-max-ziplist-entries用ziplist，大于zset-max-ziplist-entries用zset

zset-max-ziplist-value 64
#value大小小于等于zset-max-ziplist-value用ziplist，大于zset-max-ziplist-value用zset

hll-sparse-max-bytes 3000
#value大小小于等于hll-sparse-max-bytes使用稀疏数据结构（sparse），大于hll-sparse-max-bytes使用稠密的数据结构（dense）。一个比16000大的value是几乎没用的，建议的value大概为3000。如果对CPU要求不高，对空间要求较高的,建议设置到10000左右

stream-node-max-bytes 4096
stream-node-max-entries 100
#宏观节点的最大流/项目的大小。在流数据结构是一个基数
#树节点编码在这项大的多。利用这个配置它是如何可能#大节点配置是单字节和
#最大项目数，这可能包含了在切换到新节点的时候
# appending新的流条目。如果任何以下设置来设置
# ignored极限是零，例如，操作系统，它有可能只是一集
#通过设置限制最大#纪录到最大字节0和最大输入到所需的值

activerehashing yes
#Redis将在每100毫秒时使用1毫秒的CPU时间来对redis的hash表进行重新hash，可以降低内存的使用。当你的使用场景中，有非常严格的实时性需要，不能够接受Redis时不时的对请求有2毫秒的延迟的话，把这项配置为no。如果没有这么严格的实时性要求，可以设置为yes，以便能够尽可能快的释放内存

client-output-buffer-limit normal 0 0 0
##对客户端输出缓冲进行限制可以强迫那些不从服务器读取数据的客户端断开连接，用来强制关闭传输缓慢的客户端。
#对于normal client，第一个0表示取消hard limit，第二个0和第三个0表示取消soft limit，normal client默认取消限制，因为如果没有寻问，他们是不会接收数据的

client-output-buffer-limit replica 256mb 64mb 60
#对于slave client和MONITER client，如果client-output-buffer一旦超过256mb，又或者超过64mb持续60秒，那么服务器就会立即断开客户端连接

client-output-buffer-limit pubsub 32mb 8mb 60
#对于pubsub client，如果client-output-buffer一旦超过32mb，又或者超过8mb持续60秒，那么服务器就会立即断开客户端连接

client-query-buffer-limit 1gb
# 这是客户端查询的缓存极限值大小

proto-max-bulk-len 512mb
#在redis协议中，批量请求，即表示单个字符串，通常限制为512 MB。但是您可以更改此限制。

hz 10
#redis执行任务的频率为1s除以hz

dynamic-hz yes
#当启用动态赫兹时，实际配置的赫兹将用作作为基线，但实际配置的赫兹值的倍数
#在连接更多客户端后根据需要使用。这样一个闲置的实例将占用很少的CPU时间，而繁忙的实例将反应更灵敏

aof-rewrite-incremental-fsync yes
#在aof重写的时候，如果打开了aof-rewrite-incremental-fsync开关，系统会每32MB执行一次fsync。这对于把文件写入磁盘是有帮助的，可以避免过大的延迟峰值

rdb-save-incremental-fsync yes
#在rdb保存的时候，如果打开了rdb-save-incremental-fsync开关，系统会每32MB执行一次fsync。这对于把文件写入磁盘是有帮助的，可以避免过大的延迟峰值

##碎片整理↓

activedefrag yes
#开启

active-defrag-ignore-bytes 100mb
# 启动活动碎片整理的最小碎片浪费量

active-defrag-threshold-lower 10
# 启动活动碎片整理的最小碎片百分比

active-defrag-threshold-upper 100
# 我们使用最大努力的最大碎片百分比

active-defrag-cycle-min 5
# 以CPU百分比表示的碎片整理的最小工作量

active-defrag-cycle-max 75
# 在CPU的百分比最大的努力和碎片整理

active-defrag-max-scan-fields 1000
#将从中处理的set/hash/zset/list字段的最大数目
```

## 八、常用数据类型操作

### redis操作

| redis通用       | 功能                      |
| ------------- | ----------------------- |
| keys *        | 查看所有key                 |
| exists key    | 判断key是否存在               |
| type key      | 查看key的类型                |
| del key       | 删除（会阻塞）                 |
| UNLINK key    | 异步删除（性能好点）              |
| expire key 10 | 设置过期10秒                 |
| ttl key       | 查看剩余过期时间 -1 永不过期 -2 已过期 |
| select 11     | 切换数据库0-15               |
| dbsize        | 查看当前库的key数量             |
| flushdb       | 清空当前库                   |
| flushall      | 通杀全部库                   |

## string  key: value 字符

| string                                                    | 功能               |
| --------------------------------------------------------- | ---------------- |
| set key_name value1                                       | 设置值              |
| get key_name                                              | 获取值              |
| append key_name value2                                    | 追加值              |
| strlen key_name                                           | 获取值的长度           |
| setnx key_name value3                                     | 当key不存在是设置值      |
| incr key_name                                             | 数值型+1            |
| decr key_name                                             | 数值型-1            |
| incrby key_name 6                                         | 数值型＋6            |
| decrby key_name 7                                         | 数值型-7            |
| mset key_name1 value1 key_name2 value2 key_name3 value3   | 设置多个键值           |
| mget key_name1 key_name2                                  | 获取多个键值           |
| msetnx key_name1 value1 key_name2 value2 key_name3 value3 | 原子性都成功才行         |
| getrange key_name1 0-3                                    | 显示前4个字符          |
| setrange key_name1 2 value2                               | 从第三（2+1）个字符开始覆写值 |
| setex key_name1 20 value1                                 | 设置键值同时设定过期时间     |
| getset key_name1 value1                                   | 旧值换新值            |

### list  列表

| list                                       | 功能                      |
| ------------------------------------------ | ----------------------- |
| lpush/rpush key_name1 value1 value2 value3 | 从左/右插入1个或多个值            |
| lpop/rpop key_name1                        | 从左/右取出一个值               |
| rpoplpush key_name1                        | key_name2 键1右→键2左       |
| lrange key_name1 0 3                       | 从左到右读键第一个到第四个的值 0 -1指全部 |
| lindex key_name1 2                         | 从左到右读键第三（2+1）个的值        |
| llen key_name1                             | 获取长度                    |
| linsert key_name1 before value1 value2     | 从左到右在值1前面插入value2       |
| lrem key_name1 4 value3                    | 从左起删除键1中的4个值为value3     |
| lset key_name1 0 value4                    | 从左起将key下标为0的值替换为value4  |

### set  集合（不重复的列表）

| set                                       | 功能                     |
| ----------------------------------------- | ---------------------- |
| sadd key_name1 value1 value2 value3       | 添加元素进键1 不可重复           |
| smembers key_name1                        | 取出所有值                  |
| sismember key_name1 value1                | 判断键1是否有value1，有1，没有0   |
| scard key_name1                           | 返回元素个数                 |
| srem key_name1 value1 value2 value3       | 删除value1 value2 value3 |
| spop key_name1                            | 随机取出一个值                |
| srandmember key_name1 n                   | 随机取出N个值，不会删除           |
| smove key_name1 key_name2  value1 把value1 | 从键1移动到键2               |
| sunion key_name1 key_name2                | 返回并集元素                 |
| sinter key_name1 key_name2                | 返回交集元素                 |
| sdiff key_name1 key_name2                 | 返回差集元素key1有key2无的      |

### zset  带评分的集合

| zset                                       | 功能                |
| ------------------------------------------ | ----------------- |
| zadd key_name2  1 go 2 java 3 c++ 4 python | 给值加上评分，排序输出       |
| zrange key_name2 0 -1                      | 显示从0开始排序的value    |
| zrangebyscore key_name2 5 7 withscores     | 从小到大排序显示5-7 并显示分数 |
| zrevrangebyscore key_name2 7 5 withscores  | 从大到小排序显示5-7 并显示分数 |
| zincrby key_name2 3 java                   | Java的分数加3         |
| zrem  key_name2 java                       | 删除指定值             |
| zcount  key_name2 5 7                      | 统计分数5-7之间有几个值     |
| zrank key_name2 java                       | 返回java的分数排名       |

### hash   键值对集合

| hash                                                  | 功能                                    |
| ----------------------------------------------------- | ------------------------------------- |
| hset key_name1 field1 value1                          | 给键1中的字段1赋值value1                      |
| hget key_name1 field1                                 | 获取取键1 中的字段1                           |
| hmset key_name1 field1 value1 key_name2 field2 value2 | 批量设置                                  |
| hexists key_name1 field1                              | 判断key_name1 中的field1 是否存在             |
| hkeys key_name1                                       | 列出键1 中所有field                         |
| hvals key_name1                                       | 列出所有value                             |
| hincrby key_name1 field2  -2                          | 键1字段2增加-2（数值型）                        |
| hsetnx key_name1 field3 value3                        | 当key_name1.field3不存在时给键1中的字段3赋值value3 |

## 九、Redis应用问题解决

### 缓存穿透

key对应的数据在数据源并不存在，每次针对此key的请求从缓存获取不到，请求都会压到数据源，从而可能压垮数据源。比如用一个不存在的用户id获取用户信息，不论缓存还是数据库都没有，若黑客利用此漏洞进行攻击可能压垮数据库

#### 解决方案

1.对空值缓存

如果一个查询返回的数据为空（不管是数据是否不存在），我们仍然把这个空结果（null）进行缓存，设置空结果的过期时间会很短，最长不超过五分钟

2.设置可访问的名单（白名单）

使用bitmaps类型定义一个可以访问的名单，名单id作为bitmaps的偏移量，每次访问和bitmap里面的id进行比较，如果访问id不在bitmaps里面，进行拦截，不允许访问。

3.采用布隆过滤器

(布隆过滤器（Bloom Filter）是1970年由布隆提出的。它实际上是一个很长的二进制向量(位图)和一系列随机映射函数（哈希函数）。

布隆过滤器可以用于检索一个元素是否在一个集合中。它的优点是空间效率和查询时间都远远超过一般的算法，缺点是有一定的误识别率和删除困难。)

将所有可能存在的数据哈希到一个足够大的bitmaps中，一个一定不存在的数据会被 这个bitmaps拦截掉，从而避免了对底层存储系统的查询压力。

4.进行实时监控

当发现Redis的命中率开始急速降低，需要排查访问对象和访问的数据，和运维人员配合，可以设置黑名单限制服务

### 缓存击穿

key对应的数据存在，但在redis中过期，此时若有大量并发请求过来，这些请求发现缓存过期一般都会从后端DB加载数据并回设到缓存，这个时候大并发的请求可能会瞬间把后端DB压垮。

#### 解决方案

1.预先设置热门数据：在redis高峰访问之前，把一些热门数据提前存入到redis里面，加大这些热门数据key的时长

2.实时调整：现场监控哪些数据热门，实时调整key的过期时长

3.使用锁

3.1就是在缓存失效的时候（判断拿出来的值为空），不是立即去load db。

3.2先使用缓存工具的某些带成功操作返回值的操作（比如Redis的SETNX）去set一个mutex key

3.3当操作返回成功时，再进行load db的操作，并回设缓存,最后删除mutex key；

3.4当操作返回失败，证明有线程在load db，当前线程睡眠一段时间再重试整个get缓存的方法。

### 缓存雪崩

key对应的数据存在，但在redis中过期，此时若有大量并发请求过来，这些请求发现缓存过期一般都会从后端DB加载数据并回设到缓存，这个时候大并发的请求可能会瞬间把后端DB压垮。

缓存雪崩与缓存击穿的区别在于这里针对很多key缓存，前者则是某一个key

#### 解决方案

1.构建多级缓存架构：nginx缓存 + redis缓存 +其他缓存（ehcache等）

2.使用锁或队列：

用加锁或者队列的方式保证来保证不会有大量的线程对数据库一次性进行读写，从而避免失效时大量的并发请求落到底层存储系统上。不适用高并发情况

3.设置过期标志更新缓存：

记录缓存数据是否过期（设置提前量），如果过期会触发通知另外的线程在后台去更新实际key的缓存。

4.将缓存失效时间分散开：

比如我们可以在原有的失效时间基础上增加一个随机值，比如1-5分钟随机，这样每一个缓存的过期时间的重复率就会降低，就很难引发集体失效的事件。


