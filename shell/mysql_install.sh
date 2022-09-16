#!/bin/bash
# 下载mysql
download_mysql_version=8.0.28
mysql_default_port=3306
mysql_data_dir=/mysqld/data_${mysql_default_port}
init_environment() {
    rm -rf /etc/my.cnf /etc/mysql
    `id mysql` &>>/dev/null
    if [ $? -ne 0 ];then
    useradd -r -s /sbin/nologin -M mysql
    fi
    mkdir -p /data/work $1
    chown -R mysql:mysql /mysqld
    apt install libaio1 -y

}

download_mysql() {
    version=$1
    download_usl=https://cdn.mysql.com/archives/mysql-${version:0:3}/mysql-${version}-linux-glibc2.12-x86_64.tar.xz -O /data/work/mysql-${version}-linux-glibc2.12-x86_64.tar.xz
}

decompression_mysql_files() {
    tar -xf /data/work/mysql-8.0.29-linux-glibc2.12-x86_64.tar.xz -C /usr/local/
}

# 安装环境配置



ln -s mysql-8.0.29-linux-glibc2.12-x86_64 mysql
cd mysql
mkdir mysql-files
chown mysql:mysql mysql-files
chmod 750 mysql-files
# 初始化安装
bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql --datadir=/mysqld/data >> /root/mysql-init.log
bin/mysql_ssl_rsa_setup --datadir=/mysqld/data
# 配置数据库
echo "[mysqld]
basedir=/usr/local/mysql
datadir=/mysqld/data
port=3306
socket=/tmp/mysql.sock
character_set_server=utf8mb4
collation_server=utf8mb4_general_ci
server_id=10
log-bin=/mysqld/data/binlog
[client]
port=3306
socket=/tmp/mysql.sock" >> /usr/local/mysql/my.cnf
# 服务添加mysql
cp support-files/mysql.server /etc/init.d/mysqld.server
sed -i "47s#datadir=#datadir=/mysqld/data#g" /etc/init.d/mysqld.server
chmod +x /etc/init.d/mysqld.server
systemctl daemon-reload
# 添加路径
echo 'export PATH="$PATH:/usr/local/mysql/bin"' >> /etc/profile
ln -s /lib/x86_64-linux-gnu/libtinfo.so.6.2 /lib/x86_64-linux-gnu/libtinfo.so.5
source /etc/profile
# 开机自启动
update-rc.d -f mysqld.server defaults
service mysqld.server start

init_environment ${mysql_data_dir}