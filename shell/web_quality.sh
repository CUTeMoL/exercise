#!bin/bash
#使用curl获取状态码  200正常
#例如:curl -s -o /dev/null --connect-timeout 3 -w "%{http_code}" http://www.baidu.com
# httplist.txt 存放需要检测的网址
cat httplist.txt | while read URL_LIST
do
    URL_FAIL=0
    for (( i=1;i<=3;i++))
    do
        HTTP_CODE=curl -s -o /dev/null --connect-timeout 3 -w "%{http_code}" $URL_LIST
        if [ $HTTP_CODE -eq 200 ];then
            echo "$URL_LIST is ok."
            break
        else
            let URL_FAIL++
        fi
    done
    if [ URL_FAIL -eq 3 ];then
        echo "$URL_LIST is failure"
    fi
done