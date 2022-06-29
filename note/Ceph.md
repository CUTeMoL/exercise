# Ceph

提供文件存储、块存储、对象存储

## 一、部署

## 1.集群之间免密登录，配置/etc/hosts,时间同步

## 2.配置yum源

(1)阿里源（选luminous源version12以上才有MGR）

/etc/yum.repos.d/ceph.repo

```shell
[ceph]
name=ceph
baseurl=http://mirrors.aliyun.com/ceph/rpm-luminous/el7/x86_64/
gpgcheck=0
priority =1
[ceph-noarch]
name=cephnoarch
baseurl=http://mirrors.aliyun.com/ceph/rpm-luminous/el7/noarch/
gpgcheck=0
priority =1
[ceph-source]
name=Ceph source packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-luminous/el7/SRPMS/
gpgcheck=0
priority=1
```

(2)官方源

```shell
yum install epel-release -y
```

/etc/yum.repos.d/ceph.repo

```shell
[ceph]
name=ceph
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/x86_64/
enabled=1
gpgcheck=0
priority=1

[ceph-noarch]
name=cephnoarch
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/noarch/
enabled=1
gpgcheck=0
priority=1

[ceph-source]
name=Ceph source packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/SRPMS
enabled=1
gpgcheck=0
priority=1
```

## 3.master节点上部署工具

```
yum install ceph-deploy -y
yum install gcc python-setuptools python-devel
yum install python2
```

node1上创建1个集群配置目录

```shell
mkdir /etc/ceph
```

## 4.创建一个ceph集群

```shell
cd /etc/ceph #一定要在此目录内
ceph-deploy new node1
# 会生成3个文件
# ceph.conf #集群配置文件
# ceph-deploy-ceph.log #ceph-deploy部署的日志记录
# ceph.mon.keyring #mon的验证key文件
```

## 5.所有node安装ceph

```shell
yum install ceph ceph-radosgw -y
```

或可以监控端用

```shell
ceph-deploy install node1 node2 node3
ceph -s # 查看健康度
```

## 6.使用端安装

```shell
yum install ceph-common -y
```

## 7.创建MON监控

/etc/ceph/ceph.conf

```shell
[global]
public network = 192.168.51.0/24
mon clock drift allowed = 2
mon clock drift warn backoff = 30
```

监控节点初始化

```shell
ceph-deploy mon create-initial
```

配置文件同步

```shell
ceph-deploy admin node1 node2 node3
ceph-deploy --overwrite-conf admin node1 node2 node3 # 强制覆盖
```

添加监控节点

```shell
ceph-deploy mon add node2
ceph-deploy mon add node3
```

所有监控节点

```shell
systemctl restart ceph-mon.target
```

8.创建mgr(管理)

```
ceph-deploy mgr create node1
ceph-deploy mgr create node2
ceph-deploy mgr create node3
```

## 9.创建osd

列出节点的磁盘

```shell
ceph-deploy disk list node1
```

格式化磁盘

```shell
ceph-deploy disk zap node1 /dev/sdb
ceph-deploy disk zap node2 /dev/sdb
ceph-deploy disk zap node3 /dev/sdb
```

将磁盘创建为osd

```shell
ceph-deploy osd create --data /dev/sdb node1
ceph-deploy osd create --data /dev/sdb node2
ceph-deploy osd create --data /dev/sdb node3
```

扩充

(1)主机名绑定

(2)yum部署

```shell
yum install ceph ceph-radosgw -y
```

(3)deploy添加节点

```
ceph-deploy admin node4
```

(4)按需求选择在node4上添加mon或mgr或osd等

## 10.pool

### 创建pool

```shell
ceph osd pool create test_pool 128
```

查看PG数量

```shell
ceph osd pool get test_pool pg_num
```

少于 5 个 OSD 时可把 pg_num 设置为 128；

OSD 数量在 5 到 10 个时，可把 pg_num 设置为 512；

OSD 数量在 10 到 50 个时，可把 pg_num 设置为 4096；

调整PG数量

```shell
ceph osd pool set test_pool pg_num 64
```

#自动调整

```shell
ceph osd pool set test_pool pg_autoscale_mode on
```

### 删除pool

编辑配置文件，允许删除pool

/etc/ceph/ceph.conf

```shell
mon_allow_pool_delete = true
```

配置文件传输到其他节点

```shell
ceph-deploy --overwrite-conf admin node1 node2 node3
```

重启监控服务

```shell
systemctl restart ceph-mon.target
ceph osd pool delete test_pool test_pool --yes-i-really-really-mean-it
```



## 11.原生存储的使用

上传文件到test_pool

```shell
rados put newfstab /etc/fstab --pool=test_pool
```

查看pool中的文件

```shell
rados -p test_pool ls
```

删除pool中的文件

```shell
rados rm newfstab --pool=test_pool
# -p = --pool
```

## 12.文件存储的部署

至少要有一个mds

ceph mds：ceph文件存储类型存放与管理元数据metadata的服务

创建元数据服务

```shell
ceph-deploy mds create node1 node2 node3
```

创建文件池和元数据池

```shell
ceph osd pool create cephfs_pool 128
ceph osd pool create cephfs_metadata 64
```

创建一个文件存储FS

```shell
ceph fs new cephfs cephfs_metadata cephfs_pool
# ceph fs new 这个文件系统的名称 文件系统的元数据盘名称 文件系统的数据盘名称
```

```shell
ceph fs ls # 查看fs创建是否成功
ceph mds stat # 查看mds状态
ceph osd pool ls # 查看osdpool
```



默认启用cephx，需要把密钥给客户端使用

```shell
cat /etc/ceph/ceph.client.admin.keyring #查看密钥
key = AQDEKlJdiLlKAxAARx/PXR3glQqtvFFMhlhPmw==  # 后面的字符串就是验证需要的
```


client上vim admin.key

```
AQDEKlJdiLlKAxAARx/PXR3glQqtvFFMhlhPmw==
```

client挂载

```shell
mount -t ceph node1:6789:/ /mnt -o name=admin,secretfile=/root/admin.key
```

主机选择监控节点，有多个监控节点那么也可以同时使用，端口是6789，此处-o要写后面

删除文件存储

client先清空所有的数据

```shell
rm /mnt/* -rf
```

client解除挂载

```shell
umount /mnt
```

停止所有节点的mds

```shell
systemctl stop ceph-mds.target
```

检查一下fs的信息

```shell
ceph fs ls
```

删除fs的文件格式

```shell
ceph fs rm cephfs --yes-i-really-mean-it
# cephfs是之前起的名字
```

删除osd pool

```shell
ceph osd pool delete cephfs_metadata cephfs_metadata --yes-i-really-really-mean-it
ceph osd pool delete cephfs_pool cephfs_pool --yes-i-really-really-mean-it
```

启动所有节点mds服务

```shell
systemctl start ceph-mds.target
```

## 13.块存储的部署RBD

主要在客户机上操作，所以先同步配置文件到客户机

```shell
ceph-deploy admin client
```

创建osd_pool池，名为rbd_pool

```shell
ceph osd pool create rbd_pool 128
```

将osd_pool初始化为RBD格式，这步可以跳过

```shell
rbd pool init rbd_pool
```

创建image(块设备、卷)pool_name/image(块设备、卷)，并定义大小，这里的大小可以超过实际pool大小

```shell
rbd create rbd_pool/myrbd --size 16384 
rbd create myrbd --pool rbd_pool --size 5000 # 另一种
rbd map rbd_pool/myrbd # 映射
```

此时lsblk中就有了dev/rbd0 



```shell
rbd ls rbd_pool # 可以查看这个池下共有几个卷
rbd info myrbd -p rbd_pool # 可以查看卷信息
rbd info rbd_pool/myrbd # 可以查看卷信息
```


格式化

```shell
mkfs.xfs /dev/rbd0
```

挂载

```shell
mount /dev/rbd0 /mnt/
```

rbd: image myrbd: image uses unsupported features: 0x38的处理方法

删除不支持的特性

```shell
rbd feature disable rbd_pool/myrbd exclusive-lock object-map fast-diff deep-flatten
# layering: 支持分层
# striping: 支持条带化 v2
# exclusive-lock: 支持独占锁
# object-map: 支持对象映射（依赖 exclusive-lock ）
# fast-diff: 快速计算差异（依赖 object-map ）
# deep-flatten: 支持快照扁平化操作
# journaling: 支持记录 IO 操作（依赖独占锁）
```

或

/etc/ceph/ceph.conf

```shell
rbd_default_features = 1
```

或

创建时指定特性

```shell
rbd create myrbd --pool rbd_pool --size 5000 --image-feature layering
```

解除映射

```shell
rbd unmap /dev/rbd0
```

更改image大小

```shell
rbd resize rbd_pool/myrbd --size 51200 --allow-shrink
rbd info rbd_pool/myrbd # 查看，已扩容卷
```

如果df -h查看未变化

```shell
xfs_growfs -d /mnt
```

如果存在分区则可能一样没有变化

缩减要解挂再重新格式化

删除块存储

```shell
rbd rm rbd_pool/myrbd
```

删除池

```shell
ceph osd pool delete rbd_pool rbd_pool --yes-i-really-really-mean-it
```

## 14.对象存储rgw(radosgw)

创建rgw

```shell
ceph-deploy rgw create node1
lsof -i:7480
```

传配置文件给客户端

```shell
ceph-deploy admin client
radosgw-admin user create --uid="linxuewei" --display-name="lxw"
```

获取

```shell
keys: [
    {
        "user": "linxuewei",
        "access_key": "NU2E379HAI7O2ZO5MW7M",
        "secret_key": "3Bn0yVQoeNMsQsvmJMQdnhzhccxewUP4rQ5KJVjy"
    }
]
```

客户端

```
yum install s3cmd -y
```

/root/.s3cfg

```shell
[default]
access_key = 36ROCI84S5NSP4BPYL01
secret_key = jBOKH0v6J79bn8jaAF2oaWU7JvqTxqb4gjerWOFW 
host_base = 10.1.1.11:7480
host_bucket = 10.1.1.11:7480/%(bucket)
cloudfront_host = 10.1.1.11:7480
use_https = False
```

完成后可用s3cmd操作了

## 15.ceph dashboard开启

```shell
ceph mgr module enable dashboard
```

