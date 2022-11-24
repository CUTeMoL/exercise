# exercise

## 个人练习以及实践的脚本

### python

#### arpScan.py

arping出局域网的MAC地址，通过MAC地址匹配OUI网卡生产商

---

#### machineInfo.py

计算机信息

---

#### dirDiff.py

查看文件夹内容是否存在不同

---

#### dirBackup.py

同步文件内容

---

#### PVcountWriteExcel.py

统计IP的访问次数和url访问次数，并写入excel文件，绘制图表

---

#### urlTest.py

测试网页质量

---

#### mongoDBNginxLogs.py

解析IP地址来源并将日志存储到到MongoDB中

---

#### traceRouteAndIpGeo.py

路由追踪

---

#### myterminal.py

paramiko模块使用

---

#### fileDiff.py

文本内容对比，生成HTML文件更直观的查看文本不同的地方

---

#### warningMail.py

监控内存，分区空间，超过后发送警告邮件

---

#### findTruePid.py

查找Windows服务器下端口被不存在的进程占用的真实pid

---

#### md5check.py

检测文件的MD5值

---

#### ftpUpload.py

上传文件到ftp服务器

---

#### portScaner.py

多进程+多线程端口扫描

---

**2022.11.20更新,可以多进程+多线程执行**

使用`ThreadPoolExecutor`

**2022.11.22更新,可以支持打包exe**

使用`freeze_support`

**2022.11.24更新,解决KeyboardInterrupt不能停止脚本的问题**

`multiprocessing.Pool`改为使用`ProcessPoolExecutor`

### shell

#### inotifywait.sh

监控目录并同步

---

#### mysql_slave_status.sh

主从同步监控

---

#### my_iftop.sh

网速分析

---

#### resource_top.sh

进程资源占用排名

---

#### web_quality.sh

测试网页质量

---

#### create_user.sh

批量创建用户

---

#### total_resource_analyze.sh

一键获取资源情况

---

#### accesslog_analyze.sh

IP访问次数排名

---

#### logrotate_acceslog.sh

日志切割

---

#### send_ssh_key.sh

发送ssh公钥

---

#### kubernetes_manager.sh

kubernetes一键二进制部署脚本，附带集群证书更新功能，添加新节点功能

---

#### mysql_install.sh

`mysql[5.7|8.0]`版本一键自动化安装,适用于centos以及Ubuntu系统

---

**2022.10.27更新,改动了启动配置文件**

_修改了 `mysqld.server` 启动文件中的`other_args`变量的值,改为`--default-file=path/my.cnf`_

_调整了 `mysqld.server ` 启动文件中`$bindir/mysqld_safe`启动命令中`$other_args`的位置_

**2022.10.1更新,优化多实例**

_修改`basedir`路径,使得不同实例可以使用相同的`basedir`,节省磁盘空间_

_修改`my.cnf`路径,方便多实例管理_

#### mysql_replica_manager.sh

主从同步工具,可以修复一些常见的主从同步错误

---

#### mysql_backup.sh

`mysql[5.7|8.0]`定时全库备份脚本

---

#### ftp_install.sh

ftp的安装

---

**2022.10.31**

_升级到以虚拟用户的方式部署_

## 经验笔记（整理中）

### note

note - 整理中的学习笔记
