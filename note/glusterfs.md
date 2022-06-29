# glusterfs

文件系统级别的共享

## 一、安装部署

1.添加glusterfs的yum源

/etc/yum.repos.d/glusterfs.repo

```shell
[glusterfs]
name=glusterfs
basurl=https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-7/
enabled=1
gpgcheck=1
```

或者

```shell
yum install centos-release-gluster7
```

2.安装

```shell
yum install glusterfs-server -y
```

3.启动

```shell
systemctl start glusterd
systemctl enable glusterd
```

4.连接节点只需其中一台设备连接其他台就可以（无中心）

```shell
gluster peer probe (hostname|ip-address)   #建立连接
gluster peer detach (hostname|ip-address)  #删除连接
gluster peer status   #点的状态
gluster peer list    #全状态
```

5.所有分布式存储建立要分享的目录

```shell
mkdir -p /data/gv0
```

6.建立卷

(1)复制模式

```shell
gluster volume create gv0 replica 4 storage1.lxw.com:/data/gv0 storage2.lxw.com:/data/gv0 storage3.lxw.com:/data/gv0 storage4.lxw.com:/data/gv0 force
# gv0 是卷名、可变
#replica 指副本模式4代表一共会存为4份数据
# hostname|ip-address:/dirname
# force 可以不加，尽可能使用别块硬盘，当用根分区时则一定要加
```

(2)条带模式

```shell
gluster volume create gv0 stripe 4 storage1.lxw.com:/data/gv0 storage2.lxw.com:/data/gv0 storage3.lxw.com:/data/gv0 storage4.lxw.com:/data/gv0 force
# stripe 条带化数据，一份分成4个地方存储
```

(3)distributed模式，分布卷，默认

```shell
gluster volume create gv0 storage1.lxw.com:/data/gv0 storage2.lxw.com:/data/gv0 storage3.lxw.com:/data/gv0 storage4.lxw.com:/data/gv0 force
# distributed 按最小单位文件个数随机写入，一个文件只会存在一个块上
```

(4)distributed-replica模式

```SHELL
gluster volume create gv2 replica 2 storage1:/data/gv2/ storage2:/data/gv2/ storage3:/data/gv2/ storage4:/data/gv2/ force  
# replica可为2，3……N 数据会存储N分
# 块的数量为replica的倍数
# 可以扩容和HA
```

(5)dispersed模式

```shell
gluster volume create gv2 disperse 4 redundancy 1 storage1:/data/gv2/ storage2:/data/gv2/ storage3:/data/gv2/ storage4:/data/gv2/ force 
# disperse类似raid5，数据分n份存，再另的块上冗余
# redundancy 指定冗余的数量 5%=2 4%=1
```

如果 4余1 有一台挂了 那么依然能使用 但是就没有校验了
挂了的恢复时，会重新恢复数据

查看已建立的分布式存储卷的情况

```shell
gluster volume info gv0
```

启动卷

```shell
gluster volume start gv0
```

7.client安装glusterfs-fuse(远程挂载客户端)

```shell
yum install glusterfs glusterfs-fuse -y
```

8.client挂载

```shell
mount.glusterfs storage1.lxw.com:gv0 /glusterfs_data
```

如果挂载失败可以查看log

```shell
cat /var/log/glusterfs/glusterfs_data.log
```

9.卷的删除

client要先解除挂载

```shell
umount /glusterfs_data
```

停止卷

```shell
gluster volume stop vg0
```

删除卷

```shell
gluster volume delete vg0
```

10.在线裁剪和扩容
裁剪

```shell
gluster volume remove-brick gv0 storage4:/data/gv0 force
```

扩容

```shell
gluster volume add-brick gv0 storage5:/data/gv0 force
```

