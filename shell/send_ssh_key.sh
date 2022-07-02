#!/bin/bash
[ -f /root/.ssh/id_rsa ] || ssh-keygen -P "" -f /root/.ssh/id_rsa
# 从文件中获取hostIP port user password
cat SSHList.txt|while read SERVER_IP SSHD_PORT LOGIN_NAME SSH_PASSWD
do
    ping -c1 $SERVER_IP
    if [ $? -eq 0 ];then
        touch /root/ssh_up.txt
        /usr/bin/expect <<-END
        spawn ssh-copy-id -p $SSHD_PORT $LOGIN_NAME@$SERVER_IP
        expect { 
            "yes/no" { send "yes\r";exp_continue }
            "password:" { send "$SSH_PASSWD\r" }
        }
        expect eof
        END
        echo "$(date +%F) 完成向 $SERVER_IP 发送公钥" >> /root/ssh_up.txt
    else
        touch /root/ssh_down.txt
        echo "$(date +%F) $SERVER_IP 无法连接" >> /root/ssh_down.txt
    fi
done
cat /root/ssh_up.txt /root/ssh_down.txt