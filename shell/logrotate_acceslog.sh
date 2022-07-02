#!/bin/bash
#定义日志的基本目录
LOG_DIR=/usr/local/nginx/logs
#定义文件的基本名字
LOG_FILE_BASENAME=access.log
#按月份定义目录
LOG_MONTH_DIR=$LOG_DIR/$(date -d "yesterday" +"%Y-%m")
#定义昨天
YESTERDAY_TIME=$(date -d "yesterday" +%F)
for LOG_FILE in LOG_FILE_BASENAME;do
    [ ! -d $LOG_MONTH_DIR ] && mkdir -p $LOG_MONTH_DIR
    mv $LOG_DIR/$LOG_FILE_BASENAME $LOG_MONTH_DIR/${LOG_FILE_BASENAME}_${YESTERDAY_TIME}
done
kill -USR1 $(cat /usr/local/nginx/logs/nginx.pid)