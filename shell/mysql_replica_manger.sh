#!/bin/bash
# 基于mysql8.0.28-glibc版本
# 先免密登录mysql,或者要在脚本中的mysql命令行中使用-u -p 添加用户密码，只是这样会不够安全
# 推荐使用mysql_config_editor set --login-path=root_3306 --user=root --socket=/tmp/mysql_3306.sock --password来设置免密登录(仅使用此命令免密的用户有效)
# 之后就可以使用mysql --login-path=root_3306来登录实例

# 先在主库创建好同步用的用户
# 然后在从库主机上运行此脚本
# 根据情况修改变量

# master info
master_ipaddress=192.168.1.121
master_listen_port=3306
replica_user=replica
replica_passwd=123456

# slave info
slave_listen_port=3306
slave_login_user=root
slave_login_passwd=123456
slave_socket=/tmp/mysql_${slave_listen_port}.sock
slave_base_dir=/usr/local/mysql_${slave_listen_port} # 定义程序目录
slave_data_dir=/mysqld/data_${slave_listen_port} # 定义数据目录

gtid_flag=`${slave_base_dir}/bin/mysql --get-server-public-key -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show variables like \"gtid_mode\";" -s -N | awk '/gtid_mode/{print $2}'` >/dev/null 2>&1

gtid_replica() {
    master_ipaddress=$1
    master_listen_port=$2
    replica_user=$3
    replica_passwd=$4
    slave_base_dir=$5
    slave_login_user=$6
    slave_login_passwd=$7
    slave_socket=$8
    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "stop slave;" >/dev/null 2>&1
    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "reset slave;" >/dev/null 2>&1
    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e \
    "change master to master_host='${master_ipaddress}',master_port=${master_listen_port},\
    master_user='${replica_user}',master_password='${replica_passwd}',master_auto_position=1;" >/dev/null 2>&1
}

start_replica() {
    slave_base_dir=$1
    slave_login_user=$2
    slave_login_passwd=$3
    slave_socket=$4
    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "start slave;" >/dev/null 2>&1
}

check_replica() {
    slave_base_dir=$1
    master_ipaddress=$2
    master_listen_port=$3
    replica_user=$4
    replica_passwd=$5
    slave_login_user=$6
    slave_login_passwd=$7
    slave_socket=$8
    while true
    do
        slave_io_status=`${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show slave status\G" -s | grep "Slave_IO_Running:" | awk '{print $2}'` >/dev/null 2>&1
        slave_sql_status=`${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show slave status\G" -s | grep "Slave_SQL_Running:" |awk '{print $2}'` >/dev/null 2>&1
        if [[ ${slave_io_status} = No ]] && [[ ${slave_sql_status} = No ]];then
            ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "start slave;" >/dev/null 2>&1
        fi
        if [[ ${slave_io_status} = Connecting ]] && [[ ${slave_sql_status} = Yes ]];then
            io_error=`${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show slave status\G" -s | grep "Last_IO_Error:"` >/dev/null 2>&1
            echo "${io_error}"
            echo "${io_error}" | grep -o -e "Authentication plugin 'caching_sha2_password' reported error"
            if [[ $? = 0 ]];then
                ${slave_base_dir}/bin/mysql --get-server-public-key -h${master_ipaddress} -u${replica_user} -p${replica_passwd} -e "show databases;" >/dev/null 2>&1
                io_error=`${slave_base_dir}/bin/mysql --get-server-public-key -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show slave status\G" -s | grep "Last_IO_Error:"` >/dev/null 2>&1
                echo "${io_error}"
            fi
        fi
        if [[ ${slave_io_status} = Yes ]] && [[ ${slave_sql_status} = No ]];then
            sql_error=`${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "show slave status\G" -s | grep "Last_SQL_Error:"` >/dev/null 2>&1
            echo "${sql_error}"
            echo "${sql_error}" | grep -o -e "[0-9a-zA-Z]\{8\}-\([0-9A-Za-z]\{4\}-\)\{3\}[0-9a-zA-Z]\{12\}:[0-9A-Za-z]\{1,999\}" >/dev/null 2>&1
            if [[ $? = 0 ]];then
                sql_error_id=`echo "${sql_error}" | grep -o -e "[0-9a-zA-Z]\{8\}-\([0-9A-Za-z]\{4\}-\)\{3\}[0-9a-zA-Z]\{12\}:[0-9A-Za-z]\{1,999\}"`
                read -p "Do you want skip this error ${sql_error_id} (y/n): " error_skip_flag
                if [[ ${error_skip_flag} = y ]];then
                    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "stop slave;" >/dev/null 2>&1
                    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "SET GTID_NEXT=\"${sql_error_id}\";BEGIN;COMMIT;SET GTID_NEXT='AUTOMATIC'" >/dev/null 2>&1
                    ${slave_base_dir}/bin/mysql -S ${slave_socket} -u${slave_login_user} -p${slave_login_passwd} -e "start slave;" >/dev/null 2>&1
                else
                    echo "please use mysqlbinglog binlog.file | grep -A15 \"${sql_error_id}\" on master host"
                fi
            fi
        fi
        if [[ ${slave_io_status} = Yes ]] && [[ ${slave_sql_status} = Yes ]];then
            echo "Replication is running" && break
        fi
        sleep 5
    done
}

help_info() {
    echo -e "
Welcome to Master Lin's mysql management tool. Please input the number to use these functions.
\t1  mysql replica from master
\t2  check and repair mysql replication error
\tq  exit"
}

while true
do
    help_info
    read action
    case ${action} in 
        1)
            if [[ ${gtid_flag} = ON ]];then
                gtid_replica ${master_ipaddress} ${master_listen_port} ${replica_user} ${replica_passwd} ${slave_base_dir} ${slave_login_user} ${slave_login_passwd} ${slave_socket}
                start_replica ${slave_base_dir} ${slave_login_user} ${slave_login_passwd} ${slave_socket}
                sleep 10
                check_replica ${slave_base_dir} ${master_ipaddress} ${master_listen_port} ${replica_user} ${replica_passwd} 
            fi
        ;;
        2)
            check_replica ${slave_base_dir} ${master_ipaddress} ${master_listen_port} ${replica_user} ${replica_passwd} ${slave_login_user} ${slave_login_passwd} ${slave_socket}
        ;;
        q)
            break
        ;;
        *)
            help_info
        ;;
    esac
done
