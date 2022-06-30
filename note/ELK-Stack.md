# ELK Stack

Logstash:开源的服务器数据处理管道，能够同时从多个来源采集数据、转换数据，然后将数据存储到数据库中。

Elasticsearch:搜索、分析和存储数据

Kibana:数据可视化

Beats:轻量级采集器的平台，从边缘机器向Logstash和Elasticsearch发送数据

Filebeat:轻量型日志采集器

流程：

|file     |filebeat                      | Logstash             |         Elasticsearch     |             Kibana|
|-|-|-|-|-|
|file or db|采集|采集、过滤|存储|可视化|

databases >> Input > Filter > Output >> 搜索、分析和存储数据 >> 数据可视化

## 一、Elasticsearch

### 1.概念

Node:运行单个实例的服务器

Cluster:一个或多个节点构成的集群

Index:索引是多个文档的集合相当于database

Type:一个Index可以定义一种或者多种类型，将Document逻辑分组

Document:Index里的每一条记录，若干文档构建一个Index

Field:ES存储的最小单元

Shards:ES将Index分为若干份，每一份就是一个分片

Replicas:Index的一份或多份副本

### 2.部署

(1)

```shell
yum install java-1.8.0-openjdk -y
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
echo "[elastic-7.0]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
" > /etc/yum.repos.d/elastic.repo
yum install elasticsearch -y
```

(2) 修改/etc/hosts

(3)

/etc/elasticsearch/elasticsearch.yml

```yaml
# 配置集群的名字
cluster.name: elk-cluster
# 配置当前节点的名字
node.name: es1
# 存取数据的目录
path.data: /var/lib/elasticsearch
# 修改为当前节点的IP地址
network.host: 192.168.1.102
# 把端口启用
http.port: 9200
# 把需要加入集群的节点写进来discovery.seed_hosts
discovery.zen.ping.unicast.hosts: ["192.168.1.102", "192.168.1.103", "192.168.1.104"]
discovery.seed_hosts: ["192.168.1.102", "192.168.1.103", "192.168.1.104"]
# 设置最小的master节点数,一般节点数为奇数，防止脑裂
discovery.zen.minimum_master_nodes: 2
cluster.initial_master_nodes: ["es1", "es2", "es3"]
```

(4)

/etc/elasticsearch/jvm.options

```shell
# 配置堆大小服务器内存的一半   Xms（最小堆大小）和Xmx（最大堆大小）
-Xms4g
-Xmx4g
```

(5)

/usr/lib/systemd/system/elasticsearch.service

```shell
ExecStart=/bin/bash -c "/usr/share/elasticsearch/bin/systemd-entrypoint -p ${PID_DIR}/elasticsearch.pid --quiet &"
```

(6)

```shell
systemctl daemon-reload
systemctl start elasticsearch.service
```

(7)

```shell
curl -X GET "192.168.1.102:9200/_cat/health?v"
# green代表健康
# yellow警告
# red危险
curl -X GET "192.168.1.102:9200/_cat/nodes?v" # 查看节点 heap.percent 内存占用百分比
```

(8)elasticsearch-head部署

```shell
wget https://nodejs.org/dist/v16.14.0/node-v16.14.0-linux-x64.tar.xz -O /usr/local/node.tar.xz
cd /usr/local
tar -xJvf node.tar.xz 
mv node-v16.14.0-linux-x64 node
echo '
PATH=/usr/local/node/bin:$PATH
export PATH
' >>/etc/profile
cd /usr/local
yum install git -y
git clone git://github.com/mobz/elasticsearch-head.git
cd elasticsearch-head/
npm install
```

Gruntfile.js

```json
options: {
                                        port: 9100,
                                        base: '.',
                                        keepalive: true,
                                        hostname: '*'
}
```

/etc/elasticsearch/elasticsearch.yml

```yaml
http.cors.enabled: true
http.cors.allow-origin: "*"
```

```shell
systemctl restart elasticsearch
```

```shell
npm run start &
```



### 3.数据操作

```shell
curl -X<verb> 'protocol://<host>:<port>/<path>?<query_string>' -d '<body>'
-X   # 指定动作
verb   # HTTP方法GET,POST,PUT,HEAD,DELETE
host   # ES的节点
port   # 端口
path   # 索引路径(数据库)
query_string   # 可选的查询请求参数。例如?pretty参数将格式化输出JSON数据
-d   # 里面放一个JSON格式的请求主体
body   # 自己写的JSON格式的请求主体
```

列出所有索引

```shell
curl -X GET "192.168.51.51:9200/_cat/indices?v"
health   健康状态
status   
index   索引名称
uuid
pri   
rep
docs.count   索引的文档数量
docs.deleted   
store.size   存储的数量
pri.store.size   主分片存储的数量
```

创建索引

```shell
curl -X PUT "192.168.51.51:9200/test_2022-3-7"
```

往索引中创建数据

```shell
curl -X PUT "192.168.51.51:9200/test_2022-3-7/_doc/1?pretty" -H 'Content-Type: application/json' -d '{
    "name": "Lin Xuewei",
    "age": 26
}'
```

查询数据

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7/_doc/1?pretty"
```

```shell
curl -X GET "192.168.51.51:9200/bank/_search?q=*&sort=account_number:asc&pretty"
_search   #查询数据的接口
q=*   #代表数据库中的所有数据
&   #和
sort   #排序，此处是根据account_number排序 asc是升序
```

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7_search?pretty" -H 'Content-Type: application/json' -d '{
    "query": { "match_all": {} },
    "sort": [ 
        { "age": {"order": "desc"} }
    ],
    "size": 1,
    "_source":["age","name"]
}'
size  #截至from后多少位
from   #起始位置第几个
_source   #只显示指定字段
```

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7/_search?pretty" -H 'Content-Type: application/json' -d '{
    "query": { "match": {"name": "lxw linxuewei"} }
}'
match   # 根据某个字段查询或字段中包含的单词，不区分大小写，用空格分割代表或
```

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7/_search?pretty" -H 'Content-Type: application/json' -d '{
    "query": { 
        "bool": {
            "must": [
                {"match":{"age":27}},
                {"match":{"name":"linxw"}}
            ]
        }
    }
}'
bool   # 多条件
must   # 相当于and
```

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7/_search?pretty" -H 'Content-Type: application/json' -d '{
    "query": { 
        "bool": {
            "should": [
                {"match":{"age":27}},
                {"match":{"age":26}}
            ]
        }
    }
}'
should   或
```

```shell
curl -X GET "192.168.51.51:9200/test_2022-3-7/_search?pretty" -H 'Content-Type: application/json' -d '{
    "query": { 
        "bool": {
            "must": { "match_all": {} },
            "filter":{
               "range":{
                   "age":{
                        "gte":25,
                         "lte":30 
                    }
                }
            }
        }
    }
}'
filter   # 过滤
range   # 范围
gte   # 大于等于
lte    # 小于等于
```

删除doc数据

```shell
curl -X DELETE "192.168.51.51:9200/test_2022-3-7/_doc/1?pretty"
```

修改数据(同创建数据)

```shell
curl -X PUT "192.168.51.51:9200/test_2022-3-7/_doc/1?pretty" -H 'Content-Type: application/json' -d '{
    "name": "LXW"
}'
```

POST也可以

```shell
curl -X POST "192.168.51.51:9200/test_2022-3-7/_doc/1?pretty" -H 'Content-Type: application/json' -d '{
    "name": "LXW"
}'
```

导入数据JSON

```shell
curl -H 'Content-Type: application/json' -X POST "192.168.51.51:9200/bank/_doc/_bulk?pretty&refresh" --data-binary "@accounts.json"
```

官方的范例JSON

```shell
wget https://raw.githubusercontent.com/elasticsearch/master/docs/src/test/resources/accounts.json
```

## 二、logstash

### 1.部署

```shell
echo "[elastic-7.0]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md" > /etc/yum.repos.d/elastic.repo
yum makecache
yum install logstash -y
```

### 2.logstash条件判断

```shell
比较操作符
==	!=	<	>	<=	>=

=~匹配正则	
!~不匹配正则

in 包含		
not in 不包含

布尔操作符
and	    or	nand非与		xor非或

一元运算符
!取反	()复合表达式	!()复合取反
```

### 3.input插件

stdin标准输入

```shell
# stdin示例：
input {
    stdin {

    }
}
filter {

}
output {
    stdout {
        codec => rubydebug
    }
}
```

file从文件中获取

```shell
input {
    file {
        path => "/var/log/messages"
        tags => "123"
        type => "syslog"
        start_position => "beginning"
    }
}
filter {

}
output {
    stdout {
        codec => rubydebug
    }
}
```

tcp网络端口获取

```shell
input {
    tcp {
        port => 12345
        type => "nc"
    }
}
filter {

}
output {
    stdout {
        codec => rubydebug
    }
}
```

beat

```shell
input {
    beats {
        port => 5044
    }
}
filter {

}
output {
    stdout {
        codec => rubydebug
    }
}
```

综合示例

```shell
input {
    file {
        path => "/var/log/messages"
        tags => ["system_log","sys_log"]
        type => "syslog"
        start_position => "beginning"
    }
    tcp {
        port => 12345
        type => "nc"
    }
}
filter {

}
output {
    if [type] == "syslog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "syslog-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "nc" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "nc-%{+YYYY.MM.dd}"
        }
    }
}
```

### 4.Codec plugins

用于解码编码

rubydebug:默认

json:

```shell
codec => json {
        charset => ["UTF-8"]
}
```

测试用例

```shell
  {"IP": "150.150.168.93","method":"GET","bytes":"1.11"}
```

Multline:用于多行

```
input {
    stdin {
        codec => multiline {
            pattern => "^\s"
            what => "previous"
        }
    }
}
```

匹配到任何以字符串开头的作为一行的起始，没匹配到字符串的视为上一行的延续（previous），也就是\n不再是行的标志了，^\s适用于JAVA堆栈异常

pattern   正则匹配

what   有两个值 previous合并到上一行 next合并到下一行



```shell
input {
    stdin {
        codec => multiline {
            pattern => "^\["
            negate => true
            what => "previous"
        }
    }
}
```

匹配以[开头的，适合匹配java日志

### 5.filter插件

json

```shell
input {
    stdin {
    }
}
filter {
    json {
        source => "message"
        target => "content"
    }
}
output {
    stdout {
        codec => rubydebug
    }
}
#source指定消息源
#targe指定新的字段
```

kv:

kv为key=value定义输入的格式为key:value

```shell
input {
        stdin {
        }
}
filter {
  kv {
     field_split => "&?"
  }
}
output {
        stdout {
        }
}
# field_split 为定义分隔符
# 文件中的列以&或?进行分隔
```

```shell
input {
        stdin {
        }
}
filter {
  kv {
     field_split_pattern => ":+"
  }
}
output {
        stdout {
        }
}
# field_split_pattern匹配正则
```

grok:

```shell
input {
    stdin {
    }
}
filter {
    grok {
        match => {
            "message" => "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration}"
        }
    }
    geoip {
        source => "client"
        database => "/opt/GeoLite2-City.mmdb"
    }
}
output {
	stdout {
	}
}
```

示例：

```shell
3.72.85.86 GET /index.html 15284 0.0044 
```

```shell
match 匹配格式 %{key1: key2}
	KEY1为需要调用的模块
	KEY2为自定义字段名
	每个match对象空格隔开

input {
    stdin {
    }
}
filter {
    grok {
        patterns_dir => "/opt/patterns"
        match => [
        "message", "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration} %{ID:id}",
        "message", "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration} %{TAG:tag}"
        ]
    }
}
  geoip {
      source => "client"
      database => "/opt/GeoLite2-City.mmdb"
  }
}
output {
        stdout {
        }
}
#match  => [ ] 代表多选
#每一条message后面要加逗号,除非最后一条
#Id是自定义模块  ID [0-9A-Z]{10,11}
#TAG:tag也是自定义模块  TAG SYSLOG
#overwrite 重写
#pattern_dir自定义正则的路径
```

/opt/patterns/grok-patterns.txt

```shell
USERNAME [a-zA-Z0-9._-]+
USER %{USERNAME}
EMAILLOCALPART [a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~]{1,64}(?:\.[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~]{1,62}){0,63}
EMAILADDRESS %{EMAILLOCALPART}@%{HOSTNAME}
INT (?:[+-]?(?:[0-9]+))
BASE10NUM (?<![0-9.+-])(?>[+-]?(?:(?:[0-9]+(?:\.[0-9]+)?)|(?:\.[0-9]+)))
NUMBER (?:%{BASE10NUM})
BASE16NUM (?<![0-9A-Fa-f])(?:[+-]?(?:0x)?(?:[0-9A-Fa-f]+))
BASE16FLOAT \b(?<![0-9A-Fa-f.])(?:[+-]?(?:0x)?(?:(?:[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?)|(?:\.[0-9A-Fa-f]+)))\b

POSINT \b(?:[1-9][0-9]*)\b
NONNEGINT \b(?:[0-9]+)\b
WORD \b\w+\b
NOTSPACE \S+
SPACE \s*
DATA .*?
GREEDYDATA .*
QUOTEDSTRING (?>(?<!\\)(?>"(?>\\.|[^\\"]+)+"|""|(?>'(?>\\.|[^\\']+)+')|''|(?>`(?>\\.|[^\\`]+)+`)|``))
UUID [A-Fa-f0-9]{8}-(?:[A-Fa-f0-9]{4}-){3}[A-Fa-f0-9]{12}
# URN, allowing use of RFC 2141 section 2.3 reserved characters
URN urn:[0-9A-Za-z][0-9A-Za-z-]{0,31}:(?:%[0-9a-fA-F]{2}|[0-9A-Za-z()+,.:=@;$_!*'/?#-])+

# Networking
MAC (?:%{CISCOMAC}|%{WINDOWSMAC}|%{COMMONMAC})
CISCOMAC (?:(?:[A-Fa-f0-9]{4}\.){2}[A-Fa-f0-9]{4})
WINDOWSMAC (?:(?:[A-Fa-f0-9]{2}-){5}[A-Fa-f0-9]{2})
COMMONMAC (?:(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2})
IPV6 ((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?
IPV4 (?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9])
IP (?:%{IPV6}|%{IPV4})
HOSTNAME \b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)
IPORHOST (?:%{IP}|%{HOSTNAME})
HOSTPORT %{IPORHOST}:%{POSINT}

# paths (only absolute paths are matched)
PATH (?:%{UNIXPATH}|%{WINPATH})
UNIXPATH (/[[[:alnum:]]_%!$@:.,+~-]*)+
TTY (?:/dev/(pts|tty([pq])?)(\w+)?/?(?:[0-9]+))
WINPATH (?>[A-Za-z]+:|\\)(?:\\[^\\?*]*)+
URIPROTO [A-Za-z]([A-Za-z0-9+\-.]+)+
URIHOST %{IPORHOST}(?::%{POSINT})?
# uripath comes loosely from RFC1738, but mostly from what Firefox doesn't turn into %XX
URIPATH (?:/[A-Za-z0-9$.+!*'(){},~:;=@#%&_\-]*)+
URIQUERY [A-Za-z0-9$.+!*'|(){},~@#%&/=:;_?\-\[\]<>]*
# deprecated (kept due compatibility):
URIPARAM \?%{URIQUERY}
URIPATHPARAM %{URIPATH}(?:\?%{URIQUERY})?
URI %{URIPROTO}://(?:%{USER}(?::[^@]*)?@)?(?:%{URIHOST})?(?:%{URIPATH}(?:\?%{URIQUERY})?)?

# Months: January, Feb, 3, 03, 12, December
MONTH \b(?:[Jj]an(?:uary|uar)?|[Ff]eb(?:ruary|ruar)?|[Mm](?:a|ä)?r(?:ch|z)?|[Aa]pr(?:il)?|[Mm]a(?:y|i)?|[Jj]un(?:e|i)?|[Jj]ul(?:y|i)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo](?:c|k)?t(?:ober)?|[Nn]ov(?:ember)?|[Dd]e(?:c|z)(?:ember)?)\b
MONTHNUM (?:0?[1-9]|1[0-2])
MONTHNUM2 (?:0[1-9]|1[0-2])
MONTHDAY (?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])

# Days: Monday, Tue, Thu, etc...
DAY (?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)

# Years?
YEAR (?>\d\d){1,2}
HOUR (?:2[0123]|[01]?[0-9])
MINUTE (?:[0-5][0-9])
# '60' is a leap second in most time standards and thus is valid.
SECOND (?:(?:[0-5]?[0-9]|60)(?:[:.,][0-9]+)?)
TIME (?!<[0-9])%{HOUR}:%{MINUTE}(?::%{SECOND})(?![0-9])
# datestamp is YYYY/MM/DD-HH:MM:SS.UUUU (or something like it)
DATE_US %{MONTHNUM}[/-]%{MONTHDAY}[/-]%{YEAR}
DATE_EU %{MONTHDAY}[./-]%{MONTHNUM}[./-]%{YEAR}
ISO8601_TIMEZONE (?:Z|[+-]%{HOUR}(?::?%{MINUTE}))
ISO8601_SECOND %{SECOND}
TIMESTAMP_ISO8601 %{YEAR}-%{MONTHNUM}-%{MONTHDAY}[T ]%{HOUR}:?%{MINUTE}(?::?%{SECOND})?%{ISO8601_TIMEZONE}?
DATE %{DATE_US}|%{DATE_EU}
DATESTAMP %{DATE}[- ]%{TIME}
TZ (?:[APMCE][SD]T|UTC)
DATESTAMP_RFC822 %{DAY} %{MONTH} %{MONTHDAY} %{YEAR} %{TIME} %{TZ}
DATESTAMP_RFC2822 %{DAY}, %{MONTHDAY} %{MONTH} %{YEAR} %{TIME} %{ISO8601_TIMEZONE}
DATESTAMP_OTHER %{DAY} %{MONTH} %{MONTHDAY} %{TIME} %{TZ} %{YEAR}
DATESTAMP_EVENTLOG %{YEAR}%{MONTHNUM2}%{MONTHDAY}%{HOUR}%{MINUTE}%{SECOND}

# Syslog Dates: Month Day HH:MM:SS
SYSLOGTIMESTAMP %{MONTH} +%{MONTHDAY} %{TIME}
PROG [\x21-\x5a\x5c\x5e-\x7e]+
SYSLOGPROG %{PROG:[process][name]}(?:\[%{POSINT:[process][pid]:int}\])?
SYSLOGHOST %{IPORHOST}
SYSLOGFACILITY <%{NONNEGINT:[log][syslog][facility][code]:int}.%{NONNEGINT:[log][syslog][priority]:int}>
HTTPDATE %{MONTHDAY}/%{MONTH}/%{YEAR}:%{TIME} %{INT}

# Shortcuts
QS %{QUOTEDSTRING}

# Log formats
SYSLOGBASE %{SYSLOGTIMESTAMP:timestamp} (?:%{SYSLOGFACILITY} )?%{SYSLOGHOST:[host][hostname]} %{SYSLOGPROG}:

# Log Levels
LOGLEVEL ([Aa]lert|ALERT|[Tt]race|TRACE|[Dd]ebug|DEBUG|[Nn]otice|NOTICE|[Ii]nfo?(?:rmation)?|INFO?(?:RMATION)?|[Ww]arn?(?:ing)?|WARN?(?:ING)?|[Ee]rr?(?:or)?|ERR?(?:OR)?|[Cc]rit?(?:ical)?|CRIT?(?:ICAL)?|[Ff]atal|FATAL|[Ss]evere|SEVERE|EMERG(?:ENCY)?|[Ee]merg(?:ency)?)
```

geoip:

先下载地理位置数据库

```shell
input {
        stdin {
        }
}
filter {
  grok {
    match => {
      "message" => "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration}"
    }
  }
  geoip {
      source => "client"
      database => "/opt/GeoLite2-City.mmdb"
  }
}
output {
        stdout {
        }
}
#source 定义来源前面定义的字段
#database 指定数据库的位置
```

date重新定义logstash的采集时间

```shell
date {
    locale => "en"
    match => ["time_local","dd/MMM/yyyy:HH:mm:ss Z"]
}
```

mutate可以替换字段

```shell
mutate {
    convert => ["[geoip][coordinates]", "float"]
}
```

### 6.output输出插件

```shell
output {
    stdout {
        }
    if [type] == "syslog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "syslog-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "nc" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "nc-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "input" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "input-%{+YYYY.MM.dd}"
        }
    }
}
```

7.使用

```shell
/usr/share/logstash/bin/logstash
-t   检测配置文件
-f   指定配置文件的位置
--log.level fatal|error|warn|info|debug|trace  指定日志的级别
-r   动态加载配置文件(限同类型)
```

## 三、kibana使用

### 1.安装

kibana同样需要node，安装NODE

```shell
yum install kibana -y
```

 /etc/kibana/kibana.yml

```yaml
elasticsearch.hosts: ["http://192.168.51.51:9200","http://192.168.51.52:9200","http://192.168.51.53:9200"]
server.port: 5601
server.host: "0.0.0.0"
```

```shell
systemctl start kibana
```

http://192.168.51.54:5601/

management > stack management > index patterns > create index pattern

填好 name Timestamp field，就能在discover查看了

## 四、filebeat

### 1.安装

```
yum install filebeat -y
```

### 2.采集

多行模式

```yaml
  # Multiline options
  
  # 多行模式：匹配正则
  multiline.type: pattern

  # 匹配的规则
  multiline.pattern: ^\[
  
  #定义此设置正向true/反向false
  multiline.negate: true
  
  #after=previous|before=next
  multiline.match: after
```

  规则↓

| negate | match  | pattern: ^b | 注释                                  |
| ------ | ------ | ----------- | ------------------------------------- |
| false  | after  | abb  cbb    | 匹配到b开头的追加到非b开头的后面      |
| false  | before | bba  bbc    | 直到匹配到非b开头的才结束一条消息     |
| true   | after  | bac  bde    | 匹配到非b开头的都要追加到前一行的后面 |
| true   | before | acb  deb    | 直到匹配到b开头的才结束一条消息       |

常用

```yaml
  #JAVA堆载↓
  multiline.type: pattern
  multiline.pattern: '^[[:space:]]+(at|\.{3})[[:space:]]+\b|^Caused by:'
  multiline.negate: false
  multiline.match: after

  #事件↓（多个事件同时是不行的）
  multiline.type: pattern
  multiline.pattern: 'Start new event'
  multiline.negate: true
  multiline.match: after
  multiline.flush_pattern: 'End event'

  #时间戳↓
  multiline.type: pattern
  multiline.pattern: '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}'
  multiline.negate: true
  multiline.match: after
```



#### 采集审计日志传至redis

/etc/filebeat/filebeat.yml

```yaml
- type: filestream
  paths:
    - /var/log/audit/audit.log
  tags: ["auth_log","test"]
  fields:
    type: authlog
  fields_under_root: true
output.redis:
  hosts: ["192.168.51.54:6379"]
  password: "123456"
  key: "server_syslog"
  db: "0"
  data_type: "list"
```

#### 收集nginx日志

access日志先要完成日志切割

 /etc/filebeat/filebeat.yml

```yaml
- type: filestream
  enabled: true
  paths:
    - /usr/local/nginx/logs/access.log
  tags: ["accesslog","nginx","server"]
  fields:
    app: www
    type: nginx_access
  fields_under_root: true
- type: filestream
  enabled: true
  paths:
    - /usr/local/nginx/logs/error.log
  tags: ["accesslog","nginx","server"]
  fields:
    app: www
    type: nginx_error
  fields_under_root: true
output.redis:
  hosts: ["192.168.51.54:6379"]
  password: "123456"
  key: "server_syslog"
  db: "0"
  data_type: "list"
```

/etc/logstash/conf.d/logstash-from-redis.conf

```shell
input {
    redis {
        host => "192.168.51.54"
        port => 6379
        password => "123456"
        db => "0"
        data_type => "list"
        key => "server_syslog"
    }
}
filter {
    if [app] == "www" {
        if [type] == "nginx_access" {
            json {
                source => "message"
                remove_field => ["message"]
            }
            geoip {
                source => "remote_addr"
                target => "geoip"
                database => "/opt/GeoLite2-City.mmdb"
                add_field => ["[geoip][coordinates]", "%{[geoip][longitude]}"]
                add_field => ["[geoip][coordinates]", "%{[geoip][latitude]}"]
            }
            mutate {
                convert => ["[geoip][coordinates]", "float"]
            }
        }
    }
}
output {
    stdout {
        }
    if [type] == "syslog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "server-%{type}-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "authlog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "server-%{type}-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "nginx_access" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "server-%{type}-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "nginx_error" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "server-%{type}-%{+YYYY.MM.dd}"
        }
    }
}
```

#### 收集tomcat运行日志

/etc/filebeat/filebeat.yml

```yaml
filebeat.inputs:
- type: filestream
  enabled: true
  paths:
    - /usr/local/tomcat/logs/catalina.out
  tags: ["err_log","tomcat","server"]
  fields:
    app: www
    type: tomcat_catalina
  fields_under_root: true
  multiline:
    type: pattern
    pattern: '^\['
    negate: true
    match: after

output.redis:
  hosts: ["192.168.51.54:6379"]
  password: "123456"
  key: "server_syslog"
  db: "0"
  data_type: "list"
```

/etc/logstash/conf.d/logstash-from-redis.conf

```shell
input {
    redis {
        host => "192.168.51.54"
        port => 6379
        password => "123456"
        db => "0"
        data_type => "list"
        key => "server_syslog"
    }
}
filter {
}
output {
    if [type] == "tomcat_catalina" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "server-%{type}-%{+YYYY.MM.dd}"
        }
    }
}
```



## 五、引入redis

file > logstash > redis > logstash > elasticsearch > kibana

redis可以缓存 减少logstash 和 elasticsearch的压力

从redis中读数据

logstash-from-redis.conf

```shell
input {
    redis {
        host => "192.168.51.54"
        port => 6379
        password => "123456"
        db => "0"
        data_type => "list"
        key => "server_syslog"
    }
}
filter {
}
output {
    stdout {
        }
    if [type] == "syslog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "syslog50-%{+YYYY.MM.dd}"
        }
    }
    else if [type] == "authlog" {
        elasticsearch {
            hosts => ["192.168.51.51:9200","192.168.51.52:9200","192.168.51.53:9200"]
            index => "authlog50-%{+YYYY.MM.dd}"
        }
    }
}
# 只能指定一个读
```

向redis中存数据

logstash-to-redis.conf

```shell
input {
    file {
        path => "/var/log/messages"
        tags => ["system_log","test"]
        type => "syslog"
        start_position => "beginning"
    }
    file {
        path => "/var/log/audit/audit.log"
        tags => ["auth_log","test"]
        type => "authlog"
        start_position => "beginning"
    }
}
filter {
}
output {
    redis {
        host => ["192.168.51.54:6379"]
        password => "123456"
        db => "0"
        data_type => "list"
        key => "server_syslog"
    }
}
```

