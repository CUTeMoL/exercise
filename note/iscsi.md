# iscsi

## 一、安装部署

1.lvm整合

```shell
pvcreate /dev/sdb
vgcreate vg0 /dev/sdb
lvcreate -L 1G -n lv0 vg0
mkfs -t ext4 /dev/vg0/lv0
```

2.target端创建IQN标签

```shell
yum install epel-release -y
yum install scsi-target-utils -y
service tgtd start
netstat -anpt | grep tgtd
tgtadm -L iscsi -o new -m target -t 1 -T ign.2016-2.com.xdl.www:lvm
# -L 指定驱动 
# -m 指定操作对象的模式 
# -o 要做的操作 
# -t 指定target的ID 
# -T 名字 定义标签固定格式ign.yyyy-mm.域名反写:lvm随便的3个字符
tgtadm -L iscsi -o show -m target   #查看
```

3.绑定IQN标签到存储设备

```shell
tgtadm -L iscsi -o new -m logicalunit -t 1 -l 1 -b /dev/vg/lv0
# -l 指定lun的ID（0是控制，不能再使用） 
# -t 指定到之前创建的target的ID号 
# -b 指定存储设备
tgtadm -L iscsi -o bind -m target -t 1 -I 192.168.66.12
# bind 绑定某固定IP使用
```

4.客户端192.168.66.12配置

```shell
yum install iscsi-initiator-utils -y
iscsiadm -m discovery -t st -p 192.168.66.11
iscsiadm -m node -T ign.2016-2.com.xdl.www:lvm --login #
iscsiadm -m node -T ign.2016-2.com.xdl.www:lvm --logout # 退出
iscsiadm -m node -op delete	# 删除登录过的信息
```

/etc/fstab

```shell
/dev/sdb	/mnt	ext4	defaults,_netdev	0	0
```

5.配置文件持久化

target端

/etc/tgt/targets.conf

```
<target ign.2016-2.com.xdl.www:lvm>	#配置共享名
    <backing-store /dev/sdb>	#实际共享出去的设备名
        vendor_id test		#配置发行商（任意）
        lun 1			#配置LUN号
    </backing-store>
    incominguser lxw 123456	#账号密码验证（可以省略）
    initiator-address 192.168.66.0/24	#允许使用的网段
</target>
```

客户端

/etc/iscsi/iscsid.conf

```
57 node.session.auth.authmethod = CHAP
61 node.session.auth.username = lxw
62 node.session.auth.password = 123456

71 discovery.sendtargets.auth.authmethod = CHAP
75 discovery.sendtargets.auth.username = lxw
76 discovery.sendtargets.auth.password = 123456
```

## 二、安装部署

1.准备环境

```shell
yum install targetcli -y
```

二、用targetcli配置存储

1.创建存储对象

(1)创建块存储对象   

```shell
# create block_name dev=/dev/vdb1
cd backstores/block
create block1 dev=/dev/vdb1
```

(2)创建fileio对象

```shell
# create fileio_name /tmp/foo1.img
cd backstores/fileio
create fileio1 /foo.img 50M
```

(3)创建ramdisk对象  

```shell
# create ramdisk_name 1M
cd backstores/ramdisk
create ramdisk1 1M
```

2.创建ISCSI target 标签

```shell
# create iqn.2021-05.com.lxw.www:stor1
cd /iscsi
create create iqn.2021-05.com.lxw.www:stor1
```

ign.yyyy-mm.域名反写:随便的n个字符

3.配置target portal group

(1)配置portals

```shell
cd iqn.2021-05.com.lxw.www:stor1/tpg1/portals
create 0.0.0.0:3260
```

(2)配置LUN：添加块设备、ramdisk、fileio三个LUN

```shell
cd iqn.2021-05.org.linuxplus.srv1:stor1/tpg1/luns
create /backstores/block/block_name
create /backstores/fileio/fileio_name
create /backstores/ramdisk/ramdisk_name
```

(3)配置ACL

①查看ISCSI initiator查看其IQN

到使用端的机器查看IQN

```shell
cat /etc/iscsi/initiatorname.iscsi
```

②服务端为每个initiator创建ACL

```shell
cd /iqn.2021-05.org.linuxplus.srv1:stor1/tpg1/acls
create iqn.1994-05.com.redhat:b83e0e28a2 # 使用端查到的
```

(4)保存配置

```shell
saveconfig
```

(5)设置target服务为自动启动

```shell
systemctl enable target.service
```

6.检查配置

initiator端使用

(1)发现

```shell
iscsiadm --mode discovery --type sendtargets --portal 192.168.1.122
```

(2)挂载

```shell
iscsiadm -d2 -m node -login
fdisk
```

(3)断开

```shell
iscsiadm -d2 -m node --logout
```

