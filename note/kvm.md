# KVM

## 物理机迁移云平台

### linux

| 节点  | 地址             |
| --- | -------------- |
| 物理机 | 192.168.1.1    |
| 宿主机 | 150.158.93.164 |

物理机上

```shell
yum install -y pigz nmap-ncat
```

宿主机上执行

```shell
nc -l 18888|pigz -d > /vmcluster/machine-name/machine-disk.raw
# 监听18888端口通过pigz解压数据流并保存
```

物理机上

```shell
dd if=/dev/vd bs=10M | pigz|nc 150.158.93.164 18888
```

### windows

| 节点  | 地址             |
| --- | -------------- |
| 物理机 | 192.168.1.1    |
| 宿主机 | 150.158.93.164 |

物理机上

如果是windows2008

那么需要注册表导入

```powershell
http://121.207.236.34/i/mergeide.reg
```

下载winimage8.50软件

```powershell
http://www.winimage.com/download/winima85.exe
```

用下列注册码注册：  
用户名：WinImage  
注册码：10D3FF5C

选择“creating virtual hard disk image from physical drive…“

然后选择”include non removable hard disk(s)“，会出现本地磁盘。

选择你要生成镜像的磁盘，然后选中”create dynamically expanding virtual hard disk“，选这个是为了减小磁盘文件的大小，动态分配的。

选择vmdk格式的文件保存。

通过http方式传输上面步骤二生成的镜像到具体的宿主上已经生成好的虚拟机目录。

然后执行下面命令进行转换：

```shell
qemu-img convert -f vmdk -O qcow2 -p 磁盘镜像文件名.vmdk 具体云主机uuid_disk0.qcow2
```

会出现进度条，完成后就表示镜像转换完成了。

如果是数据盘也有提取的，用下面命令转换数据盘：

```shell
qemu-img convert -f vmdk -O raw -p 磁盘镜像文件名.vmdk 具体云主机uuid_disk1.raw
```

主要是-O参数改成raw格式，同时文件名中根据磁盘数量改成disk1，disk2等。
