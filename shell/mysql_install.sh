#!/bin/bash
# 修改以下变量
download_mysql_version=8.0.28 # 要安装的版本
mysql_listen_port=3306 # 端口
mysql_data_dir=/mysqld/data_${mysql_listen_port} # 数据目录
mysql_base_dir=/usr/local/mysql_${download_mysql_version} # 安装目录
serverid=10 # 集群id


init_environment() {
    data_dir=$1
    base_dir=$2
    rm -rf /etc/my.cnf /etc/mysql
    if [ -e ${base_dir}/bin ] || [ -e ${data_dir}/mysql ];then
        echo "mysql already exists. please check ${base_dir} and ${data_dir}" && exit
    fi
    `id mysql`  >/dev/null 2>&1
    if [ $? -ne 0 ];then
        useradd -r -s /sbin/nologin -M mysql  >/dev/null 2>&1
    fi
    mkdir -p /data/work ${data_dir}
    chown -R mysql:mysql /`echo ${data_dir} | awk -F "/" '{print $2}'`
    apt install libaio1 -y  >/dev/null 2>&1
}

download_mysql() {
    version=$1
    download_url=https://cdn.mysql.com/archives/mysql-${version:0:3}/mysql-${version}-linux-glibc2.12-x86_64.tar.xz  >/dev/null 2>&1
    if [ ! -e /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz ];then
        wget ${download_url} -O /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz
    else
        echo "mysql-${version}-linux-glibc2.12-x86_64.tar.xz already exists"
    fi
}

install_mysql() {
    version=$1
    data_dir=$2
    base_dir=$3
    mysql_port=$4
    server_id=$5
    tar -xf /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz -C /data/work/
    mv /data/work/mysql-${version}-linux-glibc2.12-x86_64 ${base_dir}
    mkdir -p ${base_dir}/mysql-files
    chown mysql:mysql ${base_dir}/mysql-files
    chmod 750 ${base_dir}/mysql-files
    ${base_dir}/bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql_${version} --datadir=${data_dir}
    ${base_dir}/bin/mysql_ssl_rsa_setup --datadir=${data_dir}
    cat > ${base_dir}/my.cnf <<EOF
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

# redolog
innodb_log_file_size=4G
innodb_log_buffer_size=32M

# undolog
innodb_undo_directory=${data_dir}/undospace/
innodb_undo_tablespaces=4
innodb_max_undo_log_size=4G

# binlog
binlog_format=row
sync_binlog=1
innodb_flush_log_at_trx_commit=1 
binlog_rows_query_log_events=1 
binlog_cache_size=64K
max_binlog_cache_size=2G
max_binlog_size=1024M
expire_logs_days=10
relay_log_recovery=1
relay_log_info_repository=TABLE
master_info_repository=TABLE
slave_parallel_type=logical_clock
slave_parallel_workers=8 
gtid_mode=on
log_slave_updates=1
enforce-gtid-consistency=1
relay_log_purge=1
EOF
    cat > /etc/my.cnf <<EOF
[client]
port=3306
socket=/tmp/mysql_${mysql_port}.sock
prompt="\u@\h: \R:\m[\d]> "
EOF
    mkdir ${data_dir}/undospace/
    mv ${data_dir}/undo_00* ${data_dir}/undospace/
    chown -R mysql:mysql ${data_dir}/undospace
    cp ${base_dir}/support-files/mysql.server /etc/init.d/mysqld_${mysql_port}
    sed -i -e "/^datadir=/s#datadir=#datadir=${data_dir}#g" \
    -e "/^basedir=/s#basedir=#basedir=${base_dir}#g" /etc/init.d/mysqld_${mysql_port}
    chmod +x /etc/init.d/mysqld_${mysql_port}
    systemctl daemon-reload
    echo "export PATH=\"\$PATH:${base_dir}/bin\"" >> /etc/profile
    if [ ! -e /lib/x86_64-linux-gnu/libtinfo.so.5 ];then
        if [ -e /lib/x86_64-linux-gnu/libtinfo.so.6.2 ];then
            ln -s /lib/x86_64-linux-gnu/libtinfo.so.6.2 /lib/x86_64-linux-gnu/libtinfo.so.5
        else
            echo "[error] please ln -s /lib/x86_64-linux-gnu/libtinfo.so.{version} /lib/x86_64-linux-gnu/libtinfo.so.5"
        fi
    fi
}

mysql_auto_start() {
    mysql_port=$1
    update-rc.d -f mysqld_${mysql_port} defaults
}

mysql_auto_start_disable() {
    mysql_port=$1
    update-rc.d -f mysqld_${mysql_port} remove
}


init_environment ${mysql_data_dir} ${mysql_base_dir}
download_mysql ${download_mysql_version}
install_mysql ${download_mysql_version} ${mysql_data_dir} ${mysql_base_dir} ${mysql_listen_port} ${serverid}
source /etc/profile
mysql_auto_start ${mysql_listen_port}

