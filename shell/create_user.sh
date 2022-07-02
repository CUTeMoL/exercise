#!/bin/bash
#创建用户
cat user.txt|while read USER
do
    if ! id $USER &>/dev/null; then
        passwd_value=`echo $RANDOM | md5sum | cut -c 1-8`
        useradd $USER
        echo $passwd_value | passwd --stdin $USER
        echo "$USER    $passwd_value"  >>created_user.txt
        echo "$USER create successful"
    else
        echo "$USER already exists"
    fi
done
