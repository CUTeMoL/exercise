#!/bin/bash
#mysql要先完成免密登录，这一步可以使用
#     mysql_config_editor set --login-path=my3306 --user=root --socket=/tmp/mysql.sock --password
#用crontab -e定时运行此脚本
#1.用数组保存获取到的值
SLAVE_STATUS=(`mysql --login-path=my3306 -e 'show slave status\G'|awk 'BEGIN{FS=":"};/Slave_.*_Running:/{print $2}'`)
connection_time=0
mysql_log_slave=/mysqld/slave.log
#2.循环，正常就直接推出，失连就记录，不超过3次
while (( $connection_time < 3 ))
do
    if [ ${SLAVE_STATUS[0]} = Yes ] && [ ${SLAVE_STATUS[1]} = Yes ];then
        echo "`date '+%F %T'` Slave is running"  >> $mysql_log_slave
        exit
    elif [ ${SLAVE_STATUS[0]} = Connecting ];then
        let connection_time=connection_time+1
        echo "`date '+%F %T'` Slave disconnection $connection_time ." >> $mysql_log_slave
        sleep 5
    else
        echo "`date '+%F %T'` Slave status is working correctly ." >> $mysql_log_slave
        exit
    fi
done