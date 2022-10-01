#!/bin/bash
# 2022.10.1更新,优化多实例
# # 修改basedir路径,使得不同实例可以使用相同的basedir,节省磁盘空间
# # 修改my.cnf路径,方便多实例管理
# 适用于mysqld 5.7/8.0
# 修改以下变量
download_mysql_version=8.0.28 # 要安装的版本
mysql_listen_port=3306 # 此实例监听的端口(影响socket、数据目录、配置文件路径、服务名)
mysql_data_dir=/mysqld/data_${mysql_listen_port} # 数据目录
mysql_base_dir=/usr/local/mysql_${download_mysql_version} # 安装目录
mysql_conf_dir=/mysqld/etc_${mysql_listen_port} # 配置文件路径
serverid=10 # 集群id
root_passwd=123456 # 安装完成后将root密码修改为此字符串

init_environment() {
    data_dir=$1
    base_dir=$2
    os_version=$3
    if [[ ${os_version} = CentOS ]];then
        yum install libncurses* -y >/dev/null 2>&1
    elif [[ ${os_version} = Ubuntu ]];then
        apt install libaio1 -y >/dev/null 2>&1
    else
        echo "This system is not supported" && exit
    fi
    if [ -e /etc/my.cnf ] || [ -e /etc/mysql ];then
        echo "/etc/my.cnf or /etc/mysql already exists, Please confirm whether to keep these files."
        read -p "If you want to delete these files please input y: " action
        if [[ ${action} = y ]];then
            rm -rf /etc/my.cnf /etc/mysql && echo "/etc/my.cnf or /etc/mysql already deleted"
        fi
    fi
    if [ -e ${data_dir}/mysql ];then
        echo "mysql already exists. please check ${data_dir}" && exit
    fi
    id mysql >/dev/null 2>&1
    if [ $? -ne 0 ];then
        useradd -r -s /sbin/nologin -M mysql  >/dev/null 2>&1
    fi
    mkdir -p /data/work ${data_dir}
    chown -R mysql:mysql /`echo ${data_dir} | awk -F "/" '{print $2}'`
}

download_mysql() {
    version=$1
    if [[ ${version:0:3} = 8.0 ]];then
        download_url=https://cdn.mysql.com/archives/mysql-${version:0:3}/mysql-${version}-linux-glibc2.12-x86_64.tar.xz >/dev/null 2>&1
    else
        download_url=https://cdn.mysql.com/archives/mysql-${version:0:3}/mysql-${version}-linux-glibc2.12-x86_64.tar.gz >/dev/null 2>&1
    fi
    if [ ! -e /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz ] && [[ ${version:0:3} = 8.0 ]];then
        wget ${download_url} -O /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz
        if [ $? -ne 0 ];then
            echo "download mysql-${version}-linux-glibc2.12-x86_64.tar.xz is failed" && exit
        fi
    elif [ ! -e /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.gz ];then
        wget ${download_url} -O /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.gz
        if [ $? -ne 0 ];then
            echo "download mysql-${version}-linux-glibc2.12-x86_64.tar.gz is failed" && exit
        fi
    else
        echo "mysql-${version}-linux-glibc2.12-x86_64.tar.gz already exists"
    fi
}

install_mysql() {
    version=$1
    data_dir=$2
    base_dir=$3
    mysql_port=$4
    server_id=$5
    os_version=$6
    mysql_conf_dir=$7
    if [ ! -e ${base_dir} ];then
        if [ -e /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz ] && [[ ${version:0:3} = 8.0 ]];then
            tar -xf /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz -C /data/work/
        elif [ -e /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.gz ];then
            tar -zxf /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.gz -C /data/work/
        else
            download_mysql ${version}
            echo "Downloading mysql-${version}-glibc-install package,when download is completed,please run this script again."
            exit
        fi
        mv /data/work/mysql-${version}-linux-glibc2.12-x86_64 ${base_dir}
        mkdir -p ${base_dir}/mysql-files
        chown -R mysql:mysql ${base_dir}
        chmod 750 ${base_dir}/mysql-files
    else
        echo "${base_dir} already exists"
    fi
    mkdir -p ${mysql_conf_dir}
    cat > ${mysql_conf_dir}/my.cnf <<EOF
[mysqld]
# base
basedir=${base_dir}
datadir=${data_dir}
port=${mysql_port}
socket=/tmp/mysql_${mysql_port}.sock
character_set_server=utf8mb4
collation_server=utf8mb4_general_ci
server_id=${server_id}
log-bin=${data_dir}/binlog
log_timestamps=SYSTEM
transaction_isolation=READ-COMMITTED
open_files_limit=65535
innodb_open_files=65535
skip_name_resolve=1
back_log=500
max_connections=2048
innodb_io_capacity=4000
innodb_io_capacity_max=8000
sort_buffer_size=4M
join_buffer_size=4M
tmp_table_size=32M
max_heap_table_size=32M
read_buffer_size=8M
bulk_insert_buffer_size=64M
myisam_sort_buffer_size=128M
key_buffer_size=2048M
max_allowed_packet=64M

# redolog
innodb_log_file_size=4G
innodb_log_buffer_size=32M

# undolog
innodb_undo_directory=${data_dir}/undospace/
innodb_undo_tablespaces=4
innodb_max_undo_log_size=4G

# replica
binlog_format=row
sync_binlog=1
innodb_flush_log_at_trx_commit=1
binlog_rows_query_log_events=1
binlog_cache_size=64K
max_binlog_cache_size=2G
max_binlog_size=1024M
relay_log_recovery=1
relay_log_info_repository=TABLE
master_info_repository=TABLE
gtid_mode=on
enforce-gtid-consistency=1
relay_log_purge=1

[mysqld-5.7]
# replica
expire_logs_days=10
slave_parallel_type=logical_clock
slave_parallel_workers=8 
log_slave_updates=1

[mysqld-8.0]
# base
mysqlx=OFF

# replica
binlog_expire_logs_seconds=864000
replica_parallel_type=LOGICAL_CLOCK
replica_parallel_workers=8
log_replica_updates=1
EOF
    chown -R mysql:mysql ${mysql_conf_dir}
    if [ ! -e /etc/my.cnf ] && [ ! -e /etc/mysql ];then
        cat > /etc/my.cnf <<EOF
[mysql]
port=3306
socket=/tmp/mysql_${mysql_port}.sock
prompt="mysql>\u@\h:[\d]# "

[mysqldump]
max_allowed_packet=64M

[mysqladmin]
port=3306
socket=/tmp/mysql_${mysql_port}.sock
EOF
    chown -R mysql:mysql /etc/my.cnf
    else
        echo "/etc/my.cnf or /etc/mysql already exists,please check them."
    fi
    ${base_dir}/bin/mysqld --defaults-file=${mysql_conf_dir}/my.cnf --initialize --user=mysql 2>&1 | tee -a /tmp/my_install_${mysql_port}.log
    ${base_dir}/bin/mysql_ssl_rsa_setup --datadir=${data_dir}
    if [ -e ${data_dir}/undo_001 ];then
        mkdir ${data_dir}/undospace/ -p
        mv ${data_dir}/undo_00* ${data_dir}/undospace/
    elif [ -e ${data_dir}/undo001 ];then
        mkdir ${data_dir}/undospace/ -p
        mv ${data_dir}/undo00* ${data_dir}/undospace/
    fi
    chown -R mysql:mysql ${data_dir}
    cp ${base_dir}/support-files/mysql.server /etc/init.d/mysqld_${mysql_port}
    sed -i -e "/^datadir=/s#datadir=#datadir=${data_dir}#g" \
    -e "/^other_args=/s#other_args=\"\$\*\"#other_args=\"\`\$basedir/bin/my_print_defaults --defaults-extra-file=${mysql_conf_dir}/my.cnf mysqld\` \$\*\"#g" \
    -e "/^basedir=/s#basedir=#basedir=${base_dir}#g" /etc/init.d/mysqld_${mysql_port}
    chmod +x /etc/init.d/mysqld_${mysql_port}
    systemctl daemon-reload
    grep "export PATH=\"\$PATH:${base_dir}/bin\"" /etc/profile >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "export PATH=\"\$PATH:${base_dir}/bin\"" >> /etc/profile
    fi
    if [[ ${os_version} = Ubuntu ]];then
        if [ ! -e /lib/x86_64-linux-gnu/libtinfo.so.5 ];then
            if [ -e /lib/x86_64-linux-gnu/libtinfo.so.6 ];then
                ln -s /lib/x86_64-linux-gnu/libtinfo.so.6 /lib/x86_64-linux-gnu/libtinfo.so.5
                ln -s /lib/x86_64-linux-gnu/libncurses.so.6 /lib/x86_64-linux-gnu/libncurses.so.5
            else
                echo "[error] please ln -s /lib/x86_64-linux-gnu/libtinfo.so.{version} /lib/x86_64-linux-gnu/libtinfo.so.5"
            fi
        fi
    else
        if [ ! -e /lib64/libtinfo.so.5 ];then
            if [ -e /lib64/libtinfo.so.6 ];then
                ln -s /lib64/libtinfo.so.6 /lib64/libtinfo.so.5
                ln -s /lib64/libncurses.so.6 /lib64/libncurses.so.5
            else
                echo "[error] please ln -s /lib64/libtinfo.so.{version} /lib64/libtinfo.so.5"
            fi
        fi
    fi
    service mysqld_${mysql_port} start
    if [ $? -ne 0 ];then
        echo "[error] please check ${data_dir}/`hostname`.err"
    fi
}

mysql_auto_start() {
    mysql_port=$1
    os_version=$2
    if [[ ${os_version} = Ubuntu ]];then
        update-rc.d -f mysqld_${mysql_port} defaults
    else
        chkconfig --add mysqld_${mysql_port}
    fi
}

mysql_auto_start_disable() {
    mysql_port=$1
    os_version=$2
    if [[ ${os_version} = Ubuntu ]];then
        update-rc.d -f mysqld_${mysql_port} remove
    else
        chkconfig --del mysqld_${mysql_port}
    fi
}

help_info() {
    echo -e "
Welcome to Master Lin's mysql management tool. Please input the number to use these functions.
\t1  mysql install
\t2  mysql start up at boot
\t3  mysql do not start up at boot
\t4  check configuration
\tq  exit"
}

if [ -e /etc/issue ] && [ ! -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/issue`
elif [ -e /etc/issue ] && [ -e /etc/redhat-release ];then
    os_version=`awk '1{print$1}' /etc/redhat-release`
else
    echo "This system is not supported" && break
fi
check_configuration() {
    os_version=$1
    mysql_version=$2
    data_dir=$3
    base_dir=$4
    mysql_port=$5
    server_id=$6
    mysql_conf=$7
    echo -e "\
please check configuration \
\n  os_version: ${os_version} \
\n  mysql_version: ${mysql_version} \
\n  mysqldatadir: ${data_dir} \
\n  mysql_basedir: ${base_dir} \
\n  listen_port: ${mysql_port} \
\n  server_id: ${server_id} \
\n  my.cnf: ${mysql_conf_dir}"
    read -p "Do you confirm these configuration(y/n): " action
    if [[ ${action} != y ]];then
        echo "[warning] please modify $0 configuration." && exit
    fi
}

change_random_passwd() {
    mysql_port=$1
    root_passwd=$2
    grep "root@localhost:" /tmp/my_install_${mysql_port}.log
    if [ $? -eq 0 ];then 
        random_passwd=`awk '/root@localhost:/{print $NF}' /tmp/my_install_${mysql_port}.log`
        ${mysql_base_dir}/bin/mysql --connect-expired-password -S /tmp/mysql_${mysql_port}.sock -p${random_passwd} \
        -e "ALTER USER 'root'@localhost IDENTIFIED BY \"${root_passwd}\";"
    else
        echo "[error] please check /tmp/my_install_${mysql_listen_port}.log"
    fi
}

check_configuration ${os_version} ${download_mysql_version} ${mysql_data_dir} ${mysql_base_dir} ${mysql_listen_port} ${serverid}
while true
do
    help_info
    read action
    case ${action} in
        1)
            init_environment ${mysql_data_dir} ${mysql_base_dir} ${os_version} 
            download_mysql ${download_mysql_version}
            install_mysql ${download_mysql_version} ${mysql_data_dir} ${mysql_base_dir} ${mysql_listen_port} ${serverid} ${os_version} ${mysql_conf_dir}
            change_random_passwd ${mysql_listen_port} ${root_passwd}
        ;;
        2)
            mysql_auto_start ${mysql_listen_port} ${os_version} 
        ;;
        3)
            mysql_auto_start_disable ${mysql_listen_port} ${os_version} 
        ;;
        4)
            check_configuration ${os_version} ${download_mysql_version} ${mysql_data_dir} ${mysql_base_dir} ${mysql_listen_port} ${serverid} ${mysql_conf_dir}
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
