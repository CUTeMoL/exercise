# MongoDB

## 一、启动Mongod（服务）

### 启动

```shell
/usr/local/mongodb/bin/mongod --dbpath=/usr/local/mongodb/data --logpath=/usr/local/mongodb/logs/log.txt --bind_ip 127.0.0.1,192.168.51.43 --auth --fork
```

### 关闭

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

### 数据操作基本格式

```shell
db.<table_name>.action1({条件},{列筛选}).action2({条件})
```

### 插入数据

```shell
db.<table_name>.insert ({col_name1:'value1',col_name2:'value2'}) #插入数据
```

```shell
db.<table_name>.insert ({col_name1: 'value1',col_name2: 'value2',col_name3: {col_name3.1: 'value3.1',col_name3.2: 'value3.2'}}) # 插入2级数据{字典}
```

```shell
db.<table_name>.insert ({col_name1:'value1',col_name2:'value2',col_name3:['value3.1','value3.2','value3.3']}) # 插入2级数据[数组]
```

### 查询数据

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
	$lt  小于	$lte  小于等于	$gt  大于	$gte  大于等于	$ne  不等于
```

```shell
db.<table_name>.find({'col_name1.col_name1.1':'value1.1'}) # 查询2级数据(多维),注意引号
```

```shell
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

