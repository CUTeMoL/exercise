# PostgreSQL

中文文档:

```url
http://www.postgres.cn/docs/17/index.html
```

## 一、安装

详细参考`install.py`

一个简单案例:

```shell
#!/bin/bash
mkdir /usr/local/pgsql
./configure \
    --prefix='/usr/local/pgsql' \
    --with-systemd \
    --enable-nls \
    --with-perl \
    --with-python \
    --with-tcl \
    --with-llvm \
    --with-lz4 \
    --with-zstd \
    --with-openssl \
    --with-gssapi \
    --with-ldap \
    --with-pam \
    --with-libxml \
    --with-libxslt \
    --with-uuid=e2fs \
   XML2_CONFIG="/usr/bin/xml2-config"
make
make all
make install 
adduser postgres
mkdir -p /usr/local/pgsql/data
chown postgres /usr/local/pgsql/data
su postgres -c "/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data"
cp postgresql.service /etc/systemd/system/postgresql.service

```

## 二、启动

```shell
# pg_ctl调用服务端
${pgsql_prefix}/bin/pg_ctl -D ${data_directory} -l logfile start
# 服务端直接运行
${pgsql_prefix}/bin/postgres -D ${data_directory}
# 服务端直接运行并指定配置文件路径
${pgsql_prefix}/bin/postgres  -c config_file='filename'
```

## 三、配置

基本上保存在${data_directory},可以自己决定,

有个`ALTER SYSTEM set ${option} = ${value};`命令提供了一种改变全局默认值的从SQL,实际不会立即生效,而是保存到数据目录的`postgresql.auto.conf`,下次重启会覆盖`${config_file}`的设置

### 嵌套配置

```shell
include 'filename'
include_if_exists 'filename' # 忽略不存在
include_dir 'directory' # 只有以后缀名 .conf结尾的非目录文件才会被包括.以. 字符开头的文件名也会被忽略,多个配置文件会按文件名顺序
```

### 重要配置

```shell
# 其他配置文件
data_directory = 'directory' # 指定数据目录
hba_file = 'filename' # 指定基于主机认证配置文件
ident_file = 'filename' # 指定用于用户名称映射的配置文件
external_pid_file = "filename" # 指定可被服务器创建的用于管理程序的额外进程 ID文件

# 监听连接相关
listen_addresses = 'localhost,0.0.0.0,::'
port = 5432 
max_connections = 100
reserved_connections = 0 # 确定为具有 pg_use_reserved_connections 角色权限的连接保留的连接“槽”数量
superuser_reserved_connections = 3 # 必须小于 max_connections-reserved_connections 新的连接将仅接受超级用户的阈值,保证超级用户能连
unix_socket_directories = 'directory' # 套接字保存目录
unix_socket_group = '' # 填group的名字，可以不填
unix_socket_permissions = 0777 # 设置 Unix 域套接字的访问权限

## tcp连接相关(默认0跟随系统就好)
tcp_keepalives_idle = 0 # tcp连接无活动时,保持连接时间,0跟随系统
tcp_keepalives_interval = 0 # 指定了发送keepalive探测包的时间间隔,0跟随系统
tcp_keepalives_count = 0 # 指定了发送keepalive探测包的次数,0跟随系统
tcp_user_timeout = 0 # 指定传输数据在未被确认的情况下可以保留的时间长度, 超过此时间后TCP连接将被强制关闭,0跟随系统
client_connection_check_interval = 0 # 指定设置检查客户端是否保持连接的可选检查的时间间隔, 超过此时间后TCP连接将被强制关闭,0跟随系统

## 安全认证
authentication_timeout = 1min # 允许完成客户端认证的最长时间
password_encryption = scram-sha-256 # 口令算法[scram-sha-256|md5]
scram_iterations = 4096 # 使用SCRAM-SHA-256加密密码时要执行的计算迭代次数
krb_server_keyfile = '/usr/local/pgsql/etc/krb5.keytab' # 设置服务器的Kerberos密钥文件的位置
krb_caseins_users = off # GSSAPI用户名大小写是否敏感,off为大小写敏感
gss_accept_delegation = off # 设置是否应接受来自客户端的GSSAPI委派,off为不会接受来自客户端的凭据

## ssl,这块具体看源文档
ssl = off # 是否启用SSL连接
ssl_ca_file = '' # 指定包含 SSL 服务器证书颁发机构(CA)的文件名
ssl_cert_file = 'server.crt' # 指定包含 SSL 服务器证书的文件名, 默认为空,表示不加载CRL文件,默认值是server.crt
ssl_crl_dir = '' # 指定包含SSL客户端证书吊销列表(CRL)的目录名称,默认空为数据目录
ssl_key_file = 'server.key' # 指定包含 SSL 服务器私钥的文件名,默认值是server.key

# 系统资源

## 内存相关
shared_buffers = 128MB # 设置为系统总内存的 25%-40% 比较好
huge_pages = try # 控制是否为主共享内存区域请求大页.有效值为try(默认值), on和off
huge_page_size = 0 # 控制巨型页的大小,当设置为0时,将使用系统默认的巨型页大小. 非默认设置当前仅在Linux上支持,一般是 2MB 和 1GB (Intel and AMD), 16MB 和 16GB (IBM POWER), 还有 64kB, 2MB,32MB 和 1GB (ARM).
temp_buffers = 8MB # 为每个数据库会话设置用于临时缓冲区的最大内存.这些是仅用于访问临时表的会话本地缓冲
max_prepared_transactions = 0 # 设置可以同时处于“prepared”状态的事务的最大数目,把这个参数设置 为零(这是默认设置)将禁用预备事务特性
work_mem = 4MB # 设置查询操作(如排序或哈希表)在写入临时磁盘文件之前可使用的基本最大内存量. 如果未指定单位,则将其视为千字节.默认值为四兆字节(4MB),这个操作针对每个查询的,有同时进行的任务会超出这个设定值
hash_mem_multiplier = 2.0 # 用于计算哈希操作可以使用的最大内存量.最终限制由将work_mem乘以hash_mem_multiplier确定.
maintenance_work_mem = 64MB # 指定在维护性操作(例如VACUUM、CREATE INDEX和ALTER TABLE ADD FOREIGN KEY)中使用的 最大的内存量
autovacuum_work_mem = -1 # 指定每个自动清理工作者进程能使用的最大内存量,其默认值为 -1,表示转而使用 maintenance_work_mem的值
vacuum_buffer_usage_limit = 2MB # 指定由缓冲区访问策略 用于VACUUM和ANALYZE命令的大小.设置为 0时,操作可以使用任意数量的shared_buffers. 否则,有效大小范围是从128 kB到16 GB.
logical_decoding_work_mem = 64MB # 指定逻辑解码要使用的最大内存量,每个链接共用,因此可以大于work_mem
commit_timestamp_buffers = 0 # 指定用于缓存pg_commit_ts内容的内存量,默认值为0,表示请求 shared_buffers/512,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB
multixact_member_buffers = 32 # 指定用于缓存pg_multixact/members内容的共享内存大小,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB
multixact_offset_buffers = 16 # 指定用于缓存pg_multixact/offsets内容的共享内存大,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB
notify_buffers = 16 # 指定用于缓存pg_notify内容的共享内存大小,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB
serializable_buffers = 32 # 指定用于缓存pg_serial内容的共享内存大小,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB
subtransaction_buffers = 0 # 指定用于缓存pg_subtrans内容的共享内存大小,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB. 默认值为0,表示请求shared_buffers/512,最多1024块,但不少于16块
transaction_buffers = 0  # 指定用于缓存pg_xact内容的共享内存大小,如果该值未指定单位,则视为块数,即BLCKSZ字节,通常为8kB. 默认值为0,表示请求shared_buffers/512,最多1024块,但不少于16块
max_stack_depth  = 2MB # 指定服务器执行栈的最大安全深度,
shared_memory_type = mmap # 指定服务器应用于主共享内存区域的共享内存实现,[mmap|sysv|windows]
dynamic_shared_memory_type = posix # 指定服务器应该使用的动态共享内存实现,[posix|mmap|sysv|windows]
min_dynamic_shared_memory = 0 # 指定在服务器启动时将要分配给并行查询使用的内存容量,当此内存区域不够用或被并发查询耗尽时,新的并行查询尝试使用dynamic_shared_memory_type配置的方法从操作系统临时分配额外的共享内存,由于内存管理开销该方法可能慢一些.

## 磁盘相关
temp_file_limit = -1 # 指定进程可以用于临时文件(如排序和哈希临时文件)或保留游标的存储文件的最大磁盘空间,默认-1没有限制
max_notify_queue_pages = 1048576 # 指定为 NOTIFY / LISTEN 队列分配的最大页面数

## 内核资源使用相关
max_files_per_process = 1000 # 设置每个服务器子进程允许同时打开的最大文件数目

## 基于代价的清理延迟
vacuum_cost_delay = 0 # 当超出开销限制时进程将要休眠的时间量
vacuum_cost_page_hit = 1 # 清理一个在共享缓存中找到的缓冲区的估计代价
vacuum_cost_page_miss = 2 # 清理一个必须从磁盘上读取的缓冲区的代价
vacuum_cost_page_dirty = 20 # 当清理修改一个之前干净的块时需要花费的估计代价
vacuum_cost_limit = 200 # 这是累计的成本，当达到该值时，清理进程将休眠 vacuum_cost_delay指定的时间

## 后台写入器
bgwriter_delay = 200ms # 指定后台写入器活动轮之间的延迟时间
bgwriter_lru_maxpages = 100 # 在每个轮次中，不超过这么多个缓冲区将被后台写入器写出
bgwriter_lru_multiplier = 1.0 # 每一轮次要写的脏缓冲区的数目基于最近几个轮次中服务器进程需要的新缓冲区的数目*bgwriter_lru_multiplier
bgwriter_flush_after = 512kB # 只要后台写入的数据超过这个数量，尝试强制 OS 把这些写发送到底层存储上

## 异步行为
backend_flush_after = 0 # 当单个后端写入数据的量超过这个数量时,尝试强制操作系统发送这些写入到底层存储
effective_io_concurrency = 1 # 设置PostgreSQL可以同时被执行的并发磁盘 I/O 操作的数量
maintenance_io_concurrency = 10 # 与effective_io_concurrency相似,但用于支持许多客户端会话完成的维护工作,这个值可以被覆盖,通过设置同名的表空间参数
io_combine_limit = '128kB' # 控制在合并I/O操作中最大的I/O大小
max_worker_processes = 8 # 设置集群可以支持的最大后台进程数
max_parallel_workers_per_gather = 2 # 设置单个`Gather`或者`Gather Merge`节点能够开始的工作者的最大数量,默认值是2.把这个值设置为0将会禁用并行查询执行
max_parallel_maintenance_workers = 2 # 设置单个实用程序命令可启动的最大并行工作进程数。目前，构建B树或BRIN索引时的CREATE INDEX，以及不带 FULL选项的VACUUM。并行工作进程从由 max_worker_processes建立的进程池中获取，受限于 max_parallel_workers。默认值为2。将此值设置为0 将禁用实用程序命令使用并行工作进程。
max_parallel_workers = 8 # 设置集群支持的最大并行操作工作进程数。默认值为8。增加或减少此值时， 还应考虑调整max_parallel_maintenance_workers和 max_parallel_workers_per_gather。 另外，请注意，如果此值设置高于max_worker_processes， 则不会生效，因为并行工作进程是从该设置建立的工作进程池中分配的
parallel_leader_participation = on # 允许leader进程在Gather 和 Gather Merge节点下执行查询计划，而不是等待worker进程。 默认值是on。 设置该值为off可以降低workers因为leader读取元组的速度不够快而被阻塞的可能性，但在第一个元组生成之前需要leader进程等待worker进程启动。 leader能帮助或阻碍性能的程度取决于计划类型，workers的数量和查询持续时间。

# 事务相关
## 预写式日志(WAL)
wal_level = '' # wal_level决定多少信息写入到 WAL 中。默认值是replica，它会写入足够的数据以支持WAL归档和复制，包括在后备服务器上运行只读查询。[minimal|replica|logical]
fsync = on # 如果打开这个参数，PostgreSQL服务器将尝试确保更新被物理地写入到磁盘
synchronous_commit = on # 指定数据库服务器返回“success”指示给客户端之前，必须要完成多少WAL处理,[off(异步提交,不等待WAL写入即返回,性能最好)|local(仅等待本地WAL持久化)|on(在流复制中需等待至少一个同步备库持久化WAL)|remote_write(等待备库将WAL写入OS缓存)|remote_apply(需等待备库应用WAL,安全性最高)]
wal_sync_method = fdatasync # 用来向强制 WAL 更新到磁盘的方法。如果fsync是关闭的，那么这个设置就不相关，因为 WAL 文件更新将根本不会被强制 [open_datasync|fdatasync|fsync|fsync_writethrough|open_sync]
full_page_writes = on # 当这个参数为打开时，PostgreSQL服务器在一个检查点之后的页面的第一次修改期间将每个页面的全部内容写到 WAL 中
wal_log_hints = off # 当这个参数为on时，PostgreSQL服务器一个检查点之后页面被第一次修改期间把该磁盘页面的整个内容都写入 WAL，即使对所谓的提示位做非关键修改也会这样做
wal_compression = off # 此参数启用使用指定的压缩方法对WAL进行压缩,会增加在WAL记录期间进行压缩时的额外CPU消耗.[off|pglz|lz4|zstd]
wal_init_zero = on # 如果设置为on（默认值），此选项会导致新的 WAL 文件被零填充,在某些文件系统上，这可确保在我们需要写入 WAL 记录之前分配空间
wal_recycle = on # 如果设置为 on （默认值），此选项通过重命名来回收 WAL 文件，从而避免创建新文件
wal_buffers = -1 # 用于还未写入磁盘的 WAL 数据的共享内存量。默认值 -1 选择等于shared_buffers的 1/32 的尺寸（大约3%）
wal_writer_delay = 200ms # 指定WAL写入器刷新WAL的频率，以时间为单位(文件系统缓存)
wal_writer_flush_after = 1MB # 指定积累多少数据后强制落盘)
commit_delay = 0 # 设置commit_delay会在执行WAL刷新之前添加时间延迟(事务会合并后提交)
commit_siblings = 5 # 在执行commit_delay延迟时，要求的并发活动事务的最小数目
### WAL检查点(崩溃恢复用)
checkpoint_timeout = 5min # 自动 WAL 检查点之间的最长时间。如果指定值时没有单位，则以秒为单位
checkpoint_completion_target = 0.9 # 指定检查点完成的目标，作为检查点之间总时间的一部分
checkpoint_flush_after = 256kB # 当执行检查点时写入的数据量超过此数量时，就尝试强制 OS 把这些写发送到底层存储
max_wal_size = 1GB # 在自动检查点期间允许WAL增长的最大大小
min_wal_size = 80MB # 只要 WAL 磁盘用量保持在这个设置之下，在检查点时旧的 WAL 文件总是 被回收以便未来使用，而不是直接被删除。这可以被用来确保有足够的 WAL 空间被保留来应付 WAL 使用的高峰，例如运行大型的批处理任务
archive_mode = '${shell_command}' # 当启用archive_mode时，完成的WAL段会通过设置 archive_command或 archive_library发送到归档存储 [off|on|always],always从库也会执行归档(包括主库运行、recovery模式和standby模式),wal_level要大于minimal,归档才能启用
archive_command = '${shell_command}' # 本地 shell 命令被执行来归档一个完成的 WAL 文件段。字符串中的任何%p被替换成要被归档的文件的路径名， 而%f只被文件名替换 参考 'rsync -av %p user@remote:/archive/%f'，与archive_library不能同时设置
archive_library = '' # 用于归档已完成的WAL文件段的库,与archive_command不能同时设置
archive_timeout = 0 # 非0值代表日志切换的时间,没单位时默认单位为秒,也可以自己写单位
### 恢复
recovery_prefetch = try # 是否在恢复期间尝试预取在WAL中引用但尚未在缓冲池中的块,[off|on|try]设置 try仅在操作系统提供 posix_fadvise函数时才启用 预取，该函数目前用于实现预取
wal_decode_buffer_size = 512kB # 服务器可以在WAL中查找预取块的最大提前量限制,如果未指定单位，则将其视为字节。 默认值为512kB
restore_command = '${shell_command}'# 用于获取 WAL 文件系列的一个已归档段的本地 shell 命令
archive_cleanup_command = '${shell_command}' # 目的是提供一种清除不再被后备服务器需要的旧的已归档 WAL 文件的机制
recovery_end_command = '${shell_command}' # 这个参数指定了一个将只在恢复末尾被执行一次的 shell 命令
```

## 四、特性

### 1. `PREPARE TRANSACTION`

为两阶段提交准备当前事务,`PREPARE TRANSACTION`后可以由其他会话进行 `COMMIT PREPARED`,专为分布式设计的特性

```SQL
BEGIN;
-- 执行DML操作
PREPARE TRANSACTION transaction_id;  -- 第一阶段准备(完成后当前会话可执行其他指令)
COMMIT PREPARED transaction_id;      -- 第二阶段提交(可以其他会话提交)
```

### 2.`VACUUM`回收空间

```
VACUUM [ ( option [, ...] ) ] [ table_and_columns [, ...] ]

其中 option 可以是以下之一：

    FULL [ boolean ]
    FREEZE [ boolean ]
    VERBOSE [ boolean ]
    ANALYZE [ boolean ]
    DISABLE_PAGE_SKIPPING [ boolean ]
    SKIP_LOCKED [ boolean ]
    INDEX_CLEANUP { AUTO | ON | OFF }
    PROCESS_MAIN [ boolean ]
    PROCESS_TOAST [ boolean ]
    TRUNCATE [ boolean ]
    PARALLEL integer
    SKIP_DATABASE_STATS [ boolean ]
    ONLY_DATABASE_STATS [ boolean ]
    BUFFER_USAGE_LIMIT size

并且 table_and_columns 是：

    table_name [ ( column_name [, ...] ) ]
```

### 3.pl/pgSQL

```sql
CREATE FUNCTION somefunc(integer, text) RETURNS integer
AS [ <<label>> ]
[ DECLARE
    declarations ]
BEGIN
    statements
END [ label ];

LANGUAGE plpgsql;
```

### 4.并行查询

### 5.预写式日志(WAL)

类似MySQL中的redolog,用于故障恢复

## 五、数据目录文件布局

|文件名|说明|
|-|-|
|PG_VERSION| 一个包含PostgreSQL主版本号的文件|
|base | 包含每个数据库对应的子目录的子目录|
|current_logfiles | 记录当前被日志收集器写入的日志文件的文件|
|global| 包含集簇范围的表的子目录,比如pg_database|
|pg_commit_ts | 包含事务提交时间戳数据的子目录|
|pg_dynshmem|包含被动态共享内存子系统所使用的文件的子目录|
|pg_logical| 包含用于逻辑复制的状态数据的子目录|
|pg_multixact| 包含多事务(multi-transaction)状态数据的子目录(用于共享的行锁)|
|pg_notify |包含LISTEN/NOTIFY状态数据的子目录|
|pg_replslot|包含复制槽数据的子目录|
|pg_serial |包含已提交的可序列化事务信息的子目录|
|pg_snapshots | 包含导出的快照的子目录|
|pg_stat|包含用于统计子系统的永久文件的子目录|
|pg_stat_tmp|包含用于统计信息子系统的临时文件的子目录|
|pg_subtrans|包含子事务状态数据的子目录|
|pg_tblspc |包含指向表空间的符号链接的子目录|
|pg_twophase|包含用于预备事务状态文件的子目录|
|pg_wal| 包含WAL(预写日志)文件的子目录|
|pg_xact|包含事务提交状态数据的子目录|
|postgresql.auto.conf| 一个用于存储由`ALTER SYSTEM`设置的配置参数的文件|
|postmaster.opts|一个记录服务器最后一次启动时使用的命令行参数的文件|
|postmaster.pid| 一个锁文件,记录着当前的:<br/>1.postmaster进程ID(PID)<br/>2.集簇数据目录路径<br/>3.postmaster启动时间戳<br/>4.端口号<br/>5.Unix域套接字目录路径(Windows上为空)<br/>6.第一个可用的listen_address(IP地址或者*,或者为空表示不在TCP上监听)<br/>7.以及共享内存段ID(服务器关闭后该文件不存在)<br/>8.进程状态|

## 六、特色SQL

### 1.psql

#### (1) shell命令行

|选项|短格式|说明|
|-|-|-|
|--help[=options]|-?|帮助信息|
|--command="*SQL*"|-c "*SQL*"|执行一句SQL后退出|
|--dbname="*DBNAME*"|-d "*DBNAME*"|链接到的数据库|
|-file="*filename*"|-f "*filename*"|从文件中执行SQL后退出|
|--list|-l|显示可用数据库|
|--set="*option*=*value*"<br/>--variable="*option*=*value*"|-v "*option*=*value*"|设置变量|
|--version|-V|显示版本|
|--no-psqlrc|-X|不读启动配置|
|--single-transaction|-1|已一个事务的方式运行,需要搭配-c/-f使用|
|--echo-all|-a|从script中读取sql语句执行时也会打印SQL语句(无论对错)|
|--echo-errors|-a|从script中读取sql语句执行时也会打印SQL语句(只有错误)|

#### (2) 交互模式

|选项|说明|
|-|-|
|\i|从文件中读取SQL执行|
|\d|显示数据库对象(比如表`\dt`、视图`\dv`、序列`\ds`、索引`\di`、用户`\du`，模式`\n`、表空间`\db`、数据类型`\dT`、系统表`\dS`、函数`\df`、权限`\dp`等),`\d+`可以或获取详细信息|
|\conninfo|连接信息|
|\c *database* |连接数据库|
|\l|显示当前数据库,`\l+`为加强模式,多显示大小和所处表空间|
|\timing|切换是否显示执行SQL的运行时间|
|\x|切换列/表格输出|
|\t|表格输出时是否显示字段名|
|\pset *option* *value* |输出格式定义|
|\o *file*|输出内容重定向到某个文件|
|\H|html格式输出|
|\e|使用外部编辑器编辑查询|
|\g|执行前一个查询|
|\set|设置内部变量|
|\echo|结果输出到标准输出|
|\q|退出|

### 2.数据类型

|类型|名称|说明|存储尺寸|
|-|-|-|-|
|整数|smallint|范围区间[-32768,32767]|2字节|
|整数|integer|范围区间[-2147483648,2147483647]|4字节|
|整数|bigint|范围区间[-9223372036854775808,9223372036854775807]|8字节|
|任意精度数字|decimal(*precision*,*scale*)<br/>numeric(*precision*,*scale*)|可以不指定精度<br/>指定精度(precision=总长度，scale=小数点后几位),最高小数点前131072位，以及小数点后16383位<br/>取整会圆到远离0的整数<br/>有三个特殊值['Infinity','-Infinity','NaN']代表无穷大,无穷小,未知|可变|
|浮点数字|real|单精度,精度至少是 6 位小数<br/>支持 SQL 标准表示法float和float(p)用于声明非精确的数字类型,float(1)到float(24)<br/>有三个特殊值['Infinity','-Infinity','NaN']代表无穷大,无穷小,未知|4字节	|
|浮点数字|double precision|双精度,精度至少是 15 位小数<br/>支持 SQL 标准表示法float和float(p)用于声明非精确的数字类型,float(25)到float(53)<br/>有三个特殊值['Infinity','-Infinity','NaN']代表无穷大,无穷小,未知|8字节|
|序数|smallserial|自动增加的整数<br/>smallserial区间[1,32767]|2字节|
|序数|serial|自动增加的整数<br/>serial区间[1,2147483647]|4字节|
|序数|bigserial|自动增加的整数<br/>bigserial区间[1,9223372036854775807]|8字节|
|货币|money|区间[-92233720368547758.08,+92233720368547758.07]|8字节|
|字符|varchar(*n*)|有限可变长字符串,结尾的空格有意义|可变|
|字符|text|无限可变长字符串,结尾的空格有意义|可变|
|字符|char(*n*)|定长字符串,不足时结尾空格填充,pg文档声明char的性能没法快过varchar和text(char更加占用存储空间的导致)|固定长度(4字节加上实际的字串)|
|字符|bpchar[(*n*)]|没有*n*就是无限可变字符串,接近text,不填充空格,同时结尾的空格也没有意义<br/>也可以设置*n*限制长度,此时相当于char(*n*),填充空格|固定长度|
|二进制|bytea|变长二进制串|1或4字节外加真正的二进制串|
|日期/时间|timestamp(*precision*) [ with time zone ]|时间格式"YYYY-MM-DD hh:mm:ss[tz]"<br/>*precision*可以控制秒(ss)的精度,区间[0,6]默认6|8字节|
|日期/时间|date|日期|4字节|
|日期/时间|time(*precision*) [ with time zone ]|时间<br/>*precision*可以控制秒(ss)的精度,区间[0,6]默认6|8字节|
|日期/时间|interval [ filed ] (*precision*) |时间间隔|16字节|
|布尔|boolean|2选1的真/假值,输出时总是为[t|f]<br/>[true|yes|on|1]表示为真<br/>[false|no|off|0]表示为假<br/>null非真非假|1字节|
|枚举|enum|一个静态、值的有序集合<br/>要先使用`CREATE TYPE enum_type_name AS ENUM (value1,value2);`创建类型|一个枚举值在磁盘上占据4个字节|
|几何|point|平面上的点<br/>表示方式: `(x,y)`表示|16字节|
|几何|line|平面上的线<br/>表示方式: `{A,B,C}`表示`Ax+By+C`<br/>还有使用经过的点来表示的方式:<br/>`[(x1,y1),(x2,y2)]`<br/>`((x1,y1),(x2,y2))`<br/>`(x1,y1),(x2,y2)`<br/>`x1,y1,x2,y2`|24字节|
|几何|lseg|平面上的线段<br/>表示方式: `[(x1,y1),(x2,y2)]`表示从`(x1,y1)`开始到`(x2,y2)`为止的线段<br/>其余表示方式：<br/>`((x1,y1),(x2,y2))`<br/>`(x1,y1),(x2,y2)`<br/>`x1,y1,x2,y2`|32字节|
|几何|box|平面上的矩形<br/>表示方式: `((x1,y1),(x2,y2))`表示以从`(x1,y1)`开始到`(x2,y2)`为止为矩形的斜线<br/>其余表示方式：<br/>`(x1,y1),(x2,y2)`<br/>`x1,y1,x2,y2`|32字节|
|几何|path|平面上的路径<br/>表示方式: `[(x1,y1),...,(xn,yn)]`表示从`(x1,y1)`开始到`(xn,yn)`为止的开放路径<br/>`((x1,y1),...,(xn,yn))`表示从`(x1,yn)`开始到`(x2,yn)`为止的封闭路径<br/>其余封闭路径表示方式：<br/>`(x1,y1),...,(xn,yn)`<br/>`(x1,y1,...,xn,yn)`<br/>`x1,y1,xn,yn`|16+16n字节|
|几何|polygon|平面上的多边形<br/>表示方式: `((x1,y1),...,(xn,yn))`表示从`(x1,yn)`开始到`(x2,yn)`为止的多边形<br/>其余多边形表示方式：<br/>`(x1,y1),...,(xn,yn)`<br/>`(x1,y1,...,xn,yn)`<br/>`x1,y1,xn,y`|40+16n字节|
|几何|circle|平面上的圆形<br/>表示方式: `((x,y),r)`表示以`(x,y)`为圆心,`r`为半径的圆及其内部空间<br/>其余封闭路径表示方式：<br/>`((x1,y1),r)`<br/>`(x1,y1),r`<br/>`x,y,r`|24字节|
|网络地址|cidr|IPv4和IPv6网络<br/>cidr更加严格检查IP地址和子网掩码是否规范|7或19字节|
|网络地址|inet|IPv4和IPv6主机以及网络<br/>允许一个子网中的某个地址加子网掩码代表整个网段|7或19字节|
|网络地址|macaddr|MAC地址|6字节|
|网络地址|macaddr8|MAC地址（EUI-64格式）|8字节|
|位串|bit(*n*)|定长,存储短些或者长一些的位串都是错误的<br/>没有长度意味着`bit(1)`|`n`bit|
|位串|bit varying(*n*)|变长,超过`n`更长的串会被拒绝<br/>没有长度意味着没有长度限制|实际长度,最大`n`bit|
|文本搜索|tsvector|用于存储已处理的文本数据,便于快速搜索|可变|
|文本搜索|tsquery|用于表示用户的搜索条件,支持复杂的逻辑运算|可变|
|UUID|uuid|通用唯一标识码<br/>适用于分布式场景<br/>部分算法由于生成无序,导致性能不好<br/>uuidv7使用时间戳+随机无序生成,可以一定程度上有序达到提升性能|16字节|
|XML|xml|有检查结构的text|可变|
|JSON|json|存储json格式的数据<br/>存储时比jsonb<br/>不够严格<br/>约等于text,只是有检查||
|JSON|jsonb|解析并存储json格式的数据<br/>读取时比json更高效<br/>支持索引||

此外,还有一些仅实例内部使用的数据类型

|类型|名称|说明|存储尺寸|
|-|-|-|-|
|字符|"char"|并不等于char(1),因为char(1)占|1字节|
|字符|name|用于存储标识符|64字节|

如果有自定义类型可以使用`CREATE TYPE`创建

### 3.查询

#### (1)jsonb基础查询操作

以下是一些常用的 jsonb 查询操作符和函数，以及它们在SQL中的用法：

|查询场景|符号|PostgreSQL SQL 示例|
|--|--|--|
|提取`key`对应的`value`|`->`|`SELECT data->'key' FROM table;`|
|提取`key`对应的`value`的文本|`->>`|`SELECT data->>'key' FROM table;`|
|提取`key`对应的`value`,可以使用层级路径|`#>`|`SELECT data#>{'key1'，'key2'} FROM table;`|
|提取`key`对应的`value`的文本,可以使用层级路径|`#>>`|`SELECT data#>>{'key1'，'key2'} FROM table;`|
|检查是否存在键|`?`|`SELECT * FROM table WHERE data ? 'key';`|
|检查包含键值对|`@>`|`SELECT * FROM table WHERE data @> '{"key": "value"}';`|

一个简单的查询例子

```sql
CREATE TABLE api (
    jdoc jsonb
);
CREATE INDEX idxgin ON public.api USING gin (jdoc);
CREATE INDEX idxginp ON public.api USING gin (jdoc jsonb_path_ops);
CREATE INDEX idxgintags ON api USING gin ((jdoc -> 'tags'));

INSERT INTO api VALUES ('{"guid": "9c36adc1-7fb5-4d5b-83b4-90356a46061a", "name": "Angela Barton", "tags": ["enim", "aliquip", "qui"], "address": "178 Howard Place, Gulf, Washington, 702", "company": "Magnafone", "latitude": 19.793713, "is_active": true, "longitude": 86.513373, "registered": "2009-11-07T08:53:22 +08:00"}');

INSERT INTO api VALUES ('{"guid": "9c36adc1-7fb5-4d5b-83b4-90356a46062b", "name": "lxw", "tags": ["shangbanzu", "erciyuan", "niuma"], "address": "fuzhou", "company": "nd", "latitude": 80.793713, "is_active": true, "longitude": 99.513373, "registered": "2025-11-20T04:25:00 +08:00"}');

SELECT jdoc->'guid' as guid ,jdoc#>'{tags,1}' as tags,* FROM api WHERE (jdoc->'registered')::text::timestamp >= '2025-11-07T08:53:22 +08:00' and jdoc @> '{"name":"lxw"}';
```


#### (2)时间格式转换

时间格式转unix时间戳(有时区偏移一定要带时区)

```sql
select extract(epoch from  '2025-11-16 00:00:11+08:00'::timestamp with time zone)::decimal as unixtimestamp;
```

unix时间戳转自定义时间格式

```sql
select to_char(to_timestamp(1763222411), 'YYYY-MM-DD HH24:MI:SS') as datetime;
```

## 七、备份

```shell
pg_dump -h 127.0.0.1 -U ${user} -W ${DATABASE} > ${BACKUP}.sql
```