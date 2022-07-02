rsync -av --delete /app/java_project/ root@10.1.1.100:/backup/app1_java
#!/bin/bash
# 文件目录位置
MON_DIR=/opt
# 用inotifywait检测目录
inotifywait -mrq -e modify,delete,create,attrib,move $MON_DIR |while read events
do
        echo "`date +%F\ %T` 出现事件 $events" >> /log/dirModify.txt 2>&0
        rsync -av --delete $MON_DIR root@www.lxw.com:/backup
done