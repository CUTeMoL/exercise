#!/bin/bash
mysql_port=3306
mysql_socket=`ps -ef | grep -e "--port=${mysql_port}" | grep -v "grep"| grep -o -e "--socket=.*\.sock" | awk -F "=" '{print $2}'`
mysql_datadir=`ps -ef | grep -e "port=${mysql_port}" | grep -v "grep" | grep -o -w -e "datadir=.*" | awk '{print $1}' | awk -F"=" '{print$2}'`
mysql_basedir=`ps -ef | grep -e "port=${mysql_port}" | grep -v "grep" | grep -o -w -e "basedir=.*" | awk '{print $1}' | awk -F"=" '{print$2}'`
mysqldump_version=`${mysql_basedir}/bin/mysqldump --version|grep -o -e "[0-9]\.[0-9].[0-9]\{1,3\}"`
passwd=123456

mysqldump_alldatabase_backup() {
    mysql_port=$1
    mysql_socket=$2
    mysql_basedir=$3
    mysql_datadir=$4
    mysqldump_version=$5
    passwd=$6
    mkdir -p /data/backup_${mysql_port}
    if [[ ${mysqldump_version:0:3} = 5.7 ]];then
        ${mysql_basedir}/bin/mysqldump -S ${mysql_socket} -uroot -p${passwd} --single-transaction --master-data=1 -R --triggers -E --all-databases |\
        gzip -c > /data/backup_${mysql_port}/`date +%F`.tgz
        if [ $? -eq 0 ];then
            tar -zcPf /data/backup_${mysql_port}/binlog`date +%F`.tar.gz ${mysql_datadir}/binlog.*
            echo "[info] backup is completed.please check /data/backup_${mysql_port}/`date +%F`.tgz or binlog`date +%F`.tar.gz"
        else
            echo "[error] all database backup failed"
        fi
    elif [[ ${mysqldump_version:0:3} = 8.0 ]];then
        ${mysql_basedir}/bin/mysqldump -S ${mysql_socket} -uroot -p${passwd} --single-transaction --source-data=1 -R --triggers -E --all-databases |\
        gzip -c > /data/backup_${mysql_port}/`date +%F`.tgz
        if [ $? -eq 0 ];then
            tar -zcPf /data/backup_${mysql_port}/binlog`date +%F`.tar.gz ${mysql_datadir}/binlog.*
            echo "[info] backup is completed.please check /data/backup_${mysql_port}/`date +%F`.tgz or binlog`date +%F`.tar.gz"
        else
            echo "[error] all database backup failed."
        fi
    else
        echo "This version is not supported" && exit 1
    fi
}
mysqldump_alldatabase_backup ${mysql_port} ${mysql_socket} ${mysql_basedir} ${mysql_datadir} ${mysqldump_version} ${passwd}