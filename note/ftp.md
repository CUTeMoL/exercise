# FTP

## 一、部署

```shell
#!/bin/bash
root_dir="/data/ftp/"
ftpuser="lxw"
ftphost="127.0.0.1"
# 系统判断
if [ -e /etc/issue ] && [ ! -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/issue`
elif [ -e /etc/issue ] && [ -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/redhat-release`
else
    echo "This system is not supported" && exit
fi
# 安装vsftpd
if [[ ${os_version} = CentOS ]];then
    yum install vsftpd -y >/dev/null 2>&1
    vsftpd_root="/etc/vsftpd"
elif [[ ${os_version} = Ubuntu ]];then
    apt install vsftpd -y >/dev/null 2>&1
    vsftpd_root="/etc"
fi
# 创建ftp用户
id ${ftpuser} >/dev/null 2>&1
if [ $? -ne 0 ];then
    useradd ${ftpuser} >/dev/null 2>&1
fi
# 创建白名单
touch  ${vsftpd_root}/chroot_list
echo "${ftpuser}" >> ${vsftpd_root}/user_list
# 创建根路径
mkdir -p ${root_dir}
chmod -R 777 ${root_dir}
# 修改配置文件
mv ${vsftpd_root}/vsftpd.conf ${vsftpd_root}/vsftpd.conf_`date "+%F"`
cat > ${vsftpd_root}/vsftpd.conf <<EOF
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
xferlog_enable=YES
xferlog_file=/var/log/xferlog
xferlog_std_format=YES
ascii_upload_enable=YES
ascii_download_enable=YES
chroot_local_user=YES
chroot_list_enable=YES
chroot_list_file=${vsftpd_root}/chroot_list
allow_writeable_chroot=YES
listen=YES
pam_service_name=vsftpd
userlist_enable=YES
userlist_file=${vsftpd_root}/user_list
userlist_deny=NO
tcp_wrappers=YES
local_root=${root_dir}
pasv_enable=YES
pasv_address=${ftphost}
pasv_min_port=65400
pasv_max_port=65500
EOF
systemctl restart vsftpd
```

