# Mysql

## 一、安装

### centos:

```shell
#!/bin/bash
yum install libncurses* -y
rm -rf /etc/my.cnf
`id mysql` &>>/dev/null
if [ $? -ne 0 ];then
   useradd -r -s /sbin/nologin -M mysql
fi
mkdir -p /mysqld/data
chown -R mysql:mysql /mysqld
cd /usr/local
tar -zxvf mysql-5.7.35-linux-glibc2.12-x86_64.tar.gz
ln -s mysql-5.7.35-linux-glibc2.12-x86_64 mysql
cd mysql
mkdir mysql-files
chown mysql:mysql mysql-files
chmod 750 mysql-files
bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql --datadir=/mysqld/data
bin/mysql_ssl_rsa_setup --datadir=/mysqld/data
cp support-files/mysql.server /etc/init.d/mysqld.server
sed -i "47s#datadir=#datadir=/mysqld/data#g" /etc/init.d/mysqld.server
echo "[mysqld]
basedir=/usr/local/mysql
datadir=/mysqld/data
port=3306
socket=/tmp/mysql.sock
character_set_server=utf8mb4
collation-server=utf8mb4_general_ci
transaction_isolation=READ-COMMITTED
server-id=10
log-bin=/mysqld/data/binlog
binlog-format=row
user=mysql
[client]
port=3306
socket=/tmp/mysql.sock" >> /usr/local/mysql/my.cnf
chkconfig --add mysqld.server
echo 'export PATH="$PATH:/usr/local/mysql/bin"' >> /etc/profile
source /etc/profile
service mysqld.server start
#data下frm为表结构定义文件
#可以使用mysql Utilities查看 mysqlfrm --diagnostic --server=root:123456@localhost *.frm
#可以添加skip-engine_name来跳过引擎启动
```

### ubuntu:

```shell
#!/bin/bash
# 下载mysql
wget https://cdn.mysql.com//Downloads/MySQL-8.0/mysql-8.0.29-linux-glibc2.12-x86_64.tar.xz -O /usr/local/mysql-8.0.29-linux-glibc2.12-x86_64.tar.xz
apt-get install libaio1
# 安装环境配置
rm -rf /etc/my.cnf
`id mysql` &>>/dev/null
if [ $? -ne 0 ];then
   useradd -r -s /sbin/nologin -M mysql
fi
mkdir -p /mysqld/data
chown -R mysql:mysql /mysqld
cd /usr/local
tar -xvf /usr/local/mysql-8.0.29-linux-glibc2.12-x86_64.tar.xz
ln -s mysql-8.0.29-linux-glibc2.12-x86_64 mysql
cd mysql
mkdir mysql-files
chown mysql:mysql mysql-files
chmod 750 mysql-files
# 初始化安装
bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql --datadir=/mysqld/data >> /root/mysql-init.log
bin/mysql_ssl_rsa_setup --datadir=/mysqld/data
# 配置数据库
echo "[mysqld]
basedir=/usr/local/mysql
datadir=/mysqld/data
port=3306
socket=/tmp/mysql.sock
character_set_server=utf8mb4
collation-server=utf8mb4_general_ci
server-id=10
log-bin=/mysqld/data/binlog
[client]
port=3306
socket=/tmp/mysql.sock" >> /usr/local/mysql/my.cnf
# 服务添加mysql
cp support-files/mysql.server /etc/init.d/mysqld.server
sed -i "47s#datadir=#datadir=/mysqld/data#g" /etc/init.d/mysqld.server
chmod +x /etc/init.d/mysqld.server
systemctl daemon-reload
# 添加路径
echo 'export PATH="$PATH:/usr/local/mysql/bin"' >> /etc/profile
ln -s /lib/x86_64-linux-gnu/libtinfo.so.6.2 /lib/x86_64-linux-gnu/libtinfo.so.5
source /etc/profile
# 开机自启动
update-rc.d -f mysqld.server defaults
service mysqld.server start
```

### 多实例:

1.在my.cnf中添加

```my.cnf
[mysqld_multi]
mysqld=/usr/local/mysql/bin/mysqld_safe
mysqladmin=/usr/local/mysql/bin/mysqladmin
log=/usr/local/mysql/mysqld_multi.log
[mysqld1]
basedir=/usr/local/mysql
port=3307
datadir=/mysql_3307/data
socket=/tmp/mysql_3307.sock
log-error=/mysqld_3307/data/error.log
innodb_buffer_pool_size = 32M
```

2.

```shell
mkdir -p /mysql_3307/data && chown -R mysql:mysql /mysql_3307
```

3.

```shell
mysqld --initialize-insecure --datadir=/mysql_3307/data --user=mysql#初始化
```

4.

```shell
mysqld_multi start 1 #启动mysqld1
```

5.

```shell
mysqld_multi report #查看多实例状态
```

#[mysql1]没定义的会继承[mysqld]

6.

```my.cnf
[mysqld_multi]
user=username
pass=password
```

有密码才能通过mysqld——multi命令管理实例

## 二、my.cnf配置参数

```my.cnf
[mysqld]
basedir=/usr/local/mysql
datadir=/mysqld/data
port=3306
socket=/tmp/mysql.sock
character_set_server=utf8mb4
collation-server=utf8mb4_general_ci
server-id=10
log-bin=/mysqld/data/binlog
[client]
port=3306
socket=/tmp/mysql.sock
```

## 三、INNODB

### INNODB存储引擎特性

**doublewrite**
    保证数据写入可靠性，共享表空间一份数据，数据文件一份数据，可以保证一定能有一份free page能redo
**insert/change buffer**
    先判断插入的非聚集索引页是否在缓冲池中，若在，则直接插入，若不在则放入到一个INSERT BUFFER对象中，当读取到辅助索引叶到缓冲池，将INSERT BUFFER中该页的记录合并到辅助索引页
**adaptive hash index**
    自适应hash索引

```my.cnf
innodb_adaptive_hash_index=off  #最好不要用
innodb_adaptive_hash_index_parts=8
```

**flush neighbor page**

​    刷脏页

```my.cnf
innodb_flush_neighbors=0   
```

5.6版本SSD要设置为0 
设置为0时，表示刷脏页时不刷其附近的脏页。
设置为1时，表示刷脏页时连带其附近毗连的脏页一起刷掉。
设置为2时，表示刷脏页时连带其附近区域的脏页一起刷掉。1与2的区别是2刷的区域更大一些。

### INNODB存储引擎缓冲池

**innodb_buffer_pool_size**
建议（60%-80%）
通过space（表空间ID和page_no叶的编号定位）

```mysql
# 查看space的ID
SELECT name,space FROM INNODB_SYS_TABLESPACES;
# 查看page_no
SELECT space,page_number,page_type from INNODB_BUFFER_PAGE \G
```

**buffer pool|指针**
    free list:指向未使用的叶
    LRU List:已使用的叶+flush list
    *最近最少使用算法（读到的数据放在最前）和midpoint LRU算法（读到的数据放在前3/8），midpoint LRU算法用来避免扫描语句污染LRU
    flush list:包含指向已使用已修改的叶的指针
    *free list和flush list都只是指针，只是指向的对象是对立的

```my.cnf
innodb_old_blocks_pct=n
# 默认37，设置为100则为普通LRU

innodb_old_blocks_time=1000
# 单位毫秒，老生代停留时间窗口，即同时满足“被访问”与“在老生代停留时间超过1秒”两个条件，才会被插入到新生代头部。

# innodb_buffer_pool_instances=N要设置为CPU核心数
内存总大小innodb_buffer_pool_size不变，innodb_buffer_pool被拆分为N个，效率提升
```

##缓存热点数据|持久化

```my.cnf
innodb_buffer_pool_dump_at_shutdown    #关闭时持久化
innodb_buffer_pool_dump_now     #现在就持久化
innodb_buffer_pool_dump_pct=n     #加载数据pct决定备份前N%
innodb_buffer_pool_load_at_startup    #开机时载入
innodb_buffer_pool_load_now      #现在载入buffer_pool持久化，备份的是SPACE和page_no，需要时再从磁盘加载数据pct决定备份前N%的数据,可以设置在MY.CNF也可以SET GLOBAL VARIABLES_NAME=''
```

### INNODB线程

**查询方式**

```mysql
use performance_schema
select * from threads where  name like 'thread/innodb%' ；  #可以查看thread的os ID
```

thread/innodb/io_read_thread   #读的线程数
thread/innodb/io_write_thread  #写入的线程数
innodb_write_io_threads=16  
thread/innodb/page_cleaner_thread  #刷新进磁盘的线程默认为4

```mysql
show variables like 'innodb_io_%'
# innodb_io_capacity:每秒钟刷新脏页数量
```

**线程池|thread pool**

保证高并发下的性能平稳
Thread Pool由一个Timer线程和多个Thread Group组成，而每个Thread Group又由两个队列、一个listener线程和多个worker线程构成。

```my.cnf
参数说明
thread_handling=pool-of-threads  #默认情况是one-thread-per-connection，即不启用线程池
thread_pool_size=32   #CPU
thread_pool_oversubscribe=3  #该参数设置group中的最大线程数，每个group的最大线程数为ithread_pool_oversubscribe+1，注意listener线程不包含在内。
extra_port =3333 #额外端口
thread_pool_high_prio_mode=transactions #transactions对于已经启动事务的语句放到高优先级队列中，statements这个模式所有的语句都会放到高优先级队列中，不会使用到低优先级队列。none：这个模式不使用高优先级队列。
thread_pool_idle_timeout  #worker线程最大空闲时间，默认为60秒，超过限制后会退出。
thread_pool_max_threads  #该参数用来限制线程池最大的线程数，超过该限制后将无法再创建更多的线程，默认为100000。
thread_pool_stall_limit    #该参数设置timer线程的检测group是否异常的时间间隔，默认为500ms。
```

启用线程池后，内存泄漏问题
是percona的bug，需要performance_schema=off，然后重启MySQL就OK。

拨测异常问题
1。启用MySQL的旁路管理端口，监控和高可用相关直接使用MySQL的旁路管理端口。
2.修改高可用探测脚本，将达到线程池最大活动线程数返回的错误做异常处理，当作超过最大连接数的场景。

**回收线程|Purge Thread**

```my.cnf
innodb_purge_threads=4   # 设置回收线程数
```



### DATA的存储方式

查询:

```mysql
show variables like 'innodb%row%';
```

REDUDENT:老版本，已经不用了
COMPACT:默认，存不下时使用行溢出叶
COMPRESSED:压缩
DYNAMIC:通常等于COMPACT,大对象时只存指针，指针指向大对象的行溢出叶
*是否使用行溢出叶的判断标准是单行记录大小>page/2

数据的块存储|PAGE的大小
类似文件系统 以16K为一单位存放数据，不满16K的数据也要占16K

压缩能提升性能，节省IO，但是CPU负载会变高
叶到buffer pool只需要一次解压，更新操作时会解压数据写一份，压缩数据写日志，压缩日志写不下时，解压数据才进行压缩，写回磁盘

## 四、redo log

物理格式的日志，记录的是物理数据页面的修改的信息，其的物理文件中去的。
确保事务的持久性。防止在发生故障的时间点，尚有脏页未写入磁盘，在重启mysql服务的时候，根据redo log进行重做，从而达到事务的持久性这一特性。
事务开始之后就产生redo log，当对应事务的脏页写入到磁盘之后被覆盖

### redo log buffer

redo log buffer刷新条件
1.master thread 每秒进行刷新
2.redo log buffer 使用大于1/2进行刷新
3.事务提交时（如果下面innodb_flush_log_at_trx_commit值为1）

```my.cnf
innodb_log_buffer_size # 通常8M够用
innodb_flush_log_at_trx_commit={0|1|2}
```

### redo log file

```my.cnf
innodb_log_file_size
# 重做日志文件的大小。

innodb_log_files_in_group  
# 指定重做日志文件组中文件的数量，默认2，对应的物理文件位于数据库的data目录下ib_logfile1&ib_logfile2

innodb_log_group_home_dir 
#指定日志文件组所在的路径，默认./ ，表示在数据库的数据目录下。可以和数据文件分开,选择更快的磁盘

innodb_mirrored_log_groups 指定了日志镜像文件组的数量，默认1
```



### 刷新脏页

缩短数据库恢复时间
缓冲池不够用时把脏页刷进磁盘

innodb fuzzy checkpoint可能发生的几种情况：

master thread checkpoint           主线程一定的间隔条件触发检查点
flush_lru_list checkpoint             LRU列表替换出的脏页触发检查点（缓冲区将溢出）
async flush checkpoint               重做日志不可用，强制执行检查点
dirty page too much checkpoint  太多的脏页触发检查点

```my.cnf
innodb_max_dirty_pages_pct参数控制
```

**查看checkpoint**
show engine innodb status\G
Log sequence number：代表系统中的lsn值，也就是当前系统已经写入的redo日志量，包括写入log buffer中的日志。
Log flushed up to：代表flushed_to_disk_lsn的值，也就是当前系统已经写入磁盘的redo日志量。
Pages flushed up to：代表flush链表中被最早修改的那个页面对应的oldest_modification属性值。
Last checkpoint at：当前系统的checkpoint_lsn值。

出现LSN>CHECKPOINT的情况
默认差9

出现bufferLSN>diskLSN的情况
buffer pool特性决定flush_list只记录第一次的LSN（保证数据一致性）

```my.cnf
Innodb_force_recovery=0  ：自动恢复
```

Innodb_force_recovery可以设置6个非零值：
1(SRV_FORCE_IGNORE_CORRUPT):忽略检查到的corrupt页。
2(SRV_FORCE_NO_BACKGROUND):阻止主线程的运行，如主线程需要执行full purge操作，会导致crash。
3(SRV_FORCE_NO_TRX_UNDO):不执行事务回滚操作。
4(SRV_FORCE_NO_IBUF_MERGE):不执行插入缓冲的合并操作。
5(SRV_FORCE_NO_UNDO_LOG_SCAN):不查看重做日志，InnoDB存储引擎会将未提交的事务视为已提交。
6(SRV_FORCE_NO_LOG_REDO):不执行前滚的操作。

### redo于binlog区别

仅INNODB  |  MYSQL全局
物理逻辑日志（基于叶DIFF） |  逻辑日志（基于SQL）
写入的时间点REDO有开始时间和提交时间  |  BINLOG只有最后提交时间

## 五、undo log

保存了事务发生之前的数据的一个版本，可以用于回滚

将数据从逻辑上恢复至事务之前的状态（非物理层面）

事务开始之前产生，事物完成后不会立刻删除，而是放入待清理的链表，由purge线程判断是否由其他事务在使用undo段中表的上一个事务之前的版本信息，决定是否可以清理undo log的日志空间。

mvcc多版本并发控制靠undo实现，读正在更新（尚未commit）的操作，读的是之前的版本（undo版本）
相关变量

```my.cnf
innodb_undo_directory = /data/undospace/ –undo独立表空间的存放目录,通常放在.ibd文件中，如果关闭独立表空间，则放在共享表空间ibdata1
innodb_undo_logs = 128 # 回滚段为128KB
innodb_undo_tablespaces = 4 # 指定有4个undo log文件
```



## 六、事务

### TRANSACTION特性

ATOMICITY|原子性
	要么完整执行，要么不执行
CONSISTENCY|一致性
	底层数据存储的完整性
ISOLATION|隔离性
	独立执行，不干扰其他进程和事务
DURABILITY|持久性
	所有改动都必须在成功结束前保存至某个物理设备

```mysql
begin;  #开启事务
rollback;  #回滚事务到begin
savepoint  s1;   #设置回滚保存点
rollback to s1;     #回滚到s1
commit;   #提交
```

commit分为3步
1.innodb prepare redo log （fsync）
2.write binlog （fsync）
3.innodb commit redo log (fsync)

中途故障停机了，事务commit的处理方式？
1.scan binlog生成txid list 转化为hashtable
2.scan innodb生成txidlist搜索hashtable存在则commit，不存在rollback

MySQL是自动提交，不输入BEGIN的话，执行完语句自动提交

```mysql
SHOW VARIABLES LIKE 'AUTOCOMMIT'  #查看自动提交
```

查看事务的隔离级别|isolation

```mysql
SHOW VARIABLES LIKE 'tx_isolation';
select * from performance_schema.variables_by_thread where variable_name='tx_isolation';
```

read-uncommitted：事务中的修改，即使没有提交，其他事务也可以看得到，会导致“脏读”、“幻读”和“不可重复读取”。
read-committed：大多数主流数据库的默认事务等级，保证了一个事务不会读到另一个并行事务已修改但未提交的数据，避免了“脏读取”，但不能避免“幻读”和“不可重复读取”。该级别适用于大多数系统。
repeatable-read：保证了一个事务不会修改已经由另一个事务读取但未提交（回滚）的数据。避免了“脏读取”和“不可重复读取”的情况，但不能避免“幻读”，但是带来了更多的性能损失。
serializable

RR强于RC怎么测试

```mysql
BEGIN;
SELECT * FROM T1;  重复10次
COMMIT;
```

因为READVIEW的原因
RC隔离级别：每次读取数据前，都生成一个readview；
RR隔离级别：在第一次读取数据前，生成一个readview；

但MYSQL最好还是RC，综合来看，RR更容易出现死锁

### ReadView 机制

当事务在开始执行的时候，会给每个事务生成一个 ReadView。这个 ReadView 会记录 4 个非常重要的属性：

creator_trx_id: 当前事务的 id;
m_ids: 当前系统中所有的活跃事务的 id，活跃事务指的是当前系统中开启了事务，但是还没有提交的事务;
min_trx_id: 当前系统中，所有活跃事务中事务 id 最小的那个事务，也就是 m_id 数组中最小的事务 id;
max_trx_id: 当前系统中事务的 id 值最大的那个事务 id 值再加 1，也就是系统中下一个要生成的事务 id。
ReadView 会根据这 4 个属性，再结合 undo log 版本链，来实现 MVCC 机制，决定让一个事务能读取到哪些数据，不能读取到哪些数据。
*MVCC两个条件undo和readview,RC只读1个版本，RR可能会回滚多个版本

## 七、bin log

### binlog配置解析

```my.cnf
log-bin=/binlog/mysqld-bin   #日志的路径及名字
binlog-format=row   #日志格式STATEMENT、ROW、MIXED
log-expire-day=7   #binlog失效天数
binlog_rows_query_log_events=1   #会记录对应的SQL语句
sync_binlog=1    #事务提交时，保证2进制文件一定落盘
max_binlog_size=2048M   #binlog大小
transaction-isolation=READ-COMMITTED
binlog_cache_size=32K    #默认就行，一般够用
innodb_flush_log_at_trx_commit=1  #确保数据落盘
innodb_support_xa=1   #支持xa两段式事务提交。
relay_log_recovery=1    #将sql线程的位置初始化到新的relay log
relay_log_info_repository=TABLE   #改写磁盘为写表，把event操作都放在一个事务里，保证事务一致性
log_slave_updates    #从机可以中继（相当于开启binlog）
slave_parallel_workers=8   #从机复制的线程数
slave_parallel_type=logical_clock   #逻辑回放，主机怎么做从机就怎么做
gtid_mode=on     #开启gtid
log_slave_updates=1    #从机中继日志升级为BINlog
enforce-gtid-consistency=1   #强制GTID一致性检查
```

为什么relay_log_recovery=1和relay_log_info_repository=TABLE可以保证一致性？
	因为relay_log_recovery=1将sql线程的位置初始化到新的relay log，而旧的relaylog则删除，因为不可信了，保证不会错过event
	sync_relay_log_info=10000；代表每次执行10000个event才刷一次磁盘，故障恢复时，没有savepoint就会重做一部分event，这样数据就错误了
	relay_log_info_repository=TABLE把event操作都放在一个事务里，要做就都做，不然就回滚，同时relay_log_info_repository=TABLE决定了事务存放于临时表，不写磁盘了加强了一致性


### mysqlbinlog|查看二进制日志

```mysql
show binary logs;
show binlog events in 'binlog_logfile';
```

ROW:

```shell
mysqlbinlog --base64-output=DECODE-ROWS -vv --start-datetime='2022-01-11 00:00:00' --stop-datetime='2022-01-12 15:00:00' file
```



statement:

```shell
mysqlbinlog  --start-datetime='2022-04-11 00:00:00' --stop-datetime='2022-04-11 15:00:00' file
```



-d, --database=name      #仅显示指定数据库的转储内容。
-o, --offset=    #跳过前N行的日志条目
-r, --result-file=name   #将输入的文本格式的文件转储到指定的文件。
-s, --short-form        # 使用简单格式。
--set-charset=name       #在转储文件的开头增加'SET NAMES character_set'语句。
--start-datetime=name    #转储日志的起始时间。
--stop-datetime=name     #转储日志的截止时间。
-j, --start-position=4	    #转储日志的起始位置。要正确的位置
--stop-position=609         #转储日志的截止位置，不包括at609。要正确的位置。
-v ,--verbose    #详细模式
--base64-output=       #binlog记录的是base64格式的数据,mysqlbinlog可以使用此参数改变输出格式可以设置'NEVER','AUTO','UNSPEC','DECODE-ROWS'

怎么查看从机SQL线程执行数量

```mysql
show processlist;
select * from information_schema.processlist where user='system user' and 'System lock';
```

刷新二进制日志

```mysql
flush logs;
```

### 通过binlog恢复某时刻数据

一、
1.找到正确的start-position和stop-position（数据库的状态在START-POSITION处）
2.mysqlbinlog --no-defaults --start-position=713 --stop-position=1646|mysql -p

二、
1.show binlog events in 'binlog.000001';    #找到对应的start-position和stop-position(误操作事件的)，例如3309和3401
2.安装flashback工具
3.mysqlbinlog -vv binlog.000001 --start-position=3309 和stop-position=3401 -B  #查看是否已转换，例如：insert<>delete,update的data前后对调
4.mysqlbinlog -vv binlog.000001 --start-position=3309 stop-position=3401 -B|mysql -p    #确认以后执行flashback

### 删除binglog

```mysql
purge binary logs to 'mysql-bin.000017';
```

查看有问题的进程

```mysql
SHOW PROCESSLIST;
```

处于SLEEP而且时间很长的，可能就是有问题的

事务的组提交
可以提升性能, 但尽量不要设置，调优很难

```
binlog_group_commit_sync_delay=n  #等待多少毫秒提交一次
binlog_group_commit_sync_no_delay_count  #等待多少条提交一次
```

分布式事务

```mysql
set @id:=floor(rand()*1000000+1)
xa start 'name';
update sbtest.sbtest1 set k=k+1 where id = @id;
xa end 'name';
xa prepare 'name';
xa commit 'name';
```

## 八、锁

对共享资源进行并发访问
提供数据的完整性和一致性

### LOCK与LATCH区别

|          | LOCK                                                  | LATCH                                                        |
| -------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| 保护     | 锁的是记录                                            | 锁的是内存中并发资源的对象（临界区）                         |
| 对象     | 事务                                                  | 线程                                                         |
| 持续时间 | 整个事务过程                                          | 临界资源                                                     |
| 模式     | 行锁、表锁、意向锁                                    | 读写锁、互斥锁                                               |
| 死锁     | 通过waits-for graph、time out等机制进行死锁检测与处理 | 无死锁检测与处理机制。仅通过应用程序加锁的顺序（latch leveling）保证无死锁的情况发生 |
| 存在于   | lock manager的哈希表中                                | 每个数据结构的对象中                                         |



### LOCK类型

S 行级共享锁：允许其他事务添加共享锁，不允许其他事务加排他锁（能读（无锁，或lock in share mode），写要等待上一个事务COMMIT）
X 行级排它锁：不允许加锁(能读（仅不加锁的情况），不能写)

|      | s    | x    |
| ---- | ---- | ---- |
| s    | ✔    | ❌    |
| x    | ❌    | ❌    |

插入意向锁|insertion intention lock
	一种Gap锁，用于判断是否能插入这条记录
	因为是意向锁，所以和S、X相斥
	因为是意向锁所以兼容其他意向锁，达到提高插入效率

​	IS：意向锁，这层不加锁，下层再说  与锁不兼容
​	IX：意向锁，这层不加锁，下层再说  与锁不兼容

|      | is   | ix   |
| ---- | ---- | ---- |
| is   | ✔    | ✔    |
| ix   | ✔    | ✔    |



数据库是一层层加锁的
例如
					数据库
table1	table2	table3	table4	IX
PAGE	PAGE	PAGE	PAGE	IX
ROW	ROW	ROW	ROW	X
意向锁是表锁加在表上

AI 自增锁:控制auto_increment，事务提交之前释放（其他事务也可以使用该锁自增，只要前一条自增语句完成）
innodb_autoinc_lock_mode可以设置自增锁的模式
0：traditonal （每次都会产生表锁）
1：consecutive （会产生一个轻量锁，simple insert会获得批量的锁，保证连续插入）
2：interleaved （不会锁表，来一个处理一个，并发最高）

元数据锁|Metadata Lock |MDL
元数据锁主要是面向DML和DDL之间的并发控制，如果对一张表做DML增删改查操作的同时，有一个线程在做DDL操作，不加控制的话，就会出现错误和异常。元数据锁不需要我们显式的加，系统默认会加。

元数据锁的原理
当做DML操作时，会申请一个MDL读锁
当做DDL操作时，会申请一个MDL写锁
读锁之间不互斥，读写和写写之间都互斥。

### 锁的算法

1.RECORD LOCK|单个行记录上的锁
2.GAP LOCK|锁定一个范围，但不包含记录本身（间隙锁）
3.NEXT-KEY LOCK|锁定一个范围加记录本身
以上是锁索引
RR级别会使用NEXT-KEY LOCK，影响性能
算法是为了配合S/X解决幻读问题

例如
row	a	b	c	d
1	2	4	10	11
2	3	6	20	13
3	4	8	30	15
PK=a	KEY=b	unique key=d

1.为什么  NEXT-KEY LOCK
锁b=6时会锁（4,6](6,8)?
因为此时不锁（4,6](6,8)如果插入一条a=5,b=6时，此纪录会插入到第三行（对于索引b而言第三），为了避免这种情况发生会锁这个范围

2.为什么NEXT-KEY LOCK
锁b=6时，插入a=1，b=4成功了，而a=5,b=4却不成功？
因为key（b）实际上是key（b，primarykey）包含主键值实际的区间范围是（（4，2），（6，3）】和（（6，3），（8，4））
a=1，b=4相当于4,1排在4，2之前，不在区间内
而a=5,b=4相当于4，5在4，2后面

3.如果此时对b=10 for update(b=10不存在)？
会（8，正无穷）加锁
b>=8的数据无法插入

4.RC下SELECT * FROM ROW WHERE c=20 for update;
此时仅第二行记录加锁

5.RR下SELECT * FROM ROW WHERE c=20 for update;
所有记录锁定,因为没有索引，没法确定间隙的范围，因此任何一条记录都可以是20，造成了所有记录锁定，此时没有锁升级，会造成极大的开销

6.RC模式下、D是唯一索引
事务1			事务二 
begin；
delete d=13；		begin；
			insert （10，20，40，13）
此时为什么insert堵塞并加上S锁？

insert的操作：
1.首先寻找最靠近d大于13的记录
2.看此纪录是否有GAP锁
3.判断前一条记录OLD.d=NEW.d（判断唯一性）
4.1相等且无锁，返回插入失败
4.2相等且有锁，阻塞并改变自己为Slock等待前一条事务将锁释放（转变为S lock的真正目的）

### 死锁检测机制|wait-for graph

构建所得信息链表和事务等待链表判断是否存在循环事务，若存在，则选择其一回滚（5.6UNDO量比较少，5.7回滚后一个事务）

### 查看死锁

```my.cnf
innodb_print_all_deadlocks=1 # 开启死锁检测信息
innodb_deadlock_detect=0  #不开启死锁检测机制
```

```mysql
PAPER LESS
show engine innodb status\G   #找到TRANSACTIONS可以查询死锁信息
```

这里的threadID其实是processid       hex 有事务ID和指针，所以会多2个列

INNODB_TRX
INNODB_LOCKS
INNODB_LOCK_WAITS(5.7以上推荐)

```mysql
SELECT
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM information_schema.innodb_lock_waits w
INNER JOIN information_schema.innodb_trx b
ON b.trx_id=w.blocking_trx_id
INNER JOIN information_schema.innodb_trx r
ON r.trx_id=w.requesting_trx_id;
```



锁以事务为单位，commit后释放锁

```my.cnf
innodb_lock_wait_timeout=3  #单位为秒，锁等待超时时间
```

```mysql
set global innodb_status_output_locks=1;  #输出锁的信息
```



### 加锁语法

sql语句可以添加：

​	lock in share mode  #加共享锁
​	for update;  #加排它锁

### 8.0锁的新语法

sql语句可以添加：

​	nowait：不等待，如果需要等待则报错
​	skip locked：跳过锁

## 九、表

表是是关系数据库的核心
表=关系
表是记录的集合
二维表格模型易于人类理解
MYSQL默认存储引擎是基于行（记录）存储
每行记录都是基于列进行组织的

### 表空间及压缩

压缩能提升性能，节省IO，但是CPU负载会变高
叶到buffer pool只需要一次解压，更新操作时会解压数据写一份，压缩数据写日志，压缩日志写不下时，解压数据才进行压缩，写回磁盘

```mysql
show variables like 'innodb_file_per_table'
set global innodb_file_per_table
alter table table_name row_format=compressed,key_block_size=8;  #默认16K压缩到8K
```

透明叶压缩|Transparent Page Compression

​    性能强于普通压缩，也强于不压缩利用了空洞特性

```mysql
CREATE TABLE table_name ( a int primary key ) compression='lz4';   #算法更快
CREATE TABLE table_name ( a int primary key ) compression='zlib';   #比率更高
```

### 分区表

1.将一个表或者索引分解为多个更小、更可管理的部分
2.目前只支持水平分区
3.局部分区索引
	每个分区保存自己的数据与索引
4.分区列必须是唯一索引的一个组成部分

*存在唯一主键，却不用主键分区，是无法创建分区的，因为分区后就不能保证主键唯一性了
解决办法：1.主键使用UUID,全局统一
2.事物处理，用函数获取之前获取到的insert的值
例如：

```mysql
CREATE TABLE orders (
    orderid bigint,
    orderdate datetime,
    primary key (orderid,orderdate),
)
PARTITION BY RANGE COLUMNS (ORDERDATE) (
    partition P0 values less than ('2009-01-01'),
    partition p1 values less than ('2009-02-01'),
);

create table orderid (
    orderid bigint auto_increment,
    primary key(orderid)
);

begin;
insert into orderid value (null);
insert into orders values (last_insert_id(),now());
commit;
```

分区类型：RANGE | LIST | HASH | KEY | COLUMNS
例1：

```mysql
CREATE TABLE T(
    id INT PRIMARY KEY
) ENGINE=INNODB
PARTITION BY RANGE (id)(
PARTITION p0 VALUES LESS THAN (10),
PARTITION p1 VALUES LESS THAN (20)
);
```


*按id的数值范围分区小于10的P0,小于20的p1
*分到前一个PARTITION的不会在分到后一个PARTITION

例2：

```mysql
CREATE TABLE T(
a INT,
b INT
)ENGINE=INNODB
PARTITION BY LIST(B)(
PARTITION p0 VALUES IN (1,3,5,7,9),
PARTITION p0 VALUES IN (0,2,4,6,8)
);
```

例3：

```mysql
CREATE TABLE T(
a INT,
b DATETIME
)ENGINE=INNODB
PARTITION BY KEY (b)
PARTITIONS 4;


```

*key相当于MD5

例4：

```mysql
CREATE TABLE T(
a INT,
b DATETIME
)ENGINE=INNODB
PARTITION BY HASH(YEAR(B))
PARTITIONS 4;
```

*HASH(必须是整型)

### 主键

能够唯一表示数据表中的每一个记录的字段或者字段的组合就称为主键
主键有很多规则

1.自增：identity，auto_increment

2.唯一编号

3.MAX+1

4.GUID(Global unique identifier)5.应用程序主键生成器

多主键的情况
1、数据库的每张表只能有一个主键，不可能有多个主键。
2、所谓的一张表多个主键，我们称之为联合主键。
注：联合主键：就是用多个字段一起作为一张表的主键
例如：	id		date
	1		2002.02
	2		2002.02
	1		2002.03
	2		2002.03
*id和date都是主键，但是可以允许他们重复了，只要id和date不完全相同，通常配合分区

查找没有主键的表

```mysql
SELECT * FROM information_schema.TABLES t LEFT JOIN information_schema.STATISTICS s ON t.table_schema=s.table_schema AND t.table_name=s.table_name AND s.index_name='PRIMARY' WHERE t.table_schema NOT IN ('mysql','performance_schema','information_shema','sys') AND table_type='BASE TABLE' AND s.index_name IS NULL;
```

*left join 会把 s.index_name='PRIMARY' 和s.index_name=NULL的表（没有发现索引的表）一起保留下来一起

### 创建表和字段

推荐使用工具进行创建

```mysql
create table table_name ( col_name1 int unsigned，col_name2 tinyint signed );  
```

创建表table_name 并设置第一个字段col_name1 定义它为int（整数无符号）类型  , 设置第二个字段col_name2 定义它为tinyint （整数有符号）类型



外键约束：当主表的数据发生了变化，那么子表的数据也要发生变化
存在的变化有RESTYICT | CASCADE | SET NULL | NO ACTION
CASCADE =当主表更新，子表也更新
SET NULL = 把子表的值设置为NULL
RESTYICT = NO ACTION

示例：

```mysql
CREATE TABLE product(
	category INT NOT NULL, id INT NOT NULL,
	price DECIMAL,
	PRIMARY KEY (category,id)
) ENGINE=INNODB;

CREATE TABLE customer (
	id INT NOT NULL,
	PRIMARY KEY (id)
) ENGINE=INNODB;

CREATE TABLE product_order (
    no INT NOT NULL AUTO_INCREMENT,
    product_category INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    PRIMARY KEY (no),
    INDEX (product_category,product_id),
    INDEX (customer_id),
    FOREIGN KEY (product_category,product_id)
        REFERENCES product (category,id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (customer_id)
        REFERENCES customer(id)
) ENGINE=INNODB;

insert into product values (30,2,1000);
insert into customer values (1);
insert into product_order values (null,30,2,1);

```

```mysql
update product set category=3 where id=2;
```


当product的category改变，product_order中的product_category也会改变，因为设置了外键

```mysql
update customer set id=20 where id=1;
```

失败，因为外键没有设置是否跟随改变，这表示出这是一种强制性的约束

修改表结构

```mysql
ALTER ONLINE TABLE table_name add col_name1 col_type first|after col_name;
```

ONLINE|OFFINE:默认OFFINE,online线上生产环境使用，不会过度影响性能
first|after:表示字段放置的位置

#修改字段

```mysql
ALTER ONLINE TABLE table_name change old_col_name1 new_col_name1 col_type； 
```

修改字段的名称及类型

```mysql
ALTER ONLINE TABLE table_name modify col_name1 col_type； 
```

仅修改字段的类型

​	设置变量

```mysql
show variables like 'sort_buffer_size'; #显示排序用到的内存
```

​	设置时区

```mysql
set time_zone='+8:00';
```

字符集
	转换字段字符convert

```mysql
alter table table_name convert charset UTF-8;
```

*此操作会锁表，线上谨慎使用

​	修改默认字符，但已经定义字符的字段不修改

```mysql
alter table table_name charset=UTF8;
```

创建的表字符区分大小写

```mysql
create table table_name ( col_name varchar(10) collate utf8mb4_bin, unique key (col_name)); 
```

这样就区分大小写了
unique key：代表唯一性

##显示是当前支持字符集

```mysql
show charset;
```

my.cnf中设置默认字符集

```mysql
[mysqld]
character_set_server=utf8mb4
```

### 字段类型

INT	类型
Type		range				unsigned_Max
tinyint		-128~127				255
smallint		-32768~32767			65535
mediumint	-8388608~8388607			16777215
int		-2147483648~2147483647		4294967295
bigint		-2^63~2^63-1			2^64-1

unsigned		signed		zerofill				auto_increment
无符号		有符号		显示真实属性/值不做任何修改/填充0	自增/每张表只能一个/必须是索引的一部分
								select last_insert_id();  显示上次自增的数值

数字类型
type		占用空间		精度		精确度
FLOAT		4		单精度		低
DOUBLE		8		双精度		中
DECIMAL		变长		高精度		高

FLOAT(M,D)/DOUBLE(M,D)/DECIMAL(M,D)	表示显示M位整数D位小数

字符串类型
type			说明		N的含义	是否有字符集	最大长度
CHAR(N)			定长字符		字符	是		255
VARCHAR(N)		变长字符		字符	是		16384
BINARY(N)		定长二进制字节	字节	否		255
VARBINARY(N)		变长二进制字节	字节	否		16384
TINYBLOB			二进制大对象	字节	否		256
BLOB			二进制大对象	字节	否		16K
MEDIUMBLOB		二进制大对象	字节	否		16M
LONGBLOB		二进制大对象	字节	否		4G
TINYTEXT			大对象		字节	是		256
TEXT			大对象		字节	是		16K
MEDIUMTEXT		大对象		字节	是		16M
LONGTEXT		大对象		字节	是		4G

*BINARY/BLOB主要用于存2进制数据
*VARCHAR会检查字符是否存在，但BINARY不会，BINARY存放的是2进制字节，碰到不同的字符集显示不同的字符
*TEXT相当于VARCHAR但是长度计算方式不同

ENUM枚举类型（多选一）：最多允许65536个值
SET集合类型（多选多）：最多允许64个值

JSON类型

由一系列的key:value组成的数据字符串（类似Mongodb，不需要定义列）
BLOB可以不符合key:value，不能做约束性检查，JSON数据类型会约束一定符合key:value者一格式
JSON查询性能高：查询不需要遍历所有字符串才能找到数据
支持部分属性索引：通过虚拟列的功能可以对JSON中的部分数据进行索引
另外json_extract、json_unquote

JSON插入示例：
create table table_name (
col_name1 int,
col_name2 json
);

insert into table_name (
value1,
'{"colname_json1":"value_json1","colname_json2":"value_json2"}'
)



日期类型
type		占用字节		表示范围
DATETIME	8		1000-01-01 00:00:00~9999-12-31 23:59:59
DATE		3		1000-01-01~9999-12-31
TIMESTAMP	4		1970-01-01 00:00:00 UTC~2038-01-19 03:14:17 UTC
YEAR		1		YEAR(2):1970~2070
				YEAR(4):1901~2155
TIME		3		-838:59:59~838:59:59

*有时区的话推荐TIMESTAMP

地理空间类型|geometry
地理空间类型，可存经纬度



## 十、视图

虚拟的表相当于快捷方式

```mysql
CREATE view V_SALARY as 
  select emp_no,max(salary) from emp.salaries group by emp_no;
```

## 十一、事件

定时器

```mysql
SHOW VARIABLES like   'event_scheduler' ;
set 'event_scheduler'=on;
```

一次：

```mysql
CREATE DEFINER=`root`@`localhost`
EVENT `test2`
ON SCHEDULE AT '2017-11-17 00:00:00.000000' // 只执行一次
ON COMPLETION PRESERVE ENABLE
DO insert into events_list values('event_now', now());
```

循环：

```mysql
CREATE DEFINER=`root`@`localhost` //用户
EVENT `test` //事件的名称
ON SCHEDULE EVERY 60 MINUTE_SECOND //60秒循环一次   SCHEDULE EVERY '0:0:1' HOUR_SECOND    SCHEDULE EVERY '0:1' HOUR_MINUTE  (不同的计时方式)
STARTS '2017-11-01 00:00:00.000000' ENDS '2017-11-30 00:00:00.000000' // 开始时间,结束时间
ON COMPLETION PRESERVE ENABLE //过期后禁用事件而不删除
DO
BEGIN //执行的内容
insert into events_list values('event_now', now());
insert into events_list values('event_now1', now());
END
```

## 十二、触发器|trigger

```mysql
CREATE TRIGGER 触发器名 BEFORE|AFTER 触发事件
ON 表名 FOR EACH ROW
BEGIN
        执行语句列表
END;
```

## 十三、索引

### B+TREE

  组成

​	root page：指针（一个标志性的位置）
​	non leaf page（包括root page）：存储primary KEY、pointers（non leaf page大小是primary key字节数+pointers6字节） 
​	leaf page：数据经过排序(仅逻辑上的)后存储，insert时就通过KEY决定决定插入在哪个块，因此即使无序insert，也能通过索引快速查询，如果某一LEAF PAGE 用完了会进行SPLIT操作，leaf page只存储primary KEY和KEY,想要其他的列还需要通过primary key再次查询表（回表）
​	一叶分为二叶，指针加1或加2

B+TREE的查询方式是通过ROOT PAGE(的PK和key)查找数据放在那个块

索引可以加快排序

创建索引

```mysql
创建索引会锁表
alter table table_name add [unique] index index_name (col_name);   #unique 表示唯一索引
或者
CREATE INDEX indexName ON table_name (col_name);
或者创建表时添加
INDEX [indexName] (username(length))  
```

删除:

```mysql
alter table table_name drop index index_name (col_name); 
```

或者

```mysql
DROP INDEX [indexName] ON mytable; 
```

### MyISAM(堆表)与INNODB（索引组织表）索引

1.MyISAM堆表索引查询代价相同，INNODB除了主键索引都是2次索引（先查索引字段，然后根据主键查找）
2.堆表是无序的，主键范围查找劣势（仅主键劣势）
3.MyISAM_DML操作，所有索引的操作都要修改，维护代价大，Oracle和SQL service的LEAF PAGE 留有一部分空间（MySQL默认1/16）来优化此缺陷，INNODB的仅维护主键索引

### 在线创建索引

```mysql
SHOW VARIABLES LIKE 'INNODB_ONLINE_ALTER_LOG_MAX_SIZE';  #默认128M
```

​	在线创建索引时，所有的更新操作存储在内存日志里，如果有超过128M的更新操作，索引会创建失败
​	此变量可以放在my.cnf中
或者
​	使用percona toolkit

### 复合索引|COMPOUND INDEX:多个键复合成的索引

例如：a,b复合索引是对a排序，（a，b）排序，因此可用于

```mysql
SELECT * FROM TABLE_NAME WHERE a=?;
SELECT * FROM TABLE_NAME WHERE a=? AND b=?;
SELECT * FROM TABLE_NAME WHERE a=? ORDER BY b;   #最常用的调优手段

```

不能用于

```mysql
SELECT * FROM TABLE_NAME WHERE b=?;
```

information_schema.STATISTICS.SEQ_IN_INDEX
	是查找复合索引的关键1、2、3代表复合索引的第1.2.3字段

### 索引覆盖|覆盖索引|COVERING INDEX

查询的列是主键值或已经是KEY了就不需要回表
例如：INDEX（PK1,PK2,KEY1,KEY2）

```mysql
SELECT PK1,KEY2 FROM TABLE WHERE KEY1=?;
```

### 冗余索引|redundant

在已创建（a，b）的复合索引后，a这个索引就被称为冗余索引
在sys库中有schema_redundant_indexes记录冗余索引

### 索引不可见(8.0)

```
ALTER TABLE table_name alter index index_name invisible/visible;
```

### 降序索引(8.0)

需要降序显示的字段加上DESC
例如：ALTER TABLE table_name alter index index_name (col_name1,col_name2 DESC,col_name3 );

5.7的解决方案
1.创建虚拟列
ALTER TABLE order ADD column o_orderdate2 INT (DATEDIFF('2099-01-01',o_orderdate)) VIRTUAL;
2.添加索引ALTER TABLE order add index idx_descdate (col_name1,o_orderdate2,col_name3 );
3.这个新的列就是降序了

### 全文索引

类似WHERE COL LIKE '%XXX%'

一张表一个，添加时不可写入与更新
添加全文索引：ALTER TABLE XXX ADD FULLTEXT INDEX IDX_XXX (TITLE,BODY)
全文索引语法：

```mysql
SELECT * FROM articles WHERE MATCH (title，body) AGAINST ('database' IN NATURAL LANGUAGE MODE); #只要database
SELECT * FROM articles WHERE MATCH (title，body) AGAINST ('+MYSQL -YOURSQL' IN BOOLEAN MODE); #要mysql不要yoursql
SELECT * FROM articles WHERE MATCH (title，body) AGAINST ('database' WITH QUERY EXPANSION); #模糊
```



### 索引倾斜|force index

```mysql
 SELECT * FROM lineitem force index(i_l_orderkey) where l_orderkey=1\G
```



## 十四、查询分析

### 查询状态

```shell
mysqladmin extended-status  -i 1 -r  |grep -i Questions 
```

i  ： 间隔时间
r  ： 除了第一次，后面显示的都是减去前一次后的数据

### 设置连接数

```mysql
SHOW VARIABLES LIKE  'max_connections';
set global max_connections=2048;
```



### 查看连接数

```mysql
show global status like 'thread%'  # 连接数
select * from variables_by_thread;
show processlist;    #当前线程ID（所有）or 它在做什么
select connection_id();    #自己的id
select * from threads limit 1\G  #关联threadid和processid的表
```



### DQL|查询语句

```mysql
SELECT *|col_name1,col_name2 from table_name WHERE [条件1] AND [条件2] GROUP BY [条件3] HAVING [条件4] ORDER BY [条件5] LIMIT [条件6]
```

WHERE：条件筛选

GROUP BY：先分组在显示分组后要显示的字段，如果要显示的字段或函数无法被分组则会报错
例如：select date_format(o_orderDATE,'%YY%m'),ROUND(sum(o_totalprice),2) from orders group by date_format(o_orderDATE,'%YY%m');
#按%YY%m日期格式的o_orderDATE分组，分组后每一天的o_totalprice就无法显示了，所以使用sum(o_totalprice)将每天的o_totalprice合并，变成每个月的，这样就可以显示数据了

HAVING：分组之后的过滤，分组后某些字段就找不到了

ORDER BY：根据某一字段的值进行排序参数ASC|DESC,默认是ACS
ORDER BY 3:   3指col_name3（select col_name1,col_name2，col_name3 from table_name ORDER BY 3;）
如果大量使用ORDER BY ,可以调整变量>排序内存'sort_buffer_size'此参数

LIMIT：限制行数,分页
例如：LIMIT 3;   #相当于LIMIT 0,3
LIMIT 20,10;   #从第二十行之后开始，显示后面10行
LIMIT的分页还是会读取前面记录（不会减少资源的占用）

### 分页优化

建索引，用上一段数据的结果查询，缺点只能上/下一页

### 子查询

ANY：对于子查询中返回的列中的任一数值，如果比较结果为TRUE的话，则返回TRUE

```mysql
SELECT s1 FROM t1 WHERE S1 > ANY (SELECT s1 FROM t2);
```

SOME=ANY

IN equals=ANY

```mysql
SELECT s1 FROM t1 WHERE s1 = ANY (SELECT s1 FROM t2);
SELECT s1 FROM t1 WHERE s1 IN  (SELECT s1 FROM t2);
```

*字段存在NULL值not in 查询结果只会是0和NULL
    字段存在NULL值 in 查询结果只会是1和NULL
        所以要用WHERE col_name is not null 先去除掉NULL
*in会对子查询的结果物化（因为要去重），建立起临时表，这样就可以建立索引加快查询速度了

ALL:对于子查询返回列中的所有值，如果比较结果为TRUE,则返回TRUE
NOT IN equals <> ALL

```mysql
SELECT s1 FROM t1 WHERE s1 > (SELECT s1 FROM t2);
```

EXISTS谓词：仅返回TRUE\FALSE;UNKNOWN返回为FALSE
相关子查询，总是要和外部表发生关联

查询返回自Spain且发生过订单的消费者

例1：
查找表employees中字段emp_no存在于在表dept_emp中满足deptno='d005'的emp_no的值
in的写法

```mysql
SELECT * FROM employees WHERE emp_no IN (SELECT emp_no FROM dept_emp WHERE dept_no='d005') LIMIT 10;
```

EXISTS的写法

```mysql
SELECT * FROM employees WHERE EXISTS ( SELECT * FROM dept_emp WHERE dept_no='d005' AND employees.emp_no =dept_emp.emp_no ) LIMIT 10;
```

例2：
in的写法

```mysql
SELECT orderid,customerid,employeeid,orderdate FROM orders WHERE orderdate IN (SELECT MAX(orderdate) FROM orders GROUP BY (DATE_FORMAT(orderdate,'%Y%M')));
```

EXISTS的写法

```mysql
SELECT orderid,customerid,employeeid,orderdate FROM orders a WHERE EXISTS (SELECT MAX(orderdate) FROM orders b GROUP BY (DATE_FORMAT(orderdate,'%Y%M')) HAVING MAX(orderdate)=a.orderdate);
```

求不是UTF8mb4的表

```mysql
SELECT 
    CONCAT(TABLE_SCHEMA,'.',TABLE_NAME) AS NAME,
    character_set_name,
    GROUP_CONCAT(COLUMN_NAME SEPARATOR ':') AS COLUMN_LIST
FROM information_schema.COLUMNS
WHERE
data_type IN ('varchar','longtext','text','mediumtext','char')
AND character_set_name <> 'utf8mb4'
AND table_schema NOT IN ('mysql','performance_schema','information_schema','sys')
GROUP BY NAME,character_set_name;
```

求每行共占用的多少字节

```mysql
SELECT ROUND (AVG(ROW),2) FROM (
    SELECT (LENGTH(COL_NAME1)+LENGTH(COL_NAME2)+LENGTH(COL_NAME3)) AS row FROM
    table_name
    LIMIT 15000
) AS a;
```

*length仅用于字符串类型，其他会算错，若是整数类型直接根据占用空间算即可

每一个要被引用的查询结果都要起个别名，让另一sql语句调用
起别名的方式是AS <临时名字>

### sys库

有各种查询信息集中在名字有statement的表
SELECT * FROM statement_analysis \G
但SYS库只有5.7之后才有
5.6版本可以通过git clone https://github.com/mysql/mysql-sys   下载

### 查找没有建立索引的表

```mysql
SELECT * FROM TABLES t LEFT JOIN STATISTICS s ON t.TABLE_NAME=s.TABLE_NAME WHERE INDEX_NAME IS NULL AND t.TABLE_SCHEMA<>'information_schema' AND t.TABLE_SCHEMA<> 'sys' AND t.TABLE_SCHEMA<>'performance_schema' AND t.TABLE_SCHEMA<>'mysql'\G
```

### EXPLAIN:查询某一条语句的查询效率

作用：
1- 显示SQL语句的执行计划
2- 5.6支持DML语句
3-  5.6支持JSON格式输出(json可以查看执行成本)
例如： 

```mysql
EXPLAIN format=json select * from table_name ;
```

type:
system:只有一行记录的系统表
const:最多只有一行返回记录，比如主键查询
eq_ref:通过唯一键进行JOIN
ref:使用普通索引进行查询
fulltext:使用全文索引进行查询
ref_or_null:和ref类似，使用普通索引进行查询，但是要查询NULL值
index_merge:or查询会使用到的类型
unique_subquery:子查询的列是唯一索引
index_subquery:子查询的列是普通索引
range:范围扫描
all:全表扫描
代价从低到高

Explain输出--Extra
Extra常见值		说明
using filesort		需要使用额外的排序得到结果
using index		优化器只需要使用索引就能得到结果
using index condition	优化器使用index condition pushdown优化
using index for group by	优化器只需要使用索引就能处理group by 或distinct语句
using join buffer		优化器需要使用join buffer，join_buffer_size
using mrr			优化器使用MRR优化
using temporary		优化器需要使用临时表
using where		优化器使用where过滤



### CARDINALITY:

The count of none unique record(唯一记录数)，越高索引越有价值  CARDINALITY=不重复数

查询CARDINALITY/总记录数<0.1,索引效率低的
我的：

```mysql
select S.TABLE_SCHEMA,S.TABLE_NAME,S.INDEX_NAME,S.CARDINALITY,S.CARDINALITY/T.TABLE_ROWS from STATISTICS S LEFT JOIN TABLES T ON S.TABLE_NAME=T.TABLE_NAME WHERE INDEX_NAME <> 'PRIMARY'  AND S.CARDINALITY/T.TABLE_ROWS <0.1;
```

标准答案：

```mysql
SELECT 
	CONCAT(t.TABLE_SCHEMA,'.',t.TABLE_NAME) table_name,INDEX_NAME, CARDINALITY, 
    TABLE_ROWS, CARDINALITY/TABLE_ROWS AS SELECTIVITY
FROM
    information_schema.TABLES t,
 (
  SELECT table_schema,table_name,index_name,cardinality
  FROM information_schema.STATISTICS 
  WHERE (table_schema,table_name,index_name,seq_in_index) IN (
	  SELECT table_schema,table_name,index_name,seq_in_index
	  FROM information_schema.STATISTICS
	  WHERE seq_in_index=1 )
 ) s
WHERE
    t.table_schema = s.table_schema 
        AND t.table_name = s.table_name AND t.table_rows != 0
        AND t.table_schema NOT IN ( 'mysql','performance_schema','information_schema','sys') 
ORDER BY SELECTIVITY;
```

### SQL JOIN--JOIN算法

simple nested_loop join

（An*Bn）

​	最差

index nested_loop join

​	(基于索引)

​	（外表【驱动表|数据较小的表】、内表【大表、有索引的表】）成本An    低于simple nested_loop join （An*Bn）

block nested-loop join 

​	优化simple nested_loop join，减少内部表的扫描次数(比较次数An*Bn不变)，原理是建立内存空间join buffer（存储内表的数据），join_buffer_size 决定内存大小(每张表，而不是所有表)

hashjoin（Oracle）

​	外表存为HASH TABLE(内存之中)，内表再来比较数据（不需要索引，不需要回表，可以做并发，但只能等值查询）

batched key access join

​	基于INLJ,对PK进行排序再查
​	使用方式查询BKA

优先度INLJ>BNLJ>SNLJ

### 有时候查数据未使用索引的情况

1.查询非主键索引的索引字段范围太大，回表的IO吞吐量过大，代价超过不使用索引（参考IO的计算）

##IO的计算
总记录数S
每行记录大小x
条件过滤后的行数a
B+TREE高度h
LEAF的存储空间（16k）
1.无索引：
IO=S/(16k/x)

2.有索引：
回表次数=a*h=IO数

### MRR优化(多范围优化)（空间换时间）（需要手动选择）

对key值检索获取到的PRIMARYKEY存放到内存空间，然后排序，再统一查表
SELECT /* + MRR(table_name) */ * FROM table_name where col_name > ?;

BKA  join优化（基于MRR）原理查询batched key access join

```mysql
SELECT /* + NO_BKA(t1,t2) */ * FROM t1 INNER JOIN t2 INNER JOIN t3;
```

### 查找排序次数最多的语句

```mysql
SELECT * FROM statements_with_sorting \G
```

### 修改临时表存储大小及排序表大小

```mysql
show variables like '%tmp%';
show variables like 'tmp_table_size';
set tmp_table_size=1024*1024*1024;
set sort_buffer_size=1024*1024*1024;
```

### QPS && TPS

```mysql
SHOW GLOBAL STATUS LIKE '%question%'；
SHOW GLOBAL STATUS LIKE '%uptime%'；
```

### 元数据

描述表、字段数据格式的数据，存放在information_schema中

找出非InnoDB的表

```mysql
USE INFORMATION_SCHEMA
SELECT * FROM TABLES\G  #可以显示出所有表的元数据

SELECT 
    table_schema,
    table_name,
    engine,
    sys.format_bytes(data_length) as data_size
FROM 
    tables
where
    engine <> 'InnoDB'
        AND table_schema NOT IN ('mysql','performance_schema','information_schema');
```

### 特殊数据NULL

NULL是未定义数据
判断某一值是否为NULL时，不能SELECT NULL=NULL;或 SELECT NULL=1;而是select NULL is NULL ;

## 十五、函数

```mysql
count:计数
count(col_name):返回不为NULL的记录数量
count(1):无论是否为NULL的数量（）里的数值是否1都无所谓

floor:向下取整 
比如：select floor(1.9); 结果是1
          select floor(-1.9); 结果是-2

round:四舍五入
例如：select round(9.55421,3); 取小数点后3位

rand:随机 
比如：select rand();  结果是一个0~1随机数
         select floor(i+rand()*(j-i));  结果是i~j之间的一个随机数

repeat:重复数值N次
比如：select repeat('a',3); 结果是重复a3次

length:取字节长度
char_length:取字符长度
比如：select length('我'),char_length('我');
	     3		1
*仅用于字符串


hex:将字符串转换对应的16进制的值
例如：select hex('abc')

cast:将一种类型转换成另一种类型
例1：select cast(123 as char(10));  #此处是数值123（因为没有引号）改成了字符串123
例2：select cast('我' as char(1) charset gbk); #此处是默认字符'我'转换成了gbk显示

MD5：加密
例如:insert into user values (md5('aaa')); 

concat:拼接字符串
例1：select concat('a','b','c');  结果是abc
例2：insert into user values (md5(concat('123456','mypasswd')));  #这样密码就安全了

concat_ws: 通过什么字符（第一个''）连接字符串(第二个起的''内的字符串)
例如：select concat_ws('.','a','b','cd');

upper:大写
lower:小写
例如：select upper('Abc'),lower('abC');  结果是ABC，和abc

lpad:左填充字符
rpad:有填充字符
例如：select lpad('aaa',8,'.'); 往aaa的左边填充8个点

now:现在的时间
current_timestamp:与NOW差不多
例如：select now(6); 显示现在时间，秒小数点后6位

sysdate:是执行到sysdate的系统时间，now和current_timestamp是执行语句的时间
例如：select now(),sysdate(),sleep(3),now(),sysdate(); 
结果是
2017-03-04 12:52:46		2017-03-04 12:52:46		2017-03-04 12:52:46		2017-03-04 12:52:49

date_format:定义时间格式
例如：select date_format(now(),'%Y_%m_%d'); 结果是2022_01_26;

json_extract: json格式的其中之一的数据提取出来（会有双引号）
json_unquote:去掉json_extract提取的数据的双引号
例1：select uid,json_extract(data,"$.name") from UserJson;  #结果是“David”
*select uid,data->"$.name"  from UserJson;
例2：select uid,json_unquote(json_extract(data,"$.name")) from UserJson;  #结果是David
*select uid,data->>"$.name"  from UserJson;
*从UserJson表提取出uid和data中的name这一字段，对于MYSQL来说data才是字段，所以用函数来取出JSON格式的数据

sys.format_bytes:给定一个字节数，将其转换为人类可读的格式
例如：
SELECT 
    table_schema,
    table_name,
    engine,
    sys.format_bytes(data_length) as data_size
FROM 
    tables
where
    engine <> 'InnoDB'
        AND table_schema NOT IN ('mysql','performance_schema','information_schema');

UUID:生成GUID,全局唯一
例如：SELECT UUID();

UUID_TO_BIN:转化成16个字节的UUID
例如：SELECT UUID_TO_BIN(UUID());
*仅8.0有

replace：替换  
例如： select replace(uuid(),'-','');  #把UUID的‘-’替换为‘’

group_concat:把分组后无法完全显示，但又想显示的数据通过逗号（默认）合并起来形成一条数据
group_concat(col_name order by col_name separator ':')  #separator可以替换分隔符
```

## 十六、范式|NORMAL FORM

定义：数据库结构定义的规范
组成：第一范式、第二范式、第三范式

目的：
1.消除数据冗余（因此使用更多的空间）。
2.使对数据的修改更容易，而且能避免这样做的时候出现异常。更容易执行一致性的约束。
3产生一个与数据表示的情况更相似的更容易理解的结构。

### 1NF

没有重复的组
全部的键属性都定义了
全部的属性都依赖主键
一定要有主键

### 2NF

是1NF
不包含部分依赖（属性只依赖主键的一部分）

### 3NF

是2NF
不包含传递依赖（非主属性通过另一个非键值依赖于主键）

优点：
    更新操作通常比较快
    没有或者只有很少重复的数据
    表相对比较小、容易被缓存
缺点：
    查询数据需要多次关联

## 十七、备份恢复

### 逻辑备份mysqldump

```shell
mysqldump --single-transaction --master-data=1 -R --triggers -E -B database_name > name.sql
```

--single-transaction	指只开启一个事务（防止脏读）

-R=--routines	存储过程

--triggers		触发器

-E=--events	事件

-B=--database	数据库

-w=where	某记录

--master-data=1	获取到二进制日志文件的位置

--quick    一行行备份，不经过buffer，默认打开

一步备份并压缩

```shell
mysqldump --single-transaction --master-data=1 -R --triggers -E -B database_name | gzip -c > name_backup.tgz
```

gzip -c 压缩并输出到标准输出

一步备份压缩并传到另一台服务器

```shell
mysqldump --single-transaction --master-data=1 -R --triggers -E -B database_name | gzip -c | ssh root@IP 'cat > /tmp/name_backup.tgz'
```

解压并恢复

```shell
gunzip < name_backup.tgz |mysql -p
```

Q1.

​    a
​	1
​	3
​	5
​	7
事务1			事务2
begin;
del a<=7;		begin;
​					insert a=2
​					commit;
commit

为什么binlog_format要设置为ROW?

实际上先执行del a<=7;在执行insert a=2，最终T1留下a=2；

而BINLOG中因为事务2先提交变成insert a=2后del a<=7;

如果使用statement，主从同步就会错误

使用row，日志记录是一行行记录的，a=2不会被删除，主从同步完成；

Q2.mysqldump --single-transaction备份的是备份开始时还是结束后的数据？

开始。

因为mysqldump的备份在一个事务里完成，事务是RR级别的，这意味着只会存在一个readview，且在事务开启的时候启动readview，读到的数据只会是开启readview之前的记录，保证了不会存在脏读的情况

Q3.mysqldump中出现SAVEPOINT sp的作用是？

SAVEPOINT是为了建立检查点，备份的第一步是获取表的元数据信息，这其中会存在锁表的情况，等到获取了信息rollback到SP，就能给元数据解锁

Q4.--master-data是如何实现的？

在备份前先FLUSH TABLES WITH READ LOCK把数据库实例锁住

打开事务后SHOW MASTER STATUS来获取二进制日志的位置

再UNLOCK TABLES解锁数据库

### 多线程逻辑备份mydumper

```shell
mydumper -G -E -R --trx-consistency-only -t 4 -o /back_20220206 -c -B 
```

-G = --triggers		触发器
-E = --events		事件
-R = --routines		存储过程
--trx-consistency-only	事务一致性
-t = --thread		线程数默认4
-o = --outputdir		指定的文件夹
-B = --database		指定的数据库
-T = --tables-list		指定的表
-c = --compress		压缩
--rows=N			每N行一个文件

恢复

```shell
myloader -d /back_20220206 -t -B
```

-d = --directory		指定目录
-t = --thread		线程数默认4
-B = --database		指定的数据库（可以是和备份前不同的数据库）

Q1.mydumper是如何保证事务一致性？

mydumper会先进行FLUSH TABLES WITH READ LOCK，锁表，然后每个线程start transaction with consistent snapshot;来确保一致性,再UNLOCK TABLES解锁数据库

Q2.多个线程怎么对一张表进行备份？

利用唯一索引的特性对数据进行分片，然后再分给每个线程备份

### 物理备份percona-xtrabackup

1.需要创建一个拥有RELOAD,process,LOCK TABLES,REPLICATION CLIENT权限的用户

2.

```shell
innobackupex --compress --compress-threads=8 --stream=xbstream --user=root --parallel=4   ./ > backup.xbstream
```

--compress		压缩

--compress-threads=8	压缩用的线程数

--stream=xbstream		流的格式

--parallel=4		备份用的线程数

--throttle=		限制备份时的IO速度

--user=root		指数据库的user

percona-xtrabackup备份表空间数据的同时也会备份REDO日志

所以备份的是结束时间点的数据

压缩备份并传到远程主机

```shell
innobackupex --compress --compress-threads=8 --stream=xbstream ./ |ssh user@IP 'xbstream -x'
```

恢复
一、
1.

```shell
xbstream -x < backup.xbstream
```

解除打包状态

2.

```shell
for f in `find ./ -iname "*\.qp"`; do qpress -dT4 $f $(dirname $f) && rm -f; done
```

寻找QP结尾的文件，然后循环通过qpress 解压T4代表4个线程，然后删除这个QP结尾的文件
3.

```shell
innobackupex --apply-log ./
```

进入目录应用重做日志

4.重命名数据目录的名字为mysql数据库目录

5.

```shell
chown -R mysql:mysql /$datadir
```

二、
1.

```shell
xbstream -x < backup.xbstream
```

解除打包状态
2.

```shell
for f in `find ./ -iname "*\.qp"`; do qpress -dT4 $f $(dirname $f) && rm -f; done
```

寻找QP结尾的文件，然后循环通过qpress 解压T4代表4个线程，然后删除这个QP结尾的文件

3.

```shell
innobackupex --apply-log /path to BACKUP-DIR
```

应用重做日志

4.

```shell
innobackupex --defaults-file=/etc/my.cnf --copy-back /path to BACKUP-DIR
```

5.

```shell
chown -R mysql:mysql /$datadir
```

增量备份与恢复

Q1.为什么会有innobackupex最后会flush engine logs;？
flush engine logs;是指将REDO日志刷新到磁盘

### 数据的导入导出

导出

```my.cnf
secure_file_priv=NULL;  #不可导入导出，可以定义一个文件夹，或设置为 ''则不限路径
```

仅表数据

```mysql
select * into outfile '/tmp/sqlbak/tb_student.txt' from db.table;  #可以加where等限制条件
```

导入

1.

```mysql
load data local infile '/tmp/sqlbak/tb_student.txt' into table tb_student;
```

2.

```mysql
mysqlimport dbname /path/file --fields-terminated-by=':' --lines-terminated-by='\n' -p  #要求，导出的文件必须和数据表名称完全一致
```

--fields-terminated-by=':'，指定导出文件的分隔符为冒号:

--lines-terminated-by='\n'，指定每一行的结尾使用的符号,\n代表换行符

### mysql-5.6 INNODB独立表空间导入导出

0.目的服务器：随便建个表
1.目的服务器：ALTER TABLE t DISCARD TABLESPACE;
2.源服务器：FLUSH TABLES t FOR EXPORT;
会锁表
3.从源服务器上拷贝：t.idb,t.cfg文件到目的服务器
4.源服务器：UNLOCK TABLES
5.目的服务器：ALTER TABLE t IMPORT TABLESPACE;

## 十八、慢查询日志

### my.cnf

```my.cnf
slow_query_log=1 #是否打开慢查询日志 =1开启
slow_query_log_file=slow.log #决定慢查询日志名称
long_query_time=2 #慢查询日志阈值，超过该值的有问题，将会记录
min_examined_row_limit=100 #扫描记录少于该值的SQL不记录到慢查询日志,比如该值=100时，扫描记录超过100行同时超过阈值才记录
log_queries_not_using_indexes #将没有使用索引的SQL记录到慢查询日志
log_throttle_queries_not_using_indexes=10 #限制每分钟记录没有使用索引SQL语句的次数
log_slow_admin_statements #记录管理操作，如alter/analyze table
log_output #慢查询日志格式，{FILE|TABLE|NONE}，table时记录到数据库mysql.slow_log表中
log_slow_slave_statements #在从服务器上开启慢查询日志
log_timestamps=system #写入时区信息，需要改system时间，仅在5.7中生效，因此此配置应放在[mysqld-5.7]中
```

### 清理慢查询日志

1.

```mysql
mv slow.log slow.log`date`  
```

 

2.

```mysql
flush slow logs;
```

## 十九、通用日志

```my.cnf
general_log=1 #打开通用日志，但是性能会下降
general_log_file=general.log #设置通用文件名
```

## 二十、性能调优

### 操作系统LINUX

内核并发数优化

```shell
cat >> /etc/sysctl.conf << EOF
net.ipv4.tcp_max_tw_buckets = 20480
net.ipv4.tcp_max_syn_backlog =20480
net.core.netdev_max_backlog = 262144
net.ipv4.tcp_fin_timeout = 20
EOF
```

减少SWAP使用

```shell
echo "0" > /proc/sys/vm/swappiness
```

### 文件系统

```shell
mount -o noatime,nobarrier /dev/sdb1/data  #感觉提升不多
```

### 硬件设置

(1)内存：NUMA

```shell
yum install numactl
numactl --interleave=all mysqld &
```

```my.cnf
innodb_numa_interleave=off
```

(2)网卡

网卡软中断

解决方法：启用网卡多队列

```shell
set_irq_affinity.sh   #google的脚本
service irqbalance stop
```

(3)RAID

开启写缓存

```shell
查看电量
megacli -AdpBbuCmd -GetBbuStatus -aALL | grep "Relative State of Charge"
查看充电状态
megacli -AdpBbuCmd -GetBbuStatus -aALL | grep "Charger Status"
查看缓存策略
megacli -LDGetProp -Cache -LALL -aO
```

(4)SSD

```my.cnf
innodb_flush_neighbors=0   #SSD一定要为0
innodb_log_file_size=4G   #至少4G、推荐8G
```

### SQL优化

JOIN一定要创建索引

### 数据库配置

(1)innodb_buffer_pool优化

```my.cnf
innodb_buffer_pool_size   #建议机器（60%-80%），5.7可以在线调整
innodb_buffer_pool_instances=N   #要设置为CPU核心数
innodb_page_size=4096   #不要设置为4K
innodb_flush_method=O_DIRECT   #fdatasync(默认，占内存)，O_DSYNC（性能最差），O_DIRECT（不经过OS缓冲，最不占内存）
```

(2)刷新脏页

```my.cnf
innodb_io_capacity=4000   #每秒钟刷新脏页数量,磁盘读写性能的一半
innodb_page_cleaners=1   #至少CPU数量的一半或CPU的数量
innodb_flush_neighbors=0/1/2   #5.6版本SSD要设置为0
```

(3)redo日志

```my.cnf
innodb_log_file_size=1900M/4G   #至少4G、推荐8G
innodb_log_buffer_size=8M   #8M够用
innodb_log_files_in_group=2/3  #指定重做日志文件组中文件的数量，默认2
innodb_log_group_home_dir   #指定日志文件组所在的路径，默认./ ，表示在数据库的数据目录下。
```

(4)undo日志

```my.cnf
innodb_purge_threads=4    #回收线程|Purge Thread可以多调整一点
```

(5)线程池

```my.cnf
thread_handling=pool-of-threads  #默认情况是one-thread-per-connection，即不启用线程池
thread_pool_size=32   #CPU
thread_pool_oversubscribe=3  #该参数设置group中的最大线程数，每个group的最大线程数为thread_pool_oversubscribe+1，注意listener线程不包含在内。
extra_port =3333 #额外端口
thread_pool_high_prio_mode=transactions #transactions对于已经启动事务的语句放到高优先级队列中，statements这个模式所有的语句都会放到高优先级队列中，不会使用到低优先级队列。none：这个模式不使用高优先级队列。
thread_pool_idle_timeout  #worker线程最大空闲时间，默认为60秒，超过限制后会退出。
thread_pool_max_threads  #该参数用来限制线程池最大的线程数，超过该限制后将无法再创建更多的线程，默认为100000。
thread_pool_stall_limit    #该参数设置timer线程的检测group是否异常的时间间隔，默认为500ms。
```

(6)二进制日志

```my.cnf
log-bin=/binlog/mysqld-bin   #日志的路径及名字
binlog-format=row   #日志格式STATEMENT、ROW、MIXED ，主从复制要选择ROW，STATEMENT会有数据不一致风险
log-expire-day=7   #binlog失效天数,设置可以节省磁盘空间，也可以不设置，用于做增量备份
binlog_rows_query_log_events=1   #会记录对应的SQL语句，最好要开启1=ON
```

(7)慢查询日志

```my.cnf
slow_query_log=1 #是否打开慢查询日志 =1开启
slow_query_log_file=slow.log #决定慢查询日志名称
long_query_time=2 #慢查询日志阈值，超过该值的有问题，将会记录
min_examined_row_limit=100 #扫描记录少于该值的SQL不记录到慢查询日志,比如该值=100时，扫描记录超过100行同时超过阈值才记录
log_queries_not_using_indexes #将没有使用索引的SQL记录到慢查询日志
log_throttle_queries_not_using_indexes=10 #限制每分钟记录没有使用索引SQL语句的次数
log_slow_admin_statements #记录管理操作，如alter/analyze table
log_output #慢查询日志格式，{FILE|TABLE|NONE}，table时记录到数据库mysql.slow_log表中
log_slow_slave_statements #在从服务器上开启慢查询日志
```

## 二十一、忘记密码

1.在my.cnf[mysqld]中添加

skip-grant-tables

2.重启mysqld

3.use mysql

4.select user,host,authentication_string from user;

5.update user set authentication_string = password('passwd') where user = 'root' and host = 'localhost';

6.关掉skip-grant-tables

## 二十二、主从同步

### 传统

master

1.创建用于同步的账号

```shell
create user 'replication_name'@'IP' identified by 'passwd';
```

2.刷新表并锁表

```mysql
flush tables with read lock;
```

3.记录position

```mysql
show master status;
```

slave

4.指定master

```mysql
change master to
master_host='IP',master_user='replication_name',master_password='passwd',master_port=3306,master_log_file='binlog.000003',master_log_pos=781;
```

5.

```mysql
start slave;
```

6.master 

```mysql
unlock tables;
```

### GTID

1.MASTER  >> my.cnf

```my.cnf
gtid-mode=on
log-slave-updates=1
enforce-gtid-consistency
```

2.SLAVE  >>  my.cnf

```my.cnf
log-bin=/usr/local/mysql/data/binlog	# 必须要开启二进制
gtid-mode=on
log-slave-updates=1
enforce-gtid-consistency
skip-slave-start
```

3.重启MYSQLD

4.设置只读模式 

```mysql
set @@global.read_only=ON;
```

5.SLAVE上配置

```mysql
stop slave;
reset slave;
change master to
master_host='IP',master_user='replication_name',master_password='passwd',master_port=3306,master_log_file='binlog.000003',master_log_pos=781;
start slave;
```

6.关闭主从服务器只读模式

## 二十三、安装插件

```mysql
show plugins;
#安装
install plugin validate_password soname 'validate_password.so';
```

## 二十四、免密登录

```mysql
mysql_config_editor set --login-path=my3306 --user=root --socket=/tmp/mysql3306.sock --password
mysql_config_editor print --all
mysql --login-path=my3306
```

