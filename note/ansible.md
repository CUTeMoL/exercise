

# ansible

## 一、安装部署

1.

~~~shell
yum install epel-release
yum install ansible
ansible --version
~~~

2.免密(操作agent时都要加-k参数传密码;或者在主机清单里传密码)

~~~shell
ssh-keygen
ssh-copy-id -i 10.1.1.12
ssh-copy-id -i 10.1.1.13
~~~

3.定义主机组,并测试连接性

/etc/ansible/hosts可以定义服务器分组

~~~shell
master# vim /etc/ansible/hosts 
# 格式
# IP
# IP:PORT
# 别名ALIAS_NAME ansible_ssh_host=IP ansible_ssh_port=PORT ansible_ssh_user=root ansible_ssh_pass="123456"
[GROUP_NAME]
ALIAS_NAME
# 可以先定义主机信息和别名，然后在分组
~~~

## 二、ansible模块

### 查看所有支持的模块

~~~shell
ansible-doc -l
~~~

如果要查看具体模块的用法

```shell
ansible-doc module_name
```

基本格式

```shell
ansible group_name -m module_name -a "key1=value1 key2=value2"
```

### hostname模块

hostname模块用于修改主机名,不能修改/etc/hosts文件

~~~shell
ansible group_name  -m hostname -a 'name=www.lxw.com'
~~~

### file模块

file模块用于对文件相关的操作(创建, 删除, 软硬链接等)

创建一个目录

~~~shell
ansible group_name -m file -a 'path=/test state=directory'
~~~

创建一个文件

~~~shell
ansible group_name -m file -a 'path=/tmp/111 state=touch owner=lxw group=lxw mode=1700'
~~~

递归修改owner,group,mode

~~~shell
ansible group_name -m file -a 'path=/test recurse=yes owner=lxw group=lxw mode=1700'
~~~

删除目录（连同目录里的所有文件)或文件

~~~shell
ansible group_name -m file -a 'path=/test state=absent'
~~~

创建软链接文件

~~~shell
ansible group_name -m file -a 'src=/etc/fstab path=/tmp/fstab state=link'
~~~

创建硬链接文件

~~~shell
ansible group_name -m file -a 'src=/etc/fstab path=/tmp/fstab2 state=hard'
~~~

### stat模块

获取/etc/fstab文件的状态信息

~~~shell
ansible group_name -m stat -a 'path=/etc/fstab'
~~~

### copy模块

本地拷贝到远程

~~~shell
ansible group_name -m copy -a 'src=/tmp/222 dest=/tmp/333'
~~~

使用content参数直接往远程文件里写内容（会覆盖原内容）

~~~shell
ansible group_name -m copy -a 'content="ha ha\n" dest=/tmp/333'
~~~

使用force参数控制是否强制覆盖

~~~shell
# 如果目标文件已经存在，则不覆盖
ansible group_name -m copy -a 'src=/tmp/222 dest=/tmp/333 force=no'
# 如果目标文件已经存在，则会强制覆盖
ansible group_name -m copy -a 'src=/tmp/222 dest=/tmp/333 force=yes'
~~~

使用backup参数控制是否备份文件

~~~shell
# backup=yes表示如果拷贝的文件内容与原内容不一样，则会备份一份
# group_name的机器上会将/tmp/333备份一份（备份文件命名加上时间），再远程拷贝新的文件为/tmp/333
ansible group_name -m copy -a 'src=/etc/fstab dest=/tmp/333 backup=yes owner=daemon group=daemon mode=1777'
~~~

copy模块拷贝时要注意拷贝目录后面是否带"/"符号

~~~shell
#/etc/yum.repos.d后面不带/符号，则表示把/etc/yum.repos.d整个目录拷贝到/tmp/目录下
ansible group_name -m copy -a 'src=/etc/yum.repos.d dest=/tmp/'
#/etc/yum.repos.d/后面带/符号，则表示把/etc/yum.repos.d/目录里的所有文件拷贝到/tmp/目录下
ansible group_name -m copy -a 'src=/etc/yum.repos.d/ dest=/tmp/'
~~~

在master上配置好所有的yum源，然后拷贝到group_name的远程机器上（要求目录内的内容完全一致)**

~~~shell
ansible group_name -m file -a "path=/etc/yum.repos.d/ state=absent"
ansible group_name -m copy -a "src=/etc/yum.repos.d dest=/etc/"
~~~

使用hostname模块修改过主机名后.在master上修改/etc/hosts文件，并拷贝到group_name的远程机器上

~~~shell
#先在master上修改好/etc/hosts文件，然后使用下面命令拷贝过去覆盖
ansible group_name -m copy -a "src=/etc/hosts dest=/etc/hosts"
~~~

### fetch模块

fetch模块与copy模块类似，但作用相反。用于把远程机器的文件拷贝到本地。

~~~shell
ansible group_name  -m fetch -a 'src=/tmp/1.txt dest=/tmp/'
10.1.1.12 | CHANGED => {
    "changed": true, 
    "checksum": "d2911a028d3fcdf775a4e26c0b9c9d981551ae41", 
    "dest": "/tmp/10.1.1.12/tmp/1.txt", 	10.1.1.12的在这里
    "md5sum": "0d59da0b2723eb03ecfbb0d779e6eca5", 
    "remote_checksum": "d2911a028d3fcdf775a4e26c0b9c9d981551ae41", 
    "remote_md5sum": null
}
10.1.1.13 | CHANGED => {
    "changed": true, 
    "checksum": "b27fb3c4285612643593d53045035bd8d972c995", 
    "dest": "/tmp/10.1.1.13/tmp/1.txt", 	10.1.1.13的在这里
    "md5sum": "cd0bd22f33d6324908dbadf6bc128f52", 
    "remote_checksum": "b27fb3c4285612643593d53045035bd8d972c995", 
    "remote_md5sum": null
}

~~~

会使用名称来做子目录区分

fetch模块不能从远程拷贝目录到本地

### user模块

user模块用于管理用户账号和用户属性。

创建aaa用户,默认为普通用户,创建家目录

~~~shell
ansible group_name -m user -a 'name=aaa state=present'
~~~

创建bbb系统用户,并且登录shell环境为/sbin/nologin

~~~shell
ansible group_name -m user -a 'name=bbb state=present system=yes  shell="/sbin/nologin"'
~~~

创建ccc用户, 使用uid参数指定uid, 使用password参数传密码

~~~shell
echo 123456 | openssl passwd -1 -stdin 
# $1$DpcyhW2G$Kb/y1f.lyLI4MpRlHU9oq0
ansible group_name -m user -a 'name=ccc uid=2000 state=present password="$1$DpcyhW2G$Kb/y1f.lyLI4MpRlHU9oq0"'
~~~

创建一个普通用户叫hadoop,并产生空密码密钥对

~~~shell
ansible group_name -m user -a 'name=hadoop generate_ssh_key=yes'
~~~

删除aaa用户,但家目录默认没有删除

~~~shell
ansible group_name -m user -a 'name=aaa state=absent'
~~~

删除bbb用户,使用remove=yes参数让其删除用户的同时也删除家目录

~~~shell
ansible group_name -m user -a 'name=bbb state=absent remove=yes'
~~~




### group模块

group模块用于管理用户组和用户组属性。

创建组

~~~shell
ansible group_name -m group -a 'name=groupa gid=3000 state=present'
~~~

删除组（如果有用户的gid为此组，则删除不了)

~~~shell
ansible group_name -m group -a 'name=groupa state=absent'
~~~



### cron模块

cron模块用于管理周期性时间任务

创建一个cron任务,不指定user的话,默认就是root（因为我这里是用root操作的)。

如果minute,hour,day,month,week不指定的话，默认都为*

~~~shell
ansible group_name -m cron -a 'name="test cron1" user=root job="touch /tmp/111" minute=*/2' 
~~~

删除cron任务

~~~shell
ansible group_name -m cron -a 'name="test cron1" state=absent'
~~~



### yum_repository模块

yum_repository模块用于配置yum仓库。

增加一个/etc/yum.repos.d/local.repo配置文件

~~~shell
ansible group_name -m yum_repository -a "name=local description=localyum baseurl=file:///mnt/ enabled=yes gpgcheck=no"
~~~

删除/etc/yum.repos.d/local.repo配置文件

~~~shell
ansible group_name -m yum_repository -a "name=local state=absent" 
~~~



### yum模块

yum模块用于使用yum命令来实现软件包的安装与卸载。

使用yum安装一个软件

~~~shell
ansible group_name -m yum -a 'name=vsftpd state=present'
~~~

使用yum安装httpd,httpd-devel软件,state=latest表示安装最新版本

~~~shell
ansible group_name -m yum -a 'name=httpd,httpd-devel state=latest' 
~~~

使用yum卸载httpd,httpd-devel软件

~~~shell
ansible group_name -m yum -a 'name=httpd,httpd-devel state=absent' 
~~~

### service模块

service模块用于控制服务的启动,关闭,开机自启动等。

启动vsftpd服务，并设为开机自动启动

~~~shell
ansible group_name -m service -a 'name=vsftpd state=started enabled=on'
~~~

关闭vsftpd服务，并设为开机不自动启动

~~~shell
ansible group_name -m service -a 'name=vsftpd state=stopped enabled=false'
~~~

### script模块

script模块用于在远程机器上执行本地脚本。

```shell
ansible group_name -m script -a '/tmp/1.sh'
```

### command与shell模块

shell模块与command模块差不多（command模块不能执行一些类似$HOME,>,<,|等符号，但shell可以)

```shell
ansible -m command group_name -a "useradd user2"
ansible -m command group_name -a "id user2"
ansible -m command group_name -a "cat /etc/passwd |wc -l"		--报错
ansible -m shell group_name -a "cat /etc/passwd |wc -l"		--成功
ansible -m command group_name -a "cd $HOME;pwd"	　　--报错
ansible -m shell 　group_name -a "cd $HOME;pwd"	　　--成功
```

**注意:** shell模块并不是百分之百任何命令都可以,比如vim或ll别名就不可以。不建议大家去记忆哪些命令不可以，大家只要养成任何在生产环境里的命令都要先在测试环境里测试一下的习惯就好。

# 三、playbook

playbook(剧本): 是ansible用于配置,部署,和管理被控节点的剧本。用于ansible操作的编排。

使用的格式为**yaml**格式

1.创建一个存放playbook的目录(路径自定义)

```shell
mkdir /etc/ansible/playbook
```

2.写一个playbook文件(后缀为.yml或.yaml)

/etc/ansible/playbook/example.yaml

```shell
---
# "---"yaml的开头
# "-"列表
- hosts: group_name # /etc/ansible/hosts中的
  remote_user: root # 进行远程操作的用户
  vars: #定义变量 {{key}}可以调用变量
   - key: value 
  tasks:   # 定义任务
  - name: ensure apache is at the latest version	# 名称
    yum: name=httpd,httpd-devel state=latest #模块: 参数(同-a的value)
    
  - name: write the apache config file		
    copy: src=/etc/httpd/conf/httpd.conf dest=/etc/httpd/conf/httpd.conf
    
    notify: # 检查点，当此task执行了任务达到change，就触发对应的handle
    - restart apache # handle_name
    
  - name: ensure apache is running (and enable it at boot)
    service: name=httpd state=started enabled=yes
    
  handlers:	
    - name: restart apache # 定义handle_name，
      service: name=httpd state=restarted
```

第4步: 执行写好的palybook

会显示出执行的过程，并且执行的每一步都有ok,changed,failed等标识

执行如果有错误(failed)会回滚，解决问题后，直接再执行这条命令即可,并会把failed改为changed（幂等性)

```shell
ansible-playbook /etc/ansible/playbook/example.yaml
```

# 四、roles

## roles介绍

roles(角色): 就是通过分别将variables, tasks及handlers等放置于单独的目录中,并可以便捷地调用它们的一种机制。

假设我们要写一个playbook来安装管理lamp环境，那么这个playbook就会写很长。所以我们希望把这个很大的文件分成多个功能拆分, 分成apache管理,php管理,mysql管理，然后在需要使用的时候直接调用就可以了，以免重复写。就类似编程里的模块化的概念，以达到代码复用的效果。

## **创建roles的目录结构**

```shell
files：用来存放由copy模块或script模块调用的文件。
tasks：至少有一个main.yml文件，定义各tasks。
handlers:有一个main.yml文件，定义各handlers。
templates：用来存放jinjia2模板。
vars：有一个main.yml文件，定义变量。
meta：有一个main.yml文件，定义此角色的特殊设定及其依赖关系。
```

**注意:** 在每个角色的目录中分别创建files, tasks,handlers,templates,vars和meta目录，用不到的目录可以创建为空目录.

## 通过roles实现lamp

需定制三个角色: httpd,mysql,php

1.创建roles目录及文件,并确认目录结构

```shell
cd /etc/ansible/roles/
mkdir -p {httpd,mysql,php}/{files,tasks,handlers,templates,vars,meta}
touch {httpd,mysql,php}/{tasks,handlers,vars,meta}/main.yml
```

2.准备httpd服务器的主页文件,php测试页和配置文件等

```shell
master# echo "test main page" > /etc/ansible/roles/httpd/files/index.html


master# echo -e "<?php\n\tphpinfo();\n?>" > /etc/ansible/roles/httpd/files/test.php 


master# yum install httpd -y
按需求修改配置文件后,拷贝到httpd角色目录里的files子目录
master# vim /etc/httpd/conf/httpd.conf
master# cp /etc/httpd/conf/httpd.conf /etc/ansible/roles/httpd/files/
```



2.编写httpd角色的main.yml文件

```shell
---
 - name: 安装httpd
   yum: name=httpd,httpd-devel state=present

 - name: 同步httpd配置文件
   copy: src=/etc/ansible/roles/httpd/files/httpd.conf dest=/etc/httpd/conf/httpd.conf

   notify: restart httpd

 - name: 同步主页文件
   copy: src=/etc/ansible/roles/httpd/files/index.html dest=/var/www/html/index.html

 - name: 同步php测试页
   copy: src=/etc/ansible/roles/httpd/files/test.php dest=/var/www/html/test.php

 - name: 启动httpd并开机自启动
   service: name=httpd state=started enabled=yes
```

4.编写httpd角色里的handler

```shell
master# vim /etc/ansible/roles/httpd/handlers/main.yml
---
- name: restart httpd
  service: name=httpd state=restarted
```

5.编写mysql角色的main.yml文件

```shell
---
- name: 安装mysql
  yum: name=mariadb,mariadb-server,mariadb-devel state=present

- name: 启动mysql并开机自启动
  service: name=mariadb state=started enabled=yes
```

6.编写php角色的main.yml文件

```shell
master# vim /etc/ansible/roles/php/tasks/main.yml
---
- name: 安装php及依赖包
  yum: name=php,php-gd,php-ldap,php-odbc,php-pear,php-xml,php-xmlrpc,php-mbstring,php-snmp,php-soap,curl,curl-devel,php-bcmath,php-mysql state=present

  notify: restart httpd
```

7.编写lamp的playbook文件调用前面定义好的三个角色

```shell
master# vim /etc/ansible/playbook/lamp.yaml
---
- hosts: group_name
  remote_user: root
  roles:
    - httpd
    - mysql
    - php
```

8.执行lamp的playbook文件

```shell
master# ansible-playbook /etc/ansible/playbook/lamp.yaml
```

 
