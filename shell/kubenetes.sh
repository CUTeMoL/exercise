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

# 2.做好免密,运行脚本的机器必须能以ROOT账户免密登录各节点,脚本默认使用22端口

# 3.以ROOT用户运行此脚本

# 4.设定好变量
cluster_ips=193.169.0.0/16
pod_ips=10.10.0.0/16
cluster_DNS=193.169.0.2


cfssl_install() {
    rm -rf /bin/cfssl /bin/cfssljson /bin/cfssl-certinfo
    curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl_1.5.0_linux_amd64 -o /bin/cfssl >/dev/null 2>&1
    curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssljson_1.5.0_linux_amd64 -o /bin/cfssljson >/dev/null 2>&1
    curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl-certinfo_1.5.0_linux_amd64 -o /bin/cfssl-certinfo >/dev/null 2>&1
    chmod +x /bin/cfssl
    chmod +x /bin/cfssljson
    chmod +x /bin/cfssl-certinfo
}

cfssl_check() {
    while [ true ]
    do
        if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
            echo "[info] cfssl is ok" | tee -a /data/work/running.log && break
        else
            cfssl_install
            if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
                echo "[info] cfssl is ok" | tee -a /data/work/running.log && break
            else
                echo "[error] cfssl install is fail, please check cfssl"  | tee -a /data/work/running.log && exit
            fi
        fi
    done
}


generate_certificate_ca() {
    cfssl_check
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
        echo "[info] CA certificate is ok" | tee -a /data/work/running.log && return 0
    else
        echo "[error] please check CA certificate" | tee -a /data/work/running.log && exit 1
    fi
}

generate_certificate_etcd() {
    cfssl_check
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
        sed -i "/127.0.0.1/i\        \"$host_ipAddr\"," /data/work/etcd-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/etcd-csr.json | \
    /bin/cfssljson -bare /data/work/etcd 
    if [ $? -eq 0 ];then
        echo "[info] etcd certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "[error] please check etcd_cert " | tee -a /data/work/running.log
    fi
}

generate_TLS_Bootstrapping() {
    cat > /data/work/token.csv << EOF
`head -c 16 /dev/urandom | od -An -t x | tr -d ' '`,kubelet-bootstrap,10001,"system:bootstrapper"
EOF
}

generate_certificate_apiserver() {
    cat > /data/work/kube-apiserver-csr.json <<EOF
{
    "CN": "kubernetes",
    "hosts": [
        "127.0.0.1",
        "kubernetes",
        "kubernetes.default",
        "kubernetes.default.svc",
        "kubernetes.default.svc.cluster",
        "kubernetes.default.svc.cluster.local",
        "193.169.0.1"
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
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-apiserver-csr.json | \
    cfssljson -bare /data/work/kube-apiserver
    if [ $? -eq 0 ];then
        echo "[info] apiserver certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "[error] please check apiserver_cert " | tee -a /data/work/running.log
        exit 1
    fi
}


Environment_init() {
    mkdir /data/work -p
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
    for host in ${hosts[@]}
    do
        rsync -avz /etc/modules-load.d/k8s.conf $host:/etc/modules-load.d/k8s.conf>/dev/null 2>&1
        rsync -avz /etc/sysctl.d/k8s.conf $host:/etc/sysctl.d/k8s.conf >/dev/null 2>&1
        ssh $host "sysctl --system && modprobe ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh nf_conntrack_ipv4" >/dev/null 2>&1
        ssh $host "apt-get install ipvsadm -y && apt-get install net-tools -y" >/dev/null 2>&1
        ssh $host "mkdir -p /etc/kubernetes/ && /etc/kubernetes/ssl && /var/log/kubernetes"
    done
}



get_CA_cert() {
    if [ -e /data/work/ca.pem ] || [ -e /data/work/ca-key.pem ];then
        read -p "CA certificate is exists,if you want to generate new ca certificateplease input y: " flag
        if [[ $flag = y ]];then
            generate_certificate_ca >/dev/null 2>&1 && echo "[info] CA certificate renew" | tee -a /data/work/running.log
        else
            echo "[warning] CA certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_ca >/dev/null 2>&1 && echo "[info] CA certificate completed" | tee -a /data/work/running.log
    fi
}

get_etcd_cert() {
    if [ -e /data/work/etcd.pem ] || [ -e /data/work/etcd-key.pem ];then
        read -p "certificate_ca is exists, if you want to generate new ca certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_etcd ${etcds_ip[@]} >/dev/null 2>&1 && echo "[info] etcd certificate renew" | tee -a /data/work/running.log
        else
            echo "[warning] etcd certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_etcd ${etcds_ip[@]} >/dev/null 2>&1 && echo "[info] etcd certificate completed" | tee -a /data/work/running.log
    fi
}

get_tls_bootstrapping() {
    if [ -e /data/work/token.csv ];then
        read -p "TLS Bootstrapping token is existed,if you want to generate new? please input y: " flag
        if [ $ flag = y];then
            generate_TLS_Bootstrapping >/dev/null 2>&1 && echo "[info] TLS Bootstrapping token is renew" | tee -a /data/work/running.log
        else
            echo "[warning] TLS Bootstrapping token no change" | tee -a /data/work/running.log
        fi
    else
        generate_TLS_Bootstrapping >/dev/null 2>&1 && echo "[info] TLS Bootstrapping token is completed" | tee -a /data/work/running.log
    fi
}

main() {
    Environment_init
    cert_install
    get_CA_cert
    get_etcd_cert
    get_tls_bootstrapping
    # 却get_api_cert
}

main



for host in ${etcds[@]}
do
    ssh $i "mkdir -p /etc/etcd/ssl /var/lib/etcd "
done