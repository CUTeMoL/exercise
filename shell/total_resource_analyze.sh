#!/bin/bash
#CPU
function cpu(){
    util=$(vmstat|awk '{if(NR==3)print $13+$14}')
    iowait=$(vmstat|awk '{if(NR==3)print $16}')
    echo "CPU-使用率：${util}%,等待磁盘IO响应使用率：${iowait}%"
}
#内存
function memory(){
    total=$(free -m |awk '{if(NR==2)printf "%.1f", $2/1024}')
    used=$(free -m |awk '{if(NR==2)printf "%.1f",( $2-$NF)/1024}')
    available=$(free -m |awk '{if(NR==2)printf "%.1f", $NF/1024}')
    echo  "内存 - 总大小：${total}G,已使用：${used}G,剩余：${available}G"
}
#磁盘
function disk(){
    fs=$(df -h |awk '/^\/dev/{print $1}')
    for p in $fs;do
        disk_mounted=$(df -h|awk -v p=$p '$1==p{print $NF}')
        disk_size=$(df -h |awk -v p=$p '$1==p{print $2}')
        disk_used=$(df -h |awk -v p=$p '$1==p{print $3}')
        disk_used_percent=$(df -h |awk -v p=$p '$1==p{print $5}')
        echo "硬盘-挂载点：$disk_mounted,总大小：$disk_size,已使用：$disk_used,使用率：$disk_used_percent"
    done
}
tcp_status(){
    tcp_summary=$(netstat -antp|awk '{a[$6]++}END{for(i in a)printf i":"a[i]" "}')
    echo "TCP连接状态-$tcp_summary"
}
cpu
memory
disk
tcp_status