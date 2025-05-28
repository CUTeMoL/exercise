# MongoDB

MongoDB 是一个文档数据库，为简化应用程序的开发与扩展而设计。

数据存储类似json方便程序使用(也因为这个原因可以提供高性能数据持久性)

官方文档:https://www.mongodb.com/zh-cn/docs/v5.0/introduction/

部分概念:

|关键词|说明|
|-|-|
|db|数据库|
|collection|集合,类似表名|

## 一、配置文件

1. 通常位于`/etc/mongod.conf`,如果不是,则需要通过`--config ${file}` 或者 `-f ${file}`来指定配置文件

2. 如果存在拓展指令集(rest,exec),需要--configExpand "指令1,指令2"(最好不使用)
  rest:远程api访问结果来获取配置值
  exec:本地终端shell执行命令的结果来获取配置值

3. 可以不使用配置文件通过参数指定启动方式(不推荐)

4. 使用yaml格式
```yaml
##### mongod.conf
### 仅记录下常见的一些配置,主要还是要参考官方文档

# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/



# 日志相关
systemLog:
   verbosity: <int> # 0-5 默认0,越高越详细
   quiet: <boolean> # true时为安静模式,没有日志输出(不推荐)
   traceAllExceptions: <boolean> # 打印用于调试的详细信息
   syslogFacility: <string> # 将消息记录到系统日志时使用的设施级别,要使用此选项，必须将 systemLog.destination 设置为 syslog
   path: <string> # 日志保存路径
   logAppend: <boolean> # 日志追加模式,即使重启实例,也会在原有的日志后面继续写日志
   logRotate: <string> # 日志轮询,rename添加当前时间戳来重命名现有日志文件,reopen则时重新打开文件,需要另一个程序对日志执行改名
   destination: <string> # 指定 file(自定义的路径)或 syslog(系统日志)
   timeStampFormat: <string> # 日志消息中时间戳的时间格式,iso8601-utc使用UTC,iso8601-local使用本地时区
   # 各种功能的对应日志级别
   component:
      accessControl:
         verbosity: <int>
      command:
         verbosity: <int>


# 数据存储相关
storage:
   dbPath: <string> # 数据库的路径(目录),默认的一般是/var/lib/mongo,/var/lib/mongodb
   journal:
      commitIntervalMs: <num> # mongod 进程允许在两次日志操作之间的最大时间
   directoryPerDB: <boolean> # 为 true 时，MongoDB 使用单独的目录存储每个数据库的数据
   syncPeriodSecs: <int> # MongoDB将数据刷新到数据文件之前可以经过的时间量。默认60,官方文档不推荐修改
   engine: <string> # 默认wiredTiger引擎,inMemory仅在 MongoDB Enterprise 中可用。
   wiredTiger:
      engineConfig:
         cacheSizeGB: <number> # WiredTiger 缓存内存,默认（RAM 大小 - 1 GB）的 50%，或256MB
         journalCompressor: <string> # 指定用于压缩 WiredTiger 日志数据的压缩类型。
         directoryForIndexes: <boolean> # 为 true 时，mongod 将索引和集合存储在数据（即 storage.dbPath）目录下单独的子目录中
         maxCacheOverflowFileSizeGB: <number> #
         zstdCompressionLevel:  <number> #指定使用 zstd 压缩器时的压缩级别。默认6
      collectionConfig:
         blockCompressor: <string> # 指定集合数据的默认压缩类型。none,snappy,zlib,zstd
      indexConfig:
         prefixCompression: <boolean> # 为索引数据启用或禁用前缀压缩。

   # oplogMinRetentionHours: <double>


# 程序运行
processManagement:
  fork: true  # 后台运行
  pidFilePath: /var/run/mongodb/mongod.pid  # pid文件
  timeZoneInfo: /usr/share/zoneinfo # 使用的时区数据库路径(不是指定时区)

# 网络接口连接相关
net:
   port: <int> # 监听端口
   bindIp: <string> # 绑定IP或套接字,localhost,/tmp/mongod.sock,127.0.0.1都可以,ipv6地址需要先启用net.ipv6,使用副本集/分片时地址很重要,官方文档推荐使用DNS解析
   bindIpAll: <boolean> # true时绑定到所有IP地址
   maxIncomingConnections: <int> # 最大并行连接数
   wireObjectCheck: <boolean> # 写入数据库时验证所有请求
   ipv6: <boolean> # 是否启用ipv6
   # 套接字相关设置
   unixDomainSocket:
      enabled: <boolean> # 启用
      pathPrefix: <string> # 套接字路径默认/tmp
      filePermissions: <int> # 权限,默认0700
   # ssl相关不详细记了,分的很细,有集群用,也有客户端用的,用到时直接看官方文档
   tls:
      certificateSelector: <string>
      clusterCertificateSelector: <string>
      mode: <string>
      certificateKeyFile: <string>
      certificateKeyFilePassword: <string>
      clusterFile: <string>
      clusterPassword: <string>
      CAFile: <string>
      clusterCAFile: <string>
      clusterAuthX509:
        attributes: <string>
        extensionValue: <string>
      CRLFile: <string>
      allowConnectionsWithoutCertificates: <boolean>
      allowInvalidCertificates: <boolean>
      allowInvalidHostnames: <boolean>
      disabledProtocols: <string>
      FIPSMode: <boolean>
      logVersions: <string>
   compression:
      compressors: <string>

# 安全(其他如Kerberos、sasl、ldap等认证方式用到时看官方文档)
security:
   keyFile: <string> # 密钥文件的路径，该文件存储 MongoDB 实例用于在分片集群或副本集中相互验证的共享密钥
   clusterAuthMode: <string> # 集群身份验证时使用的身份验证方式
   authorization: <string> # enabled时用户只能访问已获得授权的数据库资源和操作。disabled时用户可以访问任何数据库并执行任何操作。
   transitionToAuth: <boolean> # 开启认证但不强制要求,属于过渡的选项
   javascriptEnabled:  <boolean> # 启用javascript
   redactClientLogData: <boolean> # 客户端敏感信息输出到日志而不是保存于数据库中
   clusterIpSourceAllowlist:
     - <string> # 集群模式的的允许IP,5.2之后可以使用 setParameter 来在线配置

# 指定应该进行性能分析的操作
operationProfiling:
   mode: <string> # off不分析,slowOp分析器会收集耗时超过 slowms 值的操作的数据,all所有
   slowOpThresholdMs: <int> # 慢速操作时间阈值,设置为 0 时，记录速率由 slowOpSampleRate 确定
   slowOpSampleRate: <double> # 应分析或记录的慢速操作的比例
   filter: <string> # 用于控制要分析和记录的操作,设置 filter 后slowOpThresholdMs和slowOpSampleRate不生效

# 复制
replication:
   oplogSizeMB: <int> # 未压缩时的大小,默认最大可用空间的5%
   replSetName: <string> # 所属副本集的名称,副本集中的所有主机必须具有相同的设置名称
   enableMajorityReadConcern: <boolean>

# 分片
sharding:
   clusterRole: <string> # 实例在分片集群中的角色,configsvr:配置服务器,shardsvr分片
   archiveMovedChunks: <boolean> # true:数据段迁移过程中，分片不会保存从该分片中迁移的文档

# mongos 专用选项
replication:
   localPingThresholdMs: <int> # 副本集之间确认,默认15毫秒
sharding:
   configDB: <string>
```


## 二、启动Mongod

### 1.启动

#### (1)命令行启动:无配置文件的启动方式

```shell
/usr/local/mongodb/bin/mongod --dbpath=/usr/local/mongodb/data --logpath=/usr/local/mongodb/logs/log.txt --bind_ip 127.0.0.1,192.168.51.43 --auth --fork
```

#### (2)命令行启动:有配置文件的启动方式

```shell
/usr/local/mongodb/bin/mongod -f /etc/mongod.conf
```

#### (3)服务方式启动(推荐)

`/usr/lib/systemd/system/mongod.service`存在时

```shell
# 内容参考
[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target

[Service]
User=mongod
Group=mongod
Environment="OPTIONS=-f /usr/local/mongodb/etc/mongod.conf"
EnvironmentFile=-/etc/sysconfig/mongod
ExecStart=/usr/bin/mongod $OPTIONS
ExecStartPre=/usr/bin/mkdir -p /usr/local/mongodb/data
ExecStartPre=/usr/bin/chown mongod:mongod usr/local/mongodb/data
ExecStartPre=/usr/bin/chmod 0755 usr/local/mongodb/data
PermissionsStartOnly=true
PIDFile=/usr/local/mongodb/data/mongod.pid
Type=forking
# file size
LimitFSIZE=infinity
# cpu time
LimitCPU=infinity
# virtual memory size
LimitAS=infinity
# open files
LimitNOFILE=64000
# processes/threads
LimitNPROC=64000
# locked memory
LimitMEMLOCK=infinity
# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false
# Recommended limits for mongod as specified in
# https://docs.mongodb.com/manual/reference/ulimit/#recommended-ulimit-settings

[Install]
WantedBy=multi-user.target

```


```shell
systemctl daemon-reload
systemctl start mongod
```

### 2.关闭

```shell
/usr/local/mongodb/bin/mongod --dbpath=/usr/local/mongodb/data --shutdown
```

或在客户端里

```shell
use admin 
db.shutdownServer()
```

## 二、Mongocli

### 启动mongo命令行管理终端

```shell
/usr/local/mongosh/bin/mongo --host 192.168.51.43 -u root -p
--host # 地址
--port # 指定端口,默认27017
-u # 用户
-p # 密码
--eval # 执行命令
--quiet # 静默，不输出多余信息
```

### 管理命令

```shell
help ： 使用帮助
db.help() : 数据库使用帮助
show dbs  : 展示所有数据库
use <db_name> : 切换数据库，若数据库不存在则创建数据库
show collections  : 展示所有表
db.getName()    或  db   : 获取当前库名字的命令
db.stats() : 获取当前库的状态
```

## 三、集合数据操作

### 1.数据操作基本格式

类似json,但实际有一定的顺序

```json
{
   key_str: "value",
   key_list: ["value","value"],
   key_dict: {"sub_key": "sub_value"}
}
```

```javascript
db.collection.action1({条件},{列筛选}).action2({条件})
```

#### 2.插入数据

```python
# 插入数据支持嵌套
db.collection.insert(
    {
        'col_name1': 'value1',
        'col_name2': 'value2',
        'col_name3': {
            'col_name3.1': 'value3.1',
            'col_name3.2': 'value3.2'
         },
        'col_name4': ['value4.1','value4.2','value4.3']
    }
)
```
```shell

# 多行插入
db.collection.insertMany(
   [
      {'col_name1': 'value1', 'col_name2': "value2" },
      {'col_name1': 'value3', 'col_name2': "value4" }
   ]
);
```


#### 3.查询数据

官方文档链接:https://www.mongodb.com/zh-cn/docs/v6.0/reference/method/db.collection.find/#mongodb-method-db.collection.find

```mongoshell
db.collection.find(query, projection, options)
```

|参数|说明|格式|
|-|-|-|
|query|查询条件|json|
|projection|指定显示的字段|json|
|options|指定查询的附加选|json|

(1)query

用于设置筛选条件,以下为常用运算符

|逻辑运算符|说明|
|-|-|
|$in|查询某字段的值是否在指定的列表中存在|
|$nin|不匹配数组中指定的任何值。|
|$and|使用逻辑 AND 连接查询子句将返回与两个子句的条件匹配的所有文档。|
|,|相当于AND|
|$not|反转查询表达式的效果，并返回与查询表达式不匹配的文档。|
|$nor|使用逻辑 NOR 的联接查询子句会返回无法匹配这两个子句的所有文档。|
|$or|使用逻辑 OR 连接多个查询子句会返回符合任一子句条件的所有文档。|
|$all|查询某列表中的元素是否在指定的列表中存在|


|关系运算符|说明|
|-|-|
|$lt|小于|
|$lte|小于等于|
|$gt|大于|
|$ne|不等于|
|$eq|等于|


|特殊运算符|说明|
|-|-|
|$exists|是否存在字段|
|$type|字段类型|


```shell
db.<table_name>.find({col_name1:'value1',col_name2:'value2'}) # 查询数据，括号中可填条件，也可以不填
```

```shell
db.<table_name>.find({col_name1:'value1',col_name2:'value2'}{col_name1:1,col_name2:0})  # 查询数据，第一个花括号{条件}，第二个花括号{筛选是否显示，1显示，0不显示}，不输入条件的话第一个花括号可为空{}
```

```shell
db.<table_name>.findOne({col_name1:'value1',col_name2:'value2'}) : 查询数据，只显示第一条数据
```

```shell
db.<table_name>.find({col_name1:{'$lt':value1}}) # 查询数据，通过数值的范围查询 
	# $lt|小于	$lte|小于等于	$gt|大于	$gte|大于等于	$ne|不等于
   如果是查询时间范围使用$date表示时间
   {
      "created_at":{
         "$gte": {"$date": "2025-01-01T00:00:00Z"},
         "$lte": {"$date": "2025-12-31T00:00:00Z"}
   }
```

```shell
db.<table_name>.find({'col_name1.col_name1.1':'value1.1'}) # 查询2级数据(多维),注意引号
```

```python
db.<table_name>.find({col_name1:{'$all':['value1.1','value1.2']}}) : 查询2级数据(数组)//在[]中的条件都存在的


```

​	例如：`db.information.find({food:{'$all':['brief','water','fish']}})`


```shell
db.<table_name>.find({'$or':[{条件1},{条件2}]}) # 查询符合条件1或条件2的数据
```

​	例如：`db.information.find({'$or':[{name:'lxw'},{age:27}]})`

```shell
db.<table_name>.find({条件1，条件2}).count() # 统计次数
```

```shell
db.<table_name>.find({条件1，条件2}).skip(3).limit(2) # 查询符合条件1或条件2的数据，跳过3条，显示2条
```

```shell
db.<table_name>.find({条件1，条件2}).sort({条件3}) # 查询符合条件1或条件2的数据，按条件3进行排序
```

​	例如：`db.goods.find().sort({price:-1}) `     #-1为倒序（从大到小）

  一个复杂的示范:
```python
# 查询 id为186或者满足一下条件的记录,最后按balance从大到小输出名字balance、is_vip
# 条件1: 兴趣中存在游戏、音乐,且不存在电影、跑步
# 条件2: 年龄小于80岁
# 条件3: 地址在杭州
# 条件4: 记录创建于2025-01-01到2025-02-30之间
# 先按is_vip为false在前,最后按balance从大到小
# 输出名字balance、is_vip
db.users.find(
   {
      "$or": [
         {
            "$and": [
               {
                  "interests": {
                     "$all": ["游戏","音乐"]
                  }
               },
               {
                  "interests": {
                     "$nin": ["电影","跑步"]
                  }
               },
               {
                  "age" : {"$lt": 80}
               },
               {
                  "address.city": "杭州"
               },
               {
                  "created_at":{
                     "$gte": {"$date": "2025-01-01T00:00:00Z"},
                     "$lte": {"$date": "2025-12-31T00:00:00Z"}
                  }
               }
            ]
         },
         {
            "_id": 186
         }
      ]
   },
   {"_id":0,"name":1,"balance":1,"is_vip":1,"interests":1}
).sort({"is_vip":1,"balance":-1})

```


### 更新数据

```shell
db.<table_name>.updateOne({条件1，条件2},{'$set':条件3}) # 查询符合条件1或条件2的1条数据，修改条件3（仅1条）
```

```shell
db.<table_name>.updateMany({条件1，条件2},{'$set':条件3}) : 查询符合条件1或条件2的所有数据，修改条件3（多条）
```

```shell
db.<table_name>.update({条件1，条件2},{条件3})  # 查询符合条件1或条件2的数据，修改条件3并清空其他字段
```

### 删除数据

```shell
db.<table_name>.deleteOne({条件1，条件2}) # 查询符合条件1或条件2的数据，删除匹配到的一条
```

```shell
db.<table_name>.deleteMany({条件1，条件2}) # 查询符合条件1或条件2的数据，删除匹配到的所有
```

```shell
db.<table_name>.remove({条件1，条件2},justOne:1) # 查询符合条件1或条件2的数据，删除匹配到的一条
```

```shell
db.<table_name>.update({条件1，条件2},{'$unset':{col_name1:0}})  # 查询符合条件1或条件2的数据，删除col_name1这个字段
```

### 用户管理

```shell
use admin
db.createUser({user:"root",pwd:"123456",roles:["root"]}) # 用户名root密码123456角色root（超级管理员,全数据库读写）
```

roles: ["root"]可替换为：

```shell
roles[	
    {role:"read",db:"reporting"}		# 对reporting这个库拥有只读权限
    {role:"read",db:"products"}		# 对products这个库拥有只读权限
    {role:"readWrite",db:"accounts"}	# 对accounts这个库拥有读写权限
]
```
创造一个普通读写用户

```shell
db.createUser({user:"lxw",pwd:"123456",roles:[{role:"readWrite",db:'db_name'}]})
```

### 用户登录

```shell
use admin
db.auth('root','123456')
```

## 三、mongotools

### 备份还原

仅数据导入导出为JSON

```shell
/usr/local/mongotools/bin/mongoexport -d lxw_test_db -c information_collection -u root -p123456 --authenticationDatabase=admin -o ./mongo_bak_lxw_test_information.json
-d   # 指定数据库
-c   # 指定集合
--authenticationDatabase   # 认证的库名
-o   # 输出到的路径
```

```shell
/usr/local/mongotools/bin/mongoimport -uroot -p123456 --authenticationDatabase=admin -d lxw_test_db -c information_collection ./mongo_bak_lxw_test_information.json
```

二进制导出导入

```shell
/usr/local/mongotools/bin/mongodump -d lxw_test -c-uroot -p123456 --authentionDatabase=admin -o ./dump
/usr/local/mongotools/bin/mongorestore -d lxw_test -c-uroot -p123456 --authentionDatabase=admin --dir=./dump
```

### 性能查看

```shell
/usr/local/mongotools/bin/mongotop -uroot -p123456 --authenticationDatabase=admin
/usr/local/mongotools/bin/mongostat -uroot -p123456 --authenticationDatabase=admin
/usr/local/mongotools/bin/db.hostInfo()
```

