#!/bin/bash
net_name=$1
while  true
do
    # 获取当前总流量
    net_receive_old=`grep "$net_name" /proc/net/dev |awk '{print $2}'`
    net_send_old=`grep "$net_name" /proc/net/dev |awk '{print $10}'`
    sleep 1
    # 1秒后再获取一次总流量
    net_receive_new=`grep "$net_name" /proc/net/dev |awk '{print $2}'`
    net_send_new=`grep "$net_name" /proc/net/dev |awk '{print $10}'`
    # 相减后得出每秒流量
    in_stream=$(printf "%.1f%s"  "$((($net_receive_new-$net_receive_old)/1024))"  "KB/S")
    out_stream=$(printf "%.1f%s"  "$((($net_send_new-$net_send_old)/1024))"  "KB/S")
    clear
    echo "stream   status"
    echo -e "进流量   $in_stream\n出流量   $out_stream"
    sleep 1
done