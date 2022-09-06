#!/bin/bash
# 基于UBUNTU-20.04
# 要求
# 1.编辑好/etc/hosts,例如
# 127.0.0.1 localhost
# 192.168.1.101 k-m1 etcd1
# 192.168.1.102 k-m2 etcd2
# 192.168.1.103 k-m3 etcd3
# 192.168.1.104 k-n1
# 192.168.1.105 k-n2
# 192.168.1.106 k-n3

# 根据实际情况编写主机名称和ip地址的数组
hosts=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | awk '{print $2}' `)
masters=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "k-m[0-9]\{1,3\}" `)
nodes=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "k-n[0-9]\{1,3\}" `)
etcds=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "etcd[0-9]\{1,3\}" `)

hosts_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | awk '{print $1}' `)
masters_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-m[0-9]\{1,3\}" | awk '{print $1}' `)
nodes_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-n[0-9]\{1,3\}" | awk '{print $1}' `)
etcds_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "etcd[0-9]\{1,3\}" | awk '{print $1}' `)

# 2.做好免密,运行脚本的机器必须能以ROOT账户免密登录各节点

# 3.以ROOT用户运行此脚本




cert_install() {
    while [ true ]
    do
        if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
            echo "cfssl is ok" && break
        else
            rm -rf /bin/cfssl /bin/cfssljson /bin/cfssl-certinfo
            curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl_1.5.0_linux_amd64 -o /bin/cfssl >/dev/null 2>&1
            curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssljson_1.5.0_linux_amd64 -o /bin/cfssljson >/dev/null 2>&1
            curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl-certinfo_1.5.0_linux_amd64 -o /bin/cfssl-certinfo >/dev/null 2>&1
            chmod +x /bin/cfssl
            chmod +x /bin/cfssljson
            chmod +x /bin/cfssl-certinfo
            if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
                echo "cfssl is ok" && break
            else
                echo "cfssl install is fail, please check cfssl " && exit
            fi
        fi
    done
}

generate_certificate_ca(){
    cat > /data/work/ca-config.json <<EOF
{
    "signing": {
        "default": {
            "expiry": "876000h"
        },
        "profiles": {
            "kubernetes": {
                "usages": [
                    "signing",
                    "key encipherment",
                    "server auth",
                    "client auth"
                ],
                "expiry": "876000h"
            }
        }
    }
}
EOF
    cat > /data/work/ca-csr.json <<EOF
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "ShangHai",
      "L": "ShangHai",
      "O": "k8s",
      "OU": "system"
    }
  ],
  "ca": {
      "expiry": "876000h"
  }
}
EOF
    /bin/cfssl gencert -initca /data/work/ca-csr.json | /bin/cfssljson -bare /data/work/ca >/dev/null 2>&1 
    if [ $? -eq 0 ];then
        echo "CA certificate is ok" 
    else
        echo "please check CA certificate " && exit
    fi
}

generate_certificate_etcd(){
    cat > /data/work/etcd-csr.json <<EOF
{
    "CN": "etcd",
    "hosts": [
        "127.0.0.1"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "ShangHai",
            "L": "ShangHai",
            "O": "k8s",
            "OU": "system"
        }
    ]
}
EOF
    for host_ipAddr in $@
    do
        sed -i "/127.0.0.1/i\ \ \ \ \ \ \ \ \"$host_ipAddr\"," /data/work/etcd-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/etcd-csr.json | \
    /bin/cfssljson -bare /data/work/etcd 
    if [ $? -eq 0 ];then
        echo "etcd certificate is ok" 
        return 0
    else
        echo "please check etcd_cert " 
        exit 1
    fi
}


mkidr /data/work -p
cat > /etc/modules-load.d/k8s.conf <<EOF
br_netfilter
overlay
ip_vs
ip_vs_rr
ip_vs_wrr
ip_vs_sh
nf_conntrack_ipv4
EOF
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF


cert_install

if [ -e /data/work/ca.pem ] || [ -e /data/work/ca-key.pem ];then
    read -p "CA certificate is exists,if you want to generate new ca certificateplease input y: " flag
    if [[ $flag = y ]];then
        generate_certificate_ca >/dev/null 2>&1 && echo "CA certificate completed"
    else
        echo "CA certificate no change"
    fi
else
    generate_certificate_ca >/dev/null 2>&1 && echo "CA certificate completed"
fi

if [ -e /data/work/etcd.pem ] || [ -e /data/work/etcd-key.pem ];then
    read -p "certificate_ca is exists, if you want to generate new ca certificate, please input y" flag
    if [ $flag = y ];then
        generate_certificate_ctcd ${etcds_ip[@]} >/dev/null 2>&1 && echo "etcd certificate completed"
    else
        echo "etcd certificate no change"
    fi
else
    generate_certificate_etcd ${etcds_ip[*]} >/dev/null 2>&1 && echo "etcd certificate completed"
fi



for host in ${hosts[@]}
do
    rsync -avz /etc/modules-load.d/k8s.conf $i:/etc/modules-load.d/k8s.conf>/dev/null 2>&1
    rsync -avz /etc/sysctl.d/k8s.conf $i:/etc/sysctl.d/k8s.conf >/dev/null 2>&1
    ssh $i "sysctl --system && modprobe ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh nf_conntrack_ipv4" >/dev/null 2>&1
    ssh $i "apt-get install ipvsadm -y && apt-get install net-tools -y" >/dev/null 2>&1
    ssh $i "mkdir -p /etc/kubernetes/ && /etc/kubernetes/ssl && /var/log/kubernetes"
done

for host in ${etcds[@]}
do
    ssh $i "mkdir -p /etc/etcd/ssl /var/lib/etcd "
done