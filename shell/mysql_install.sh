#!/bin/bash
# 修改以下变量
download_mysql_version=8.0.28 # 要安装的版本
mysql_default_port=3306 # 端口
mysql_data_dir=/mysqld/data_${mysql_default_port} # 数据目录
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
        useradd -r -s /sbin/nologin -M mysql
    fi
    mkdir -p /data/work ${data_dir}
    chown -R mysql:mysql /`echo ${data_dir} | awk -F "/" '{print $2}'`
    apt install libaio1 -y
}

download_mysql() {
    version=$1
    download_url=https://cdn.mysql.com/archives/mysql-${version:0:3}/mysql-${version}-linux-glibc2.12-x86_64.tar.xz
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
    ${base_dir}/bin/mysqld --initialize --user=mysql --basedir=/usr/local//mysql_${version} --datadir=${data_dir} >> /root/mysql-init.log
    ${base_dir}/bin/mysql_ssl_rsa_setup --datadir=${data_dir}
    cat > ${base_dir}/my.cnf <<EOF
[mysqld]
basedir=${base_dir}
datadir=${data_dir}
port=${mysql_port}
socket=/tmp/mysql_${mysql_port}.sock
character_set_server=utf8mb4
collation_server=utf8mb4_general_ci
server_id=${server_id}
log-bin=${data_dir}/binlog
[client]
port=3306
socket=/tmp/mysql_${mysql_port}.sock
EOF
    cp ${base_dir}/support-files/mysql.server /etc/init.d/mysqld.server
    sed -i -e "/^datadir=/s#datadir=#datadir=${data_dir}#g" \
    -e "/^basedir=/s#basedir=#basedir=${base_dir}#g" /etc/init.d/mysqld.server
    chmod +x /etc/init.d/mysqld.server
    systemctl daemon-reload
    echo "export PATH=\"\$PATH:${base_dir}/bin\"" >> /etc/profile
    if [ ! -e /lib/x86_64-linux-gnu/libtinfo.so.5 ];then
        if [ -e /lib/x86_64-linux-gnu/libtinfo.so.6.2 ];then
            ln -s /lib/x86_64-linux-gnu/libtinfo.so.6.2 /lib/x86_64-linux-gnu/libtinfo.so.5
        else
            echo "[error] please ln -s /lib/x86_64-linux-gnu/libtinfo.so.version /lib/x86_64-linux-gnu/libtinfo.so.5"
        fi
    fi
}

mysql_auto_start() {
    update-rc.d -f mysqld.server defaults
}

mysql_auto_start_disable() {
    update-rc.d -f mysqld.server remove
}


init_environment ${mysql_data_dir} ${mysql_base_dir}
download_mysql ${download_mysql_version}
install_mysql ${download_mysql_version} ${mysql_data_dir} ${mysql_base_dir} ${mysql_default_port} ${serverid}
source /etc/profile
mysql_auto_start

