#!/bin/bash
# 修改以下变量
root_dir="/data/ftp/" # ftp根目录
ftpuser="ftpuser" # ftp用户
ftppasswd="123456" # 密码
ftphost="127.0.0.1" # 被动模式
virtualuser="crq"
virtualpasswd="123456"
virtualrootdir="${root_dir}${virtualuser}"
# 系统判断
if [ -e /etc/issue ] && [ ! -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/issue`
    vsftpd_conf_dir="/etc"
elif [ -e /etc/issue ] && [ -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/redhat-release`
    vsftpd_conf_dir="/etc/vsftpd"
else
    echo "This system is not supported" && exit
fi
# 安装vsftpd
vsftpd_install() {
    os_version=$1
    if [[ ${os_version} = CentOS ]];then
        yum install db4 db4-utils vsftpd -y >/dev/null 2>&1
    elif [[ ${os_version} = Ubuntu ]];then
        apt install db5.3-util vsftpd -y >/dev/null 2>&1
        if [ ! -e /usr/bin/db_load ];then
            ln -s /usr/bin/db5.3_load /usr/bin/db_load
        fi
    fi
}
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
guest_enable=YES
guest_username=${ftpuser}
user_config_dir=${vsftpd_conf_dir}/user_conf/
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
pam_service_name=vsftpd.vu
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
    cat > /etc/pam.d/vsftpd.vu <<EOF
auth  required  pam_userdb.so  db=/etc/vsftpd/vsftpd_login
account  required  pam_userdb.so  db=/etc/vsftpd/vsftpd_login
EOF
}

ftp_useradd(){
    # 创建ftp用户
    ftpuser=$1
    ftppasswd=$2
    vsftpd_conf_dir=$3
    virtualuser=$4
    virtualpasswd=$5
    virtualrootdir=$6
    id ${ftpuser} >/dev/null 2>&1
    if [ $? -ne 0 ];then
        useradd ${ftpuser} >/dev/null 2>&1
        # ubuntu 不能使用passwd --stdin 需要手动修改密码
        echo ${ftppasswd} | passwd --stdin ${ftpuser}
    fi
    # 创建不受限制的名单
    touch ${vsftpd_conf_dir}/chroot_list
    # 创建白名单
    sed -i "/^#/d" ${vsftpd_conf_dir}/user_list
    grep "${virtualuser}" ${vsftpd_conf_dir}/user_list >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "${virtualuser}" >> ${vsftpd_conf_dir}/user_list
    fi
    grep "${virtualuser}" ${vsftpd_conf_dir}/logins.txt >/dev/null 2>&1
    if [ $? -ne 0 ];then
        cat >> ${vsftpd_conf_dir}/logins.txt <<EOF
${virtualuser}
${virtualpasswd}
EOF
    fi 
    db_load -T -t hash -f ${vsftpd_conf_dir}/logins.txt ${vsftpd_conf_dir}/vsftpd_login.db
    mkdir -p ${vsftpd_conf_dir}/user_conf
    cat > ${vsftpd_conf_dir}/user_conf/${virtualuser} <<EOF
local_root=${virtualrootdir}
anon_world_readable_only=NO
write_enable=YES
anon_mkdir_write_enable=YES
anon_upload_enable=YES
anon_other_write_enable=YES
EOF
    if [ ! -e ${virtualrootdir} ];then
        mkdir -p ${virtualrootdir}
        chown -R ${ftpuser}:${ftpuser} ${virtualrootdir}
    else
        echo "${virtualrootdir} is exists.please check.If an error occurs, please use chown -R ${ftpuser}:${ftpuser} ${virtualrootdir}"
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

help_info() {
    echo -e "
Welcome to Master Linxw's ftp management tool. Please input the number to use these functions.
\t1  ftp install
\t2  add ftp vitural user
\tq  exit"
}

while true
do
    help_info
    read action
    case ${action} in
        1)
            vsftpd_install ${os_version}
            ftp_useradd ${ftpuser} ${ftppasswd} ${vsftpd_conf_dir} ${virtualuser} ${virtualpasswd} ${virtualrootdir}
            modify_ftp_conf ${root_dir} ${vsftpd_conf_dir} ${root_dir} ${ftphost}
            systemctl restart vsftpd
            ftpcheck
        ;;
        2)
            read -p "user name: " virtualuser
            read -p "user password: " virtualpasswd
            virtualrootdir="${root_dir}${virtualuser}"
            ftp_useradd ${ftpuser} ${ftppasswd} ${vsftpd_conf_dir} ${virtualuser} ${virtualpasswd} ${virtualrootdir}
            systemctl restart vsftpd
            ftpcheck
        ;;
        q)
            break
        ;;
        *)
            help_info
        ;;
    esac
done
echo "exit"
