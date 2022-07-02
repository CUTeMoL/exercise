#!/bin/bash
#提取IP前十
echo "-----IP访问最多前十-----"
awk 'BEGIN{FS="|"};{print $1}' /usr/local/nginx/logs/access.log |sort |uniq -c|sort -nr -k 1|head -n 10
#另一种awk 'BEGIN{FS="|"};{a[$1]++}END{for (v in a)print v,a[v]}' /usr/local/nginx/logs/access.log

echo "-----访问最多的页面前十-----"
awk 'BEGIN{FS="|"};{print $5}' /usr/local/nginx/logs/access.log |awk '{print $1"\t"$2}'|sort -k1|uniq -c|sort -nr|head -n 10

echo "-----访问最多状态码前十-----"
awk 'BEGIN{FS="|"};{print $6}' /usr/local/nginx/logs/access.log |sort |uniq -c |sort -nr|head -n 10
#另一种awk 'BEGIN{FS="|"};{a[$6]++;}END{for (v in a)print v,a[v]}' /usr/local/nginx/logs/access.log|sort -nr -k2

###一定期间的统计###
# $BEGIN_TIME='17-Feb-2022:15:00:00'
# $END_TIME='17-Feb-2022:17:00:00'
# awk 'BEGIN{FS="|"};{print $1"\t"$3}' /usr/local/nginx/logs/access.log |sed 's/\//-/g'|awk '$2>="$BEGIN_TIME" && $2<="$END_TIME"{print $1}'|sort|uniq -c
#时间一定要放入awk中，不能使用变量
#最终版
BEGIN_TIME='17022022170000'
END_TIME='17022022180000'
awk 'BEGIN{FS="|"};{print $1"\t"$3}' /usr/local/nginx/logs/access.log |sed 's/\//-/g'|sed 's#:#-#g'|sed 's#Feb#02#g'|awk '{print $1"\t"$2}'|sed 's/-//g'|awk -v BEGIN_TIME=$BEGIN_TIME 'BEGIN_TIME<=$2{print $0}'|awk -v END_TIME=$END_TIME 'END_TIME>$2{print $1}'|sort |uniq -c|sort -nr
