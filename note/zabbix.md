# zabbix

## 一、安装部署

server

1.添加yum源

```shell
rpm -Uvh https://repo.zabbix.com/zabbix/5.0/rhel/7/x86_64/zabbix-release-5.0-1.el7.noarch.rpm
yum clean all
yum install zabbix-server-mysql zabbix-agent -y
yum install centos-release-scl -y
```

2./etc/yum.repos.d/zabbix.repo

```shell
[zabbix-frontend]
...
enabled=1  # 修改0为1
...
```

3.

```shell
yum install zabbix-web-mysql-scl zabbix-apache-conf-scl -y
yum install mariadb-server -y
```

4.创建mysql的zabbix用户

```shell
mysql -uroot -p
```

```mysql
create database zabbix character set utf8 collate utf8_bin;
create user zabbix@localhost identified by '123456';
grant all privileges on zabbix.* to zabbix@localhost;
quit;
```

5.导入数据库

```shell
zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uzabbix -pzabbixpw zabbix
```

6./etc/zabbix/zabbix_server.conf

```shell
DBPassword=123456
DBSocket=/var/lib/mysql/mysql.sock
```

7./etc/opt/rh/rh-php72/php-fpm.d/zabbix.conf

```
php_value date.timezone Asia/Shanghai
```

8.

```shell
systemctl restart zabbix-server zabbix-agent httpd rh-php72-php-fpm
```

agent

1.添加yum源

```shell
rpm -Uvh https://repo.zabbix.com/zabbix/5.0/rhel/7/x86_64/zabbix-release-5.0-1.el7.noarch.rpm
yum clean all
```

2.

```shell
yum install zabbix-agent
```

3./etc/zabbix/zabbix_agentd.conf

```shell
Server=192.168.51.50 # 允许的serverIP
# ServerActive=192.168.51.50
UnsafeUserParameters=1 # 启用自定义监控项
# HostMetadataItem=system.uname
```

## 二、SNMP监控

1.客户端安装snmp服务端

```shell
yum install snmpd
```

2.zabbix-server安装snmp客户端

```shell
yum install net-snmp-utils -y
```

3.snmp-server(zabbix-agent)

/etc/snmp/snmpd.conf 

```shell
#修改snmp默认社区配置
com2sec notConfigUser 192.168.0.71 MichaelXia
#修改OID视图取值范围
view systemview included .1
```

```shell
systemctl start snmpd
```

4.测试

```shell
snmpwalk  -s 192.168.51.53 -c Michaelxia -v 2c .1
```

5.web添加主机

选择SNMP类型>SNMP community>MichaelXia

6.添加监控项时

可以自定义键值

OID要转换为具体的名称

## 三、工作流程

主机 > 监控项 > 模板 > 触发器 > 动作 > 告警

## 四、自定义监控项

1./etc/zabbix/zabbix_agentd.conf或子目录

```shell
Userparameter=<key>,<shell command>
# key是自定义名称
# shell command 要绝对路径
```

2.测试

```shell
zabbix_get
测试自定义监控项
-s --host # agent host-name or IP
-p --port # agent port-number
-I --source-address # server ip-address
-k --key key-name # 自定义key
```

3.web上添加主机>监控项>创建监控项

```
名称：
键值：刚刚添加的，要完全一致
主机接口：默认
信息类型：根据类型选择
单位：
更新间隔：10s
历史数据保留时间：
趋势存储时间：
新的应用集：给键值分组
```

## 五、触发器

对指标异常的数据报警

```
名称：
严重性：等级
表达式：具体的条件，满足时报警
    条件
    监控项：选择监控项
    功能：选择函数
    最后一个：至少连续取值N次满足条件才会报警
    间隔时间：
    结果：满足的条件
恢复表达式：
```

## 六、动作(发送邮件)

1.配置邮件信息

发件设置

管理>报警媒介类型>新增

```shell
名称：
类型：mail
SMTP服务器: smtp.126.com
SMTP服务器端口: 465
SMTP HELO: 126.com
SMTP电邮: lxw@126.com # 发件地址
安全链接: SSL/TLS
SSL验证对端: 1
SSL验证主机: 1
认证: 用户与密码
用户名称: lxw@126.com
密码: 修改密码123456 #此处为邮箱授权码
Message format: 文本
描述:
已启用: 1
Message templates也要添加
```

收件设置

管理>用户>创建用户

```shell
别名：
用户名第一部分：
姓氏：
群组：
密码：
密码（再次确认）：
```

2.给收件人用户添加报警媒介

用户>报警媒介>选择新添加的

定义收件人邮箱

3.配置动作

动作>创建动作

```sehll
名称：
条件：选择触发的方式（如警示度）
操作
默认操作步骤持续时间：
暂停操作以制止问题： 1
操作：
    发送消息
    send to user 
    仅发送到：定义好的报警媒介类型
    条件：可以不填
```

## 七、动作(微信)

略

## 八、自动发现

配置>自动发现>添加规则

```
名称：
IP范围：
更新间隔：
检查：
    检查类型：zabbix客户端
    端口范围：10050
    键值：system.uname    (随意)
```

配置>动作>创建动作

```
名称：
条件：
    类型：自动发现
    自动发现检查：选择刚创建的
操作：
    操作类型：添加主机+模板关联
```

## 九、自动注册

1./etc/zabbix/zabbix_agentd.conf

```shell
Server=192.168.51.50
ServerActive=192.168.51.50
Hostname=当前客户端主机名 #自动注册|发现时记录的主机名称
HostMetadata=LINUX    #相当于自定义分组，定义自动注册时根据分组采用的动作
#HostMetadataItem=system.uname    #HostMetadata没生效时使用
```

2.

配置>动作>Autoregistration actions>创建动作

```
名称：
条件：
    类型：主机元数据
    匹配：LINUX
    操作：添加主机，链接模板
```

## 十、中文乱码解决

1.上传ttf文件，/usr/share/zabbix/assets/fonts/SIMKAI.ttf

2.修改/usr/share/zabbix/include/defines.inc.php中的字体为自己上传的ttf文件

```
define('ZBX_GRAPH_FONT_NAME',           'SIMKAI'); 
```

## 十一、监控MySQL

office

1.mysql创建用户

```mysql
create user zbx_monitor@'%' identified by '123456';
grant REPLICATION CLIENT,PROCESS,SHOW DATABASES,SHOW VIEW on *.* to zbx_monitor@'%';
quit;
```

2./etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf

mysql

```SHELL
#template_db_mysql.conf created by Zabbix for "Template DB MySQL" and Zabbix 4.2
#For OS Linux: You need create .my.cnf in zabbix-agent home directory (/var/lib/zabbix by default)
#For OS Windows: You need add PATH to mysql and mysqladmin and create my.cnf in %WINDIR%\my.cnf,C:\my.cnf,BASEDIR\my.cnf https://dev.mysql.com/doc/refman/5.7/en/option-files.html
#The file must have three strings:
#[client]
#user=zbx_monitor
#password=<password>
#
UserParameter=mysql.ping[*], mysqladmin -h"$1" -P"$2" ping
UserParameter=mysql.get_status_variables[*], mysql -h"$1" -P"$2" -sNX -e "show global status"
UserParameter=mysql.version[*], mysqladmin -s -h"$1" -P"$2" version
UserParameter=mysql.db.discovery[*], mysql -h"$1" -P"$2" -sN -e "show databases"
UserParameter=mysql.dbsize[*], mysql -h"$1" -P"$2" -sN -e "SELECT SUM(DATA_LENGTH + INDEX_LENGTH) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='$3'"
UserParameter=mysql.replication.discovery[*], mysql -h"$1" -P"$2" -sNX -e "show slave status"
UserParameter=mysql.slave_status[*], mysql -h"$1" -P"$2" -sNX -e "show slave status"
```

或

```shell
UserParameter=mysql.ping[*], mysqladmin -h"$1"  ping
UserParameter=mysql.get_status_variables[*], mysql -h"$1"  -sNX -e "show global status"
UserParameter=mysql.version[*], mysqladmin -s -h"$1"  version
UserParameter=mysql.db.discovery[*], mysql -h"$1"  -sN -e "show databases"
UserParameter=mysql.dbsize[*], mysql -h"$1"  -sN -e "SELECT COALESCE(SUM(DATA_LENGTH + INDEX_LENGTH),0) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='$3'"
UserParameter=mysql.replication.discovery[*], mysql -h"$1"  -sNX -e "show slave status"
UserParameter=mysql.slave_status[*], mysql -h"$1"  -sNX -e "show slave status" 
```

3./var/lib/zabbix/.my.cnf

```shell
[client]
user=zbx_monitor
password=123456
socket=/tmp/mysql.sock # 检查socket权限
```

4.

```shell
chown -R zabbix:zabbix /var/lib/zabbix
```

5.测试

```shell
zabbix_get -s 192.168.51.51 -k mysql.get_status_variables[localhost,3306]
```

6.添加模板

Template DB MySQL by Zabbix agent

7.重启agent

```shell
systemctl restart zabbix-agent.service
```

percona

1.安装模板

```shell
wget https://downloads.percona.com/downloads/percona-monitoring-plugins/percona-monitoring-plugins-1.1.8/binary/redhat/7/x86_64/percona-zabbix-templates-1.1.8-1.noarch.rpm
yum install percona-zabbix-templates-1.1.8-1.noarch.rpm
```

2.复制key配置文件

```shell
cp /var/lib/zabbix/percona/templates/userparameter_percona_mysql.conf /etc/zabbix/zabbix_agentd.d/
```

3.

```shell
systemctl restart zabbix-agent.service
```

4.测试

```shell
zabbix_get -s 192.168.51.50 -k MySQL.Questions
```

5.web导入zabbix_agent_template_percona_mysql_server_ht_2.0.9-sver1.1.8.xml

## 十二、监控JVM

1.

zabbix-server 

```shell
yum install zabbix-java-gateway
```

java-server 

```shell
yum install java-1.8.0-openjdk-devel tomcat-admin-webapps tomcat-docs-webapp
```

2.zabbix-server设置/etc/zabbix/zabbix_server.conf

```shell
JavaGateway=192.168.51.50    # zabbix-java-gateway ip 地址
JavaGatewayPort=10052
StartJavaPollers=5        # StartJavaPollers 应小于等于zabbix_java_gateway.conf 中START_POLLERS的值。
```

3./etc/zabbix/zabbix_java_gateway.conf

```SHELL
LISTEN_IP="0.0.0.0"
LISTEN_PORT=10052
START_POLLERS=5

#以下取消注释↓
# uncomment to enable remote monitoring of the standard JMX objects on the Zabbix Java Gateway itself
#JAVA_OPTIONS="$JAVA_OPTIONS -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=12345
#       -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
```

4.tomcat主机设置

tomcat/bin/catalina.sh

```
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote=true
-Djavax.management.builder.initial=
     -Dcom.sun.management.jmxremote.authenticate=false
     -Dcom.sun.management.jmxremote.ssl=false
     -Dcom.sun.management.jmxremote.port=12345
     -Djava.rmi.server.hostname=192.168.51.52"
```

或

```
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote
     -Dcom.sun.management.jmxremote.authenticate=false
     -Dcom.sun.management.jmxremote.ssl=false
     -Dcom.sun.management.jmxremote.port=12345
     -Djava.rmi.server.hostname=192.168.51.52"
```

5.启动java-gateway

```shell
systemctl enable zabbix-java-gateway.service
systemctl start zabbix-java-gateway.service
systemctl status zabbix-java-gateway.service   #查看gateway启动是否正常
systemctl restart zabbix-server.service
```

6.在tomcat/lib下执行

要找到对应tomcat版本的catalina-jmx-remote.jar。访问tomcat各个版本网站，从上面一直找下去。catalina-jmx-remote.jar文件在tomcat版本的/bin/extras/目录下，只要替换wget后面url即可。

```shell
wget http://archive.apache.org/dist/tomcat/tomcat-8/v8.5.37/bin/extras/catalina-jmx-remote.jar
```

7.重启tomcat

```shell
./shutdown.sh
./startup.sh
```

8.

下载cmdline-jmxclient-0.10.3.jar文件

```shell
wget -O /usr/local/tomcat/cmdline-jmxclient-0.10.3.jar http://crawler.archive.org/cmdline-jmxclient/downloads.html
```

测试

```
java -jar /usr/local/tomcat/cmdline-jmxclient-0.10.3.jar - 127.0.0.1:12345 java.lang:type=Memory HeapMemoryUsage
```

9.

配置->主机->主机zabbix server

找到JMX接口，配置如下，然后点击添加按钮

192.168.51.50    12345

10.添加模板Template App Apache Tomcat JMX

## 十三、监控Nginx

1./etc/zabbix/zabbix_agentd.d/nginx_status.conf

```
Userparameter=nginx_status[*],/usr/local/nginx/nginx_status.sh $1
```

2./usr/local/nginx/nginx_status.sh

```shell
NGINX_PORT=80  
NGINX_COMMAND=$1
nginx_active(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk '/Active/ {print $NF}'
}
nginx_reading(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk '/Reading/ {print $2}'
}
nginx_writing(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk '/Writing/ {print $4}'
       }
nginx_waiting(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk '/Waiting/ {print $6}'
       }
nginx_accepts(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk 'NR==3 {print $1}'
       }
nginx_handled(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk 'NR==3 {print $2}'
       }
nginx_requests(){
    /usr/bin/curl -s "http://127.0.0.1:"$NGINX_PORT"/status/" |awk 'NR==3 {print $3}'
       }
  case $NGINX_COMMAND in
active)
nginx_active;
;;
reading)
nginx_reading;
;;
writing)
nginx_writing;
;;
waiting)
nginx_waiting;
;;
accepts)
nginx_accepts;
;;
handled)
nginx_handled;
;;
requests)
nginx_requests;
;;
      *)
echo $"USAGE:$0 {active|reading|writing|waiting|accepts|handled|requests}"
    esac
```

```shell
chmod +x /usr/local/nginx/nginx_status.sh
```

3.测试

```shell
zabbix_get -s 192.168.51.50 -k nginx_status
```

4.在web中添加监控项

例如nginx_status[active]

需要一个个添加
