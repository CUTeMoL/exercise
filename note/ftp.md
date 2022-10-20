# FTP

## 一、部署

```shell
#!/bin/bash
# 修改以下变量
root_dir="/data/ftp/" # ftp根目录
ftpuser="lxw" # ftp用户
ftppasswd="123456" # 密码
ftphost="127.0.0.1" # 被动模式

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
    vsftpd_conf_dir="/etc/vsftpd"
elif [[ ${os_version} = Ubuntu ]];then
    apt install vsftpd -y >/dev/null 2>&1
    vsftpd_conf_dir="/etc"
fi

modify_ftp_conf() {
    # 创建根路径
    root_dir=$1
    vsftpd_conf_dir=$2
    root_dir=$3
    ftphost=$4
    mkdir -p ${root_dir}
    chmod -R 777 ${root_dir}
    # 修改配置文件
    mv ${vsftpd_conf_dir}/vsftpd.conf ${vsftpd_conf_dir}/vsftpd.conf_`date "+%F"`
    cat > ${vsftpd_conf_dir}/vsftpd.conf <<EOF
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
chroot_list_file=${vsftpd_conf_dir}/chroot_list
allow_writeable_chroot=YES
listen=YES
pam_service_name=vsftpd
userlist_enable=YES
userlist_file=${vsftpd_conf_dir}/user_list
userlist_deny=NO
tcp_wrappers=YES
local_root=${root_dir}
pasv_enable=YES
pasv_address=${ftphost}
pasv_min_port=65400
pasv_max_port=65500
EOF
}

ftp_useradd(){
    # 创建ftp用户
    ftpuser=$1
    ftppasswd=$2
    vsftpd_conf_dir=$3
    id ${ftpuser} >/dev/null 2>&1
    if [ $? -ne 0 ];then
        useradd ${ftpuser} >/dev/null 2>&1
        echo ${ftppasswd} | passwd --stdin ${ftpuser}
    fi
    # 创建不受限制的名单
    touch ${vsftpd_conf_dir}/chroot_list
    # 创建白名单
    grep "${ftpuser}" ${vsftpd_conf_dir}/user_list >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "${ftpuser}" >> ${vsftpd_conf_dir}/user_list
    fi
}
ftpcheck(){
    sleep 10
	ftpprocess_count=`ps -ef|grep vsftpd|grep -v "color=auto"|wc -l`
	if [ ${ftpprocess_count} -eq 1 ];then
	    echo "FTP install completed" && exit
	else
	    echo "FTP install failed.Please check it." && exit
	fi
}
ftp_useradd ${ftpuser} ${ftppasswd} ${vsftpd_conf_dir}
modify_ftp_conf ${root_dir} ${vsftpd_conf_dir} ${root_dir} ${ftphost}
systemctl restart vsftpd
ftpcheck
```

## 二、配置

vsftpd.conf

```shell
# base
tcp_wrappers=YES # 限速相关
local_root=${root_dir} # 根目录
anonymous_enable=NO # 匿名访问
local_enable=YES # 本地用户访问
write_enable=YES # 写总开关
local_umask=022 # 权限子码
dirmessage_enable=YES # 目录变更消息计入日志
xferlog_enable=YES # 开启xferlog
xferlog_file=/var/log/xferlog # 路径
xferlog_std_format=YES # 记录xferlog日志风格
ascii_upload_enable=YES
ascii_download_enable=YES # ascii支持
listen=YES # ipv4监听
pam_service_name=vsftpd # pam

# 更改路径不受限
chroot_local_user=YES # 本地用户更改路径不限
chroot_list_enable=YES # 改变目录名单
chroot_list_file=${vsftpd_conf_dir}/chroot_list # 本地用户更改路径不限的用户名单路径
allow_writeable_chroot=YES # 改变目录时可写

# 用户名单
userlist_enable=YES # 启用用户名单
userlist_file=${vsftpd_conf_dir}/user_list # 用户名单路径
userlist_deny=NO # 决定用户名单是黑名单还是白名单


# 被动模式
pasv_enable=YES
pasv_address=${ftphost} # 绑定地址
pasv_min_port=65400
pasv_max_port=65500 # 被动模式范围
```

