#!/bin/bash
# 基于UBUNTU-20.04
# 要求
# 1.编辑好/etc/hosts,此脚本集群(除etcd外)的前缀要有k,用m表示master节点,用n表示node节点,例如
# 127.0.0.1 localhost
# 192.168.1.101 k-m1
# 192.168.1.101 etcd1
# 192.168.1.102 k-m2
# 192.168.1.102 etcd2
# 192.168.1.103 k-m3
# 192.168.1.103 etcd3
# 192.168.1.104 k-n1
# 192.168.1.105 k-n2
# 192.168.1.106 k-n3
# 192.168.1.107 virtual_ip
# 如果想自定义集群名称,那么可以根据实际情况编写能获取到主机名称和ip地址的数组
hosts=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "k-[a-zA-Z][0-9]\{1,3\}" `)
masters=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "k-m[0-9]\{1,3\}" `)
nodes=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "k-n[0-9]\{1,3\}" `)
etcds=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -o -e "etcd[0-9]\{1,3\}" `)

hosts_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-[a-zA-Z][0-9]\{1,3\}" | awk '{print $1}' `)
masters_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-m[0-9]\{1,3\}" | awk '{print $1}' `)
nodes_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-n[0-9]\{1,3\}" | awk '{print $1}' `)
etcds_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "etcd[0-9]\{1,3\}" | awk '{print $1}' `)
virtual_ip=`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep virtual_ip | awk '{print $1}'`

# 2.做好免密,运行脚本的机器必须能以ROOT账户免密登录各节点,脚本默认使用22端口

# 3.以ROOT用户运行此脚本

# 4.设定好集群信息相关变量
etcd_version=v3.4.20
etcd_url=http://150.158.93.164/files
# 目前仅上传了etcdv3.4.20到150.158.93.164的服务器上之后会添加新版本
cluster_ips=193.169.0.0/16
pod_ips=10.10.0.0/16
cluster_ip=193.169.0.1
cluster_DNS=193.169.0.2


cfssl_install() {
    rm -rf /bin/cfssl /bin/cfssljson /bin/cfssl-certinfo
    wget http://150.158.93.164/files/cfssl.tar.gz -O /data/work/cfssl.tar.gz
    tar -zxf /data/work/cfssl.tar.gz -C /bin
    chmod +x /bin/cfssl
    chmod +x /bin/cfssljson
    chmod +x /bin/cfssl-certinfo
}

cfssl_check() {
    while [ true ]
    do
        if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
            echo "`date \"+%F %T \"`[info] cfssl is ok" | tee -a /data/work/running.log && break
        else
            cfssl_install
            if [ -x /bin/cfssl ] && [ -x /bin/cfssljson ] && [ -x /bin/cfssl-certinfo ];then
                echo "`date \"+%F %T \"`[info] cfssl is ok" | tee -a /data/work/running.log && break
            else
                echo "`date \"+%F %T \"`[error] cfssl install is fail, please check cfssl"  | tee -a /data/work/running.log && exit
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
        echo "`date \"+%F %T \"`[info] The CA certificate is ok" | tee -a /data/work/running.log && return 0
    else
        echo "`date \"+%F %T \"`[error] please check CA certificate" | tee -a /data/work/running.log && exit 1
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
    /bin/cfssljson -bare /data/work/etcd  >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The etcd certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check etcd_cert " | tee -a /data/work/running.log
    fi
}

generate_TLS_Bootstrapping() {
    cat > /data/work/token.csv << EOF
`head -c 16 /dev/urandom | od -An -t x | tr -d ' '`,kubelet-bootstrap,10001,"system:bootstrapper"
EOF
}

generate_certificate_apiserver() {
    cfssl_check
    cat > /data/work/kube-apiserver-csr.json <<EOF
{
    "CN": "kubernetes",
    "hosts": [
        "127.0.0.1",
        "kubernetes",
        "kubernetes.default",
        "kubernetes.default.svc",
        "kubernetes.default.svc.cluster",
        "kubernetes.default.svc.cluster.local"
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
        sed -i "/127.0.0.1/a\        \"$host_ipAddr\"," /data/work/kube-apiserver-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-apiserver-csr.json | \
    /bin/cfssljson -bare /data/work/kube-apiserver >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The apiserver certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check apiserver_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

generate_certificate_kubectl() {
    cfssl_check
    cat > /data/work/admin-csr.json <<EOF
{
    "CN": "admin",
    "hosts": [],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "ShangHai",
            "L": "ShangHai",
            "O": "system:masters",
            "OU": "system"
        }
    ]
}
EOF
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/admin-csr.json | \
    /bin/cfssljson -bare /data/work/admin >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kubectl certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check kubectl_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

generate_certificate_kubecontrollermanager() {
    cfssl_check
    cat > /data/work/kube-controller-manager-csr.json <<EOF
{
    "CN": "system:kube-controller-manager",
    "key":{
        "algo": "rsa",
        "size": 2048
    },
    "hosts": [
        "127.0.0.1"
    ],
    "names": [
        {
            "C": "CN",
            "ST": "ShangHai",
            "L": "ShangHai",
            "O": "system:kube-controller-manager",
            "OU": "system"
        }
    ]
}
EOF
    for host_ipAddr in $@
    do
        sed -i "/127.0.0.1/i\        \"$host_ipAddr\"," /data/work/kube-controller-manager-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/kube-controller-manager-csr.json | \
    /bin/cfssljson -bare /data/work/kube-controller-manager
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kube-controller-manager certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check kube-controller-manager_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

generate_certificate_kubescheduler() {
    cfssl_check
    cat > /data/work/kube-scheduler-csr.json<<EOF
{
    "CN": "system:kube-scheduler",
    "key":{
        "algo": "rsa",
        "size": 2048
    },
    "hosts": [
        "127.0.0.1"
    ],
    "names": [
        {
            "C": "CN",
            "ST": "ShangHai",
            "L": "ShangHai",
            "O": "system:kube-scheduler",
            "OU": "system"
        }
    ]
}
EOF
    for host_ipAddr in $@
    do
        sed -i "/127.0.0.1/i\        \"$host_ipAddr\"," /data/work/kube-scheduler-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/kube-scheduler-csr.json | \
    /bin/cfssljson -bare /data/work/kube-scheduler
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kube-scheduler certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check kube-scheduler_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

generate_certificate_kube_proxy() {
    cfssl_check
    cat > /data/work/kube-proxy-csr.json<<EOF
{
    "CN": "system:kube-proxy",
    "key":{
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
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/kube-proxy-csr.json | /bin/cfssljson -bare /data/work/kube-proxy
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kube-proxy certificate is ok" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check kube-proxy_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

etcd_install() {
    ETCD_VER=$1
    shift
    ETCD_URL=$1
    shift
    DOWNLOAD_URL=${ETCD_URL}
    rm -rf /data/work/etcd-${ETCD_VER}-linux-amd64.tar.gz /data/work/etcd-${ETCD_VER}-linux-amd64
    wget ${DOWNLOAD_URL}/etcd-${ETCD_VER}-linux-amd64.tar.gz -P /data/work/ && \
    tar -zxf /data/work/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /data/work/ >/dev/null 2>&1
    for host in $@
    do
        ssh $host "mkdir -p /etc/etcd/ssl"
        rsync -avz /data/work/etcd-${ETCD_VER}-linux-amd64/etcd* $host:/usr/local/bin/ >/dev/null 2>&1
    done
}

generate_etcd_conf() {
    cat > /data/work/etcd.conf <<EOF
#[Member]
ETCD_NAME="etcd_name"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://host_ip:2380"
ETCD_LISTEN_CLIENT_URLS="https://host_ip:2379,https://127.0.0.1:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://host_ip:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://host_ip:2379"
ETCD_INITIAL_CLUSTER=""
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
    cat  > /data/work/etcd.service <<EOF
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
EnvironmentFile=/etc/etcd/etcd.conf
WorkingDirectory=/var/lib/etcd/
ExecStart=/usr/local/bin/etcd \\
--cert-file=/etc/etcd/ssl/etcd.pem \\
--key-file=/etc/etcd/ssl/etcd-key.pem \\
--trusted-ca-file=/etc/etcd/ssl/ca.pem \\
--peer-cert-file=/etc/etcd/ssl/etcd.pem \\
--peer-key-file=/etc/etcd/ssl/etcd-key.pem \\
--peer-trusted-ca-file=/etc/etcd/ssl/ca.pem \\
--client-cert-auth \\
--peer-client-cert-auth
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
    sed -e "s#etcd_name#$1#g" -e "s#host_ip#$2#g" /data/work/etcd.conf > /data/work/etcd-$1.conf
    sed -i "/ETCD_INITIAL_CLUSTER=/s#\"\$#$3\"#g" /data/work/etcd-$1.conf
    chmod +x /data/work/etcd.service
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
    for host in $@
    do
        /usr/bin/expect <<EOF
            spawn ssh $host "mkdir -p /etc/kubernetes/ && /etc/kubernetes/ssl && /var/log/kubernetes"
            expect { 
                "yes/no" { send "yes\r" }
            }
            expect eof
EOF
        rsync -avz /etc/modules-load.d/k8s.conf $host:/etc/modules-load.d/k8s.conf >/dev/null 2>&1
        rsync -avz /etc/sysctl.d/k8s.conf $host:/etc/sysctl.d/k8s.conf >/dev/null 2>&1
        ssh $host "sysctl --system && modprobe ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh nf_conntrack_ipv4" >/dev/null 2>&1
        ssh $host "apt-get install ipvsadm -y && apt-get install net-tools -y" >/dev/null 2>&1
    done
}



get_CA_cert() {
    if [ -e /data/work/ca.pem ] || [ -e /data/work/ca-key.pem ];then
        read -p "The CA certificate already exists,if you want to generate new ca certificateplease input y: " flag
        if [[ $flag = y ]];then
            generate_certificate_ca >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The CA certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The CA certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_ca >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The CA certificate is completed" | tee -a /data/work/running.log
    fi
}

get_etcd_cert() {
    if [ -e /data/work/etcd.pem ] || [ -e /data/work/etcd-key.pem ];then
        read -p "The certificate_ca already exists, if you want to generate new ca certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_etcd ${etcds_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The etcd certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The etcd certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_etcd ${etcds_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The etcd certificate is completed" | tee -a /data/work/running.log
    fi
}

get_tls_bootstrapping() {
    if [ -e /data/work/token.csv ];then
        read -p "TLS Bootstrapping token already exists,if you want to generate new? please input y: " flag
        if [ $ flag = y];then
            generate_TLS_Bootstrapping >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] TLS Bootstrapping token is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] TLS Bootstrapping token no change" | tee -a /data/work/running.log
        fi
    else
        generate_TLS_Bootstrapping >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] TLS Bootstrapping token is completed" | tee -a /data/work/running.log
    fi
}

get_apiserver_cert() {
    if [ -e /data/work/kube-apiserver.pem ] || [ -e /data/work/kube-apiserver-key.pem ];then
        read -p "The certificate_kube-apiserver already exists, if you want to generate new kube-apiserver certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_apiserver ${masters_ip[@]} ${cluster_ip} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-apiserver certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The kube-apiserver certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_apiserver ${masters_ip[@]} ${cluster_ip} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-apiserver certificate is completed" | tee -a /data/work/running.log
    fi
}

get_kubectl_cert() {
    if [ -e /data/work/admin.pem ] || [ -e /data/work/admin-key.pem ];then
        read -p "The certificate kuberctl already exists, if you want to generate new kubectl certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_kubectl >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kubectl certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The kubectl certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_kubectl >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kubectl certificate is completed" | tee -a /data/work/running.log
    fi
}

get_kube_controller_manager_cert() {
    if [ -e /data/work/kube-controller-manager.pem ] || [ -e /data/work/kube-controller-manager-key.pem ];then
        read -p "The certificate kube-controller-manager already exists, if you want to generate new kube-controller-manager certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_kubecontrollermanager ${masters_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-controller-manager certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The kube-controller-manager certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_kubecontrollermanager ${masters_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-controller-manager certificate is completed" | tee -a /data/work/running.log
    fi
}

get_kube_scheduler_cert() {
    if [ -e /data/work/kube-scheduler.pem ] || [ -e /data/work/kube-scheduler-key.pem ];then
        read -p "The certificate kube-scheduler already exists, if you want to generate new kube-scheduler certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_kubescheduler ${masters_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-scheduler certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The kube-scheduler certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_kubescheduler ${masters_ip[@]} >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-scheduler certificate is completed" | tee -a /data/work/running.log
    fi
}

get_kube_proxy_cert() {
    if [ -e /data/work/kube-proxy.pem ] || [ -e /data/work/kube-proxy-key.pem ];then
        read -p "The certificate kube-proxy already exists, if you want to generate new kube-proxy certificate, please input y: " flag
        if [ $flag = y ];then
            generate_certificate_kube_proxy >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-proxy certificate is renew" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[warning] The kube-proxy certificate is no change" | tee -a /data/work/running.log
        fi
    else
        generate_certificate_kube_proxy >/dev/null 2>&1 && echo "`date \"+%F %T \"`[info] The kube-proxy certificate is completed" | tee -a /data/work/running.log
    fi
}



get_etcd() {
    etcd_install $@ >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The etcd is installed" | tee -a /data/work/running.log
        return 0
    else
        echo "`date \"+%F %T \"`[error] please check etcd " | tee -a /data/work/running.log
        exit 1
    fi
}



put_etcd_conf() {
    for host in $@
    do
        host_ipAddr=`ping $host -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        etcd_inital_cluster=`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "etcd[0-9]\{1,3\}" | awk '{print $2"=https://"$1":2380"}'|awk 'BEGIN{RS="\n";ORS=","};{print $0}'| sed 's#,$##g'`
        generate_etcd_conf $host $host_ipAddr $etcd_inital_cluster
        rsync -avz /data/work/etcd-${host}.conf $host:/etc/etcd/etcd.conf >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The $host etcd.conf is transfer completed" | tee -a /data/work/running.log
            return 0
        else
            echo "`date \"+%F %T \"`[error] please check $host:/etc/etcd/etcd.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/etcd.service $host:/lib/systemd/system/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The $host etcd.service is transfer completed" | tee -a /data/work/running.log
            return 0
        else
            echo "`date \"+%F %T \"`[error] please check $host:/lib/systemd/system/etcd.service" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

update_etcd_cert() {
    for host in $@
    do
        rsync -avz /data/work/ca*.pem $host:/etc/etcd/ssl/ || echo "`date \"+%F %T \"`[error] update $host etcd ca certificate is failed" | tee -a /data/work/running.log
        rsync -avz /data/work/etcd*.pem $host:/etc/etcd/ssl/ || echo "`date \"+%F %T \"`[error] update $host etcd certificate is failed" | tee -a /data/work/running.log
        echo "`date \"+%F %T \"`[info] update $host etcd certificate is completed" | tee -a /data/work/running.log
    done
}

etcd_check() {
    if [ ! -e /usr/local/bin/etcdctl ];then
        apt install etcd-client -y
        etcd_client=`which etcdctl`
    else
        etcd_client=/usr/local/bin/etcdctl
    fi
    for host in $@
    do
        check_result=`ETCDCTL_API=3 ${etcd_client} \
        --write-out=fields \
        --cacert=/etc/etcd/ssl/ca.pem \
        --cert=/etc/etcd/ssl/etcd.pem \
        --key=/etc/etcd/ssl/etcd-key.pem \
        --endpoints=https://$host:2379 \
        endpoint health | grep "Health" | awk '{print $3}'`
        if [ $check_result = true ];then
            echo "`date \"+%F %T \"`[info] etcd-cluster:$host is healthy" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check etcd-cluster:$host health" | tee -a /data/work/running.log
        fi
    done
}

etcd_service_restart() {
    for host in $@
    do
        ssh $host "systemctl daemon-reload && systemctl enable etcd && systemctl restart etcd"
    done
}

for host in ${etcds[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh $host "mkdir -p /etc/etcd/ssl /var/lib/etcd "
        expect { 
            "yes/no" { send "yes\r" }
        }
        expect eof
EOF
done

for host in ${masters[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh $host "mkdir -p /etc/kubernetes/ssl "
        expect { 
            "yes/no" { send "yes\r" }
        }
        expect eof
EOF
done

for host in ${nodes[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh $host "mkdir -p /etc/kubernetes/ssl "
        expect { 
            "yes/no" { send "yes\r" }
        }
        expect eof
EOF
done

Environment_init ${hosts[@]}
cert_install
get_CA_cert
get_etcd_cert
get_tls_bootstrapping
get_apiserver_cert
get_kubectl_cert
get_kube_controller_manager_cert
get_kube_scheduler_cert
get_kube_proxy_cert
get_etcd ${etcd_version} ${etcd_url} ${etcds[@]}
put_etcd_conf ${etcds[@]}
update_etcd_cert ${etcds[@]}
etcd_check ${etcds[@]}
etcd_service_restart ${etcds[@]}
