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
etcd_url=http://150.158.93.164/files/etcd/${etcd_version}
kubernetes_version=v1.23.10
kubernetes_url=http://150.158.93.164/files/kubernetes/${kubernetes_version}
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
        echo "`date \"+%F %T \"`[info] The CA certificate is ok" | tee -a /data/work/running.log
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
        sed -i "/127.0.0.1/i\        \"${host_ipAddr}\"," /data/work/etcd-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/etcd-csr.json | \
    /bin/cfssljson -bare /data/work/etcd  >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The etcd certificate is ok" | tee -a /data/work/running.log
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
        sed -i "/127.0.0.1/a\        \"${host_ipAddr}\"," /data/work/kube-apiserver-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem \
    -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-apiserver-csr.json | \
    /bin/cfssljson -bare /data/work/kube-apiserver >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The apiserver certificate is ok" | tee -a /data/work/running.log
    else
        echo "`date \"+%F %T \"`[error] please check apiserver certificate " | tee -a /data/work/running.log
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
        sed -i "/127.0.0.1/i\        \"${host_ipAddr}\"," /data/work/kube-controller-manager-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/kube-controller-manager-csr.json | \
    /bin/cfssljson -bare /data/work/kube-controller-manager
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kube-controller-manager certificate is ok" | tee -a /data/work/running.log
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
        sed -i "/127.0.0.1/i\        \"${host_ipAddr}\"," /data/work/kube-scheduler-csr.json
    done
    /bin/cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json \
    -profile=kubernetes /data/work/kube-scheduler-csr.json | \
    /bin/cfssljson -bare /data/work/kube-scheduler
    if [ $? -eq 0 ];then
        echo "`date \"+%F %T \"`[info] The kube-scheduler certificate is ok" | tee -a /data/work/running.log
    else
        echo "`date \"+%F %T \"`[error] please check kube-scheduler_cert " | tee -a /data/work/running.log
        exit 1
    fi
}

generate_certificate_kube_proxy() {
    cfssl_check
    cat > /data/work/kube-proxy-csr.json <<EOF
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
        ssh ${host} "mkdir -p /etc/etcd/ssl"
        rsync -avz /data/work/etcd-${ETCD_VER}-linux-amd64/etcd* ${host}:/usr/local/bin/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} etcd is installed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} etcd or network" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

kube_install() {
    kubernetes_url=$1
    download_url=${kubernetes_url}
    shift
    rm -rf /data/work/kubernetes-server-linux-amd64.tar.gz /data/work/kubernetes_url
    wget ${kubernetes_url}/kubernetes-server-linux-amd64.tar.gz -P /data/work/ && \
    tar -zxf /data/work/kubernetes-server-linux-amd64.tar.gz -C /data/work/ >/dev/null 2>&1
    k8sdir=/data/work/kubernetes/server/bin
    for host in $@
    do
        rsync -avz ${k8sdir}/kube-apiserver ${k8sdir}/kube-controller-manager ${k8sdir}/kube-scheduler ${k8sdir}/kubectl \
        ${k8sdir}/kubelet ${k8sdir}/kube-proxy ${host}:/usr/local/bin/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kubernetes is installed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} kubernetes_file or network" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

keepalived_install() {
    for host in $@
    do
        ssh ${host} "apt install keepalived -y"
    done
}

docker_install() {
    for host in $@
    do
        ssh ${host} "apt remove docker docker-engine docker.io containerd runc -y" >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} docker is removed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} network" | tee -a /data/work/running.log
            exit 1
        fi
        ssh ${host} "apt-get update && sudo apt-get install ca-certificates curl gnupg lsb-release"
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} ca-certificates curl gnupg lsb-release is installed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} network" | tee -a /data/work/running.log
            exit 1
        fi
        ssh ${host} "mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -"
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} apt-key is added" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} network" | tee -a /data/work/running.log
            exit 1
        fi
        ssh ${host} "add-apt-repository \"deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" && apt-get update"
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} apt-repository is added" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} network" | tee -a /data/work/running.log
            exit 1
        fi
        ssh ${host} "apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y"
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} docker is installed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host} network" | tee -a /data/work/running.log
            exit 1
        fi
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

generate_apiserver_conf() {
    cat > /data/work/kube-apiserver.service <<EOF
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes
After=etcd.service
Wants=etcd.service

[Service]
EnvironmentFile=/etc/kubernetes/kube-apiserver.conf
ExecStart=/usr/local/bin/kube-apiserver \$KUBE_APISERVER_OPTS
Restart=on-failure
RestartSec=5
Type=notify
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
chmod +x /data/work/kube-apiserver.service
    cat > /data/work/kube-apiserver.conf <<EOF
KUBE_APISERVER_OPTS="--enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \\
--anonymous-auth=false \\
--bind-address=host_ip \\
--secure-port=6443 \\
--advertise-address=host_ip \\
--insecure-port=0 \\
--authorization-mode=Node,RBAC \\
--requestheader-client-ca-file=/etc/kubernetes/ssl/ca.pem \\
--proxy-client-cert-file=/etc/kubernetes/ssl/kube-proxy.pem \\
--proxy-client-key-file=/etc/kubernetes/ssl/kube-proxy-key.pem \\
--requestheader-allowed-names=aggregator \\
--requestheader-extra-headers-prefix=X-Remote-Extra- \\
--requestheader-group-headers=X-Remote-Group \\
--requestheader-username-headers=X-Remote-User \\
--enable-aggregator-routing=true \\
--runtime-config=api/all=true \\
--enable-bootstrap-token-auth=true \\
--service-cluster-ip-range=cluster_ips \\
--token-auth-file=/etc/kubernetes/token.csv \\
--service-node-port-range=30000-50000 \\
--tls-cert-file=/etc/kubernetes/ssl/kube-apiserver.pem \\
--tls-private-key-file=/etc/kubernetes/ssl/kube-apiserver-key.pem \\
--client-ca-file=/etc/kubernetes/ssl/ca.pem \\
--kubelet-client-certificate=/etc/kubernetes/ssl/kube-apiserver.pem \\
--kubelet-client-key=/etc/kubernetes/ssl/kube-apiserver-key.pem \\
--service-account-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--service-account-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--service-account-issuer=https://kubernetes.default.svc.cluster.local \\
--etcd-cafile=/etc/etcd/ssl/ca.pem \\
--etcd-certfile=/etc/etcd/ssl/etcd.pem \\
--etcd-keyfile=/etc/etcd/ssl/etcd-key.pem \\
--etcd-servers=etcd_hosts \\
--enable-swagger-ui=true \\
--allow-privileged=true \\
--apiserver-count=3 \\
--audit-log-maxage=30 \\
--audit-log-maxbackup=3 \\
--audit-log-maxsize=100 \\
--audit-log-path=/var/log/kube-apiserver-audit.log \\
--event-ttl=1h \\
--alsologtostderr=true \\
--logtostderr=false \\
--log-dir=/var/log/kubernetes \\
--v=4"
EOF
    sed -e "s#host_ip#$2#g" -e "s#cluster_ips#$3#g" -e "/etcd-servers=/s#etcd_hosts#$4#g" /data/work/kube-apiserver.conf > /data/work/kube-apiserver-$1.conf
}

generate_keepalived_conf() {
    cat > /data/work/keepalived.conf <<EOF
! Configuration File for keepalived
global_defs {
   notification_email {
     acassen@firewall.loc
     failover@firewall.loc
     sysadmin@firewall.loc
   }
   notification_email_from Alexandre.Cassen@firewall.loc
   smtp_server 192.168.200.1
   smtp_connect_timeout 1
   script_user root
   enable_script_security
   router_id LVS_DEVEL
}
vrrp_script check_service {
   script  /etc/keepalived/check_service.sh
   interval 3
}
vrrp_instance VI_1 {
    state BACKUP
    interface if_name
    virtual_router_id 51
    priority 80
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 123456
    }
    virtual_ipaddress {
        virtual_ipAddr
    }
    unicast_src_ip host_ip
    unicast_peer {
    }
    track_script {
        check_service
    }
}
EOF
    masters_ip=(`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "k-m[0-9]\{1,3\}" | awk '{print $1}' `)
    sed -e "s#if_name#$2#g" -e "s#host_ip#$3#g" -e "s#virtual_ipAddr#$4#g" /data/work/keepalived.conf > /data/work/keepalived-$1.conf
    for peer_ip in ${masters_ip[@]}
    do
        if [ $peer_ip != $3 ];then
            sed -i "/unicast_peer {/a\        $peer_ip" /data/work/keepalived-$1.conf
        fi
    done
    cat > /data/work/check_service.sh <<EOF
#!/bin/bash
haproxy_status=\`ps -C haproxy --no-header | wc -l\`
n=0
while [ $n -lt 3 ]
do
    if [ \$haproxy_status -eq 0 ];then
        let n=n+1
        if [ n -eq 3 ]
            service keepalived stop
        fi
        sleep 10
    else
        exit
    fi
done
EOF
    chmod +x /data/work/check_service.sh
}

generate_haproxy_conf() {
    cat > /data/work/haproxy.cfg <<EOF
global
    log /dev/log    local0
    log /dev/log    local1 notice
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    chroot /var/lib/haproxy
    user haproxy
    group haproxy
    daemon

defaults
    mode tcp
    log global
    retries 3
    timeout connect 10s
    timeout client 20s
    timeout server 30s
    timeout check 5s
    timeout http-keep-alive 10s
    timeout queue 1m
    timeout http-request 10s
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

frontend haproxy-apiserver
    bind *:8443
    mode tcp
    default_backend kube-apiserver

backend kube-apiserver
    mode tcp
    balance roundrobin
    
listen admin_stats
    bind *:9188
    mode http
    log 127.0.0.1 local0 err
    stats refresh 30s
    stats uri /haproxy-status
    stats realm welcome login\ HAProxy
    stats auth root:123456
    stats hide-version
    stats admin if TRUE
EOF
    for backend in $@
    do
        host_ipAddr=`ping ${backend} -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        backend_apiserver="server ${backend} ${host_ipAddr}:6443 check inter 2000 rise 2 fall 3 weight 1"
        sed -i "/balance roundrobin/a\    ${backend_apiserver}" /data/work/haproxy.cfg
    done
}

generate_kubectl_conf() {
    if [ ! -e /data/work/ca.pem ] || [ ! -e /data/work/ca-key.pem ];then
        echo "`date \"+%F %T \"`[error]generate_kubectl_conf is failed. The ca certificate is no found" | tee -a /data/work/running.log
        exit 1
    else
        if [ -e /data/work/admin.pem ] && [ ! -e /data/work/admin-key.pem ];then
            kubectl config set-cluster kubernetes \
            --certificate-authority=/data/work/ca.pem \
            --embed-certs=true \
            --server=https://$1:8443 \
            --kubeconfig=/data/work/kube.config
            kubectl config set-credentials admin \
            --client-certificate=/data/work/admin.pem \
            --client-key=/data/work/admin-key.pem \
            --embed-certs=true \
            --kubeconfig=/data/work/kube.config
            kubectl config set-context kubernetes \
            --cluster=kubernetes \
            --user=admin \
            --kubeconfig=/data/work/kube.config
            kubectl config use-context kubernetes \
            --kubeconfig=/data/work/kube.config
            echo "`date \"+%F %T \"`[info] generate_kubectl_conf is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error]generate_kubectl_conf is failed. The admin.pem is no found" | tee -a /data/work/running.log
            exit 1
        fi
    fi
}

generate_kube_controller_manager_conf() {
    if [ ! -e /data/work/ca.pem ] || [ ! -e /data/work/ca-key.pem ];then
        echo "`date \"+%F %T \"`[error] generate_kube_controller_manager_conf is failed. The ca certificate is no found" | tee -a /data/work/running.log
        exit 1
    else
        cat > /data/work/kube-controller-manager.service <<EOF
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes
[Service]
EnvironmentFile=/etc/kubernetes/kube-controller-manager.conf
ExecStart=/usr/local/bin/kube-controller-manager \$KUBE_CONTROLLER_MANAGER_OPTS


Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
        chmod +x /data/work/kube-controller-manager.service
        cat > /data/work/kube-controller-manager.conf<<EOF
KUBE_CONTROLLER_MANAGER_OPTS="--v=2 \\
--log-dir=/var/log/kubernetes \\
--alsologtostderr=true \\
--logtostderr=false \\
--secure-port=10257 \\
--cluster-name=kubernetes \\
--feature-gates=RotateKubeletServerCertificate=true \\
--controllers=*,bootstrapsigner,tokencleaner \\
--tls-cert-file=/etc/kubernetes/ssl/kube-controller-manager.pem \\
--tls-private-key-file=/etc/kubernetes/ssl/kube-controller-manager-key.pem \\
--use-service-account-credentials=true \\
--leader-elect=true \\
--kubeconfig=/etc/kubernetes/kube-controller-manager.kubeconfig \\
--bind-address=127.0.0.1 \\
--allocate-node-cidrs=true \\
--cluster-cidr=$1 \\
--service-cluster-ip-range=$2 \\
--cluster-signing-cert-file=/etc/kubernetes/ssl/ca.pem \\
--cluster-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--root-ca-file=/etc/kubernetes/ssl/ca.pem \\
--service-account-private-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--cluster-signing-duration=87600h0m0s"
EOF
        if [ -e /data/work/kube-controller-manager.pem ] && [ -e /data/work/kube-controller-manager-key.pem ];then
            kubectl config set-cluster kubernetes \
            --certificate-authority=/data/work/ca.pem \
            --embed-certs=true \
            --server=https://$3:8443 \
            --kubeconfig=/data/work/kube-controller-manager.kubeconfig
            kubectl config set-credentials system:kube-controller-manager \
            --client-certificate=/data/work/kube-controller-manager.pem \
            --client-key=/data/work/kube-controller-manager-key.pem \
            --embed-certs=true \
            --kubeconfig=/data/work/kube-controller-manager.kubeconfig
            kubectl config set-context system:kube-controller-manager \
            --cluster=kubernetes \
            --user=system:kube-controller-manager \
            --kubeconfig=/data/work/kube-controller-manager.kubeconfig
            kubectl config use-context system:kube-controller-manager \
            --kubeconfig=/data/work/kube-controller-manager.kubeconfig
            echo "`date \"+%F %T \"`[info] The generate_kube_controller_manager_conf is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error]generate_kube_controller_manager_conf is failed. The kube-controller-manager certificate is no found" | tee -a /data/work/running.log
            exit 1
        fi
    fi
}

generate_kube_scheduler_conf() {
    if [ ! -e /data/work/ca.pem ] || [ ! -e /data/work/ca-key.pem ];then
        echo "`date \"+%F %T \"`[error] generate_kube_scheduler_conf is failed. The ca certificate is no found" | tee -a /data/work/running.log
        exit 1
    else
        cat > /data/work/kube-scheduler.service<<EOF
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes
[Service]
EnvironmentFile=/etc/kubernetes/kube-scheduler.conf
ExecStart=/usr/local/bin/kube-scheduler \$KUBE_SCHEDULER_OPTS

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        cat > /data/work/kube-scheduler.conf<<EOF
KUBE_SCHEDULER_OPTS=" \\
--address=127.0.0.1 \\
--kubeconfig=/etc/kubernetes/kube-scheduler.kubeconfig \\
--leader-elect=true \\
--alsologtostderr=true \\
--logtostderr=false \\
--log-dir=/var/log/kubernetes \\
--v=2"
EOF
        if [ -e /data/work/kube-scheduler.pem ] && [ -e /data/work/kube-scheduler-key.pem ];then
            kubectl config set-cluster kubernetes \
            --certificate-authority=/data/work/ca.pem \
            --embed-certs=true \
            --server=https://$1:8443 \
            --kubeconfig=/data/work/kube-scheduler.kubeconfig

            kubectl config set-credentials system:kube-scheduler \
            --client-certificate=/data/work/kube-scheduler.pem \
            --client-key=/data/work/kube-scheduler-key.pem \
            --embed-certs=true \
            --kubeconfig=/data/work/kube-scheduler.kubeconfig

            kubectl config set-context system:kube-scheduler \
            --cluster=kubernetes \
            --user=system:kube-scheduler \
            --kubeconfig=/data/work/kube-scheduler.kubeconfig

            kubectl config use-context system:kube-scheduler \
            --kubeconfig=/data/work/kube-scheduler.kubeconfig
        else
            echo "`date \"+%F %T \"`[error]generate_kube_scheduler_conf is failed. The kube-scheduler certificate is no found" | tee -a /data/work/running.log
            exit 1
        fi
    fi
}

generate_kubelet_conf() {
    if [ ! -e /data/work/ca.pem ] || [ ! -e /data/work/ca-key.pem ];then
        echo "`date \"+%F %T \"`[error] generate_kubelet_conf is failed. The ca certificate is no found" | tee -a /data/work/running.log
        exit 1
    else
        if [ ! -e /data/work/token.csv ];then
            echo "`date \"+%F %T \"`[error] generate_kubelet_conf is failed. The token file is no found" | tee -a /data/work/running.log
            exit 1
        else
            kubectl config set-cluster kubernetes \
            --certificate-authority=/data/work/ca.pem \
            --embed-certs=true \
            --server=https://$1:8443 \
            --kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
            kubectl config set-credentials kubelet-bootstrap \
            --token=`awk -F , '{print $1}' /data/work/token.csv` \
            --kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
            kubectl config set-context default \
            --cluster=kubernetes \
            --user=kubelet-bootstrap \
            --kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
            kubectl config use-context default \
            --kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
            cat > /data/work/kubelet.conf << EOF
KUBELET_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/var/log/kubernetes \\
--network-plugin=cni \\
--kubeconfig=/etc/kubernetes/kubelet.kubeconfig \\
--bootstrap-kubeconfig=/etc/kubernetes/kubelet-bootstrap.kubeconfig \\
--config=/etc/kubernetes/kubelet.yaml \\
--cert-dir=/etc/kubernetes/ssl \\
--alsologtostderr=true \
--logtostderr=false \
--pod-infra-container-image=docker.io/gotok8s/pause:3.7"
EOF
            cat > /data/work/kubelet.yaml <<EOF
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
address: "host_ip"
port: 10250
failSwapOn: false
serializeImagePulls: false
evictionHard:
  memory.available:  "10%"
  nodefs.available:  "10%"
  nodefs.inodesFree: "10%"
  imagefs.available: "10%"
authentication:
  x509:
    clientCAFile: "/etc/kubernetes/ssl/ca.pem"
  webhook:
    enabled: true
    cacheTTL: "2m"
  anonymous:
    enabled: false
authorization:
  mode: "Webhook"
  webhook:
    cacheAuthorizedTTL: "5m"
    cacheUnauthorizedTTL: "30s"
readOnlyPort: 10255
cgroupDriver: "cgroupfs"
hairpinMode: "promiscuous-bridge"
serializeImagePulls: false
featureGates: 
  RotateKubeletServerCertificate: true
serverTLSBootstrap: true
clusterDomain: "cluster.local"
clusterDNS: 
  - "cluster_dns"
EOF
            sed -e "s#host_ip#$3#g" -e "s#cluster_dns#$4#g" /data/work/kubelet.yaml > /data/work/kubelet-$2.yaml
            cat > /data/work/kubelet.service << EOF
[Unit]
Description=Kubernetes Kubelet
Documentation=https://github.com/kubernetes/kubernetes
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/var/lib/kubelet
EnvironmentFile=/etc/kubernetes/kubelet.conf
ExecStart=/usr/local/bin/kubelet \$KUBELET_OPTS

Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
            chmod +x /data/work/kubelet.service
        fi
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
    for host in $@
    do
        /usr/bin/expect <<EOF
            spawn ssh ${host} "mkdir -p /etc/kubernetes/ /etc/kubernetes/ssl /var/log/kubernetes /etc/etcd/ssl"
            expect { 
                "yes/no" { send "yes\r" }
            }
            expect eof
EOF
        rsync -avz /etc/modules-load.d/k8s.conf ${host}:/etc/modules-load.d/k8s.conf >/dev/null 2>&1
        rsync -avz /etc/sysctl.d/k8s.conf ${host}:/etc/sysctl.d/k8s.conf >/dev/null 2>&1
        ssh ${host} "sysctl --system && modprobe ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh nf_conntrack_ipv4" >/dev/null 2>&1
        ssh ${host} "apt-get install ipvsadm -y && apt-get install net-tools -y" >/dev/null 2>&1
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

put_etcd_conf() {
    for host in $@
    do
        host_ipAddr=`ping ${host} -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        etcd_inital_cluster=`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "etcd[0-9]\{1,3\}" | awk '{print $2"=https://"$1":2380"}'|awk 'BEGIN{RS="\n";ORS=","};{print $0}'| sed 's#,$##g'`
        generate_etcd_conf ${host} ${host_ipAddr} $etcd_inital_cluster
        rsync -avz /data/work/etcd-${host}.conf ${host}:/etc/etcd/etcd.conf >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} etcd.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/etcd/etcd.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/etcd.service ${host}:/lib/systemd/system/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} etcd.service is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/lib/systemd/system/etcd.service" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_apiserver_conf() {
    cluster_ips=$1
    shift
    for host in $@
    do
        host_ipAddr=`ping ${host} -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        etcd_cluster=`grep -v "^#" /etc/hosts |grep -v "localhost" | grep -v "^$" | grep -e "etcd[0-9]\{1,3\}" | awk '{print "https://"$1":2379"}'|awk 'BEGIN{RS="\n";ORS=","};{print $0}'| sed 's#,$##g'`
        generate_apiserver_conf ${host} ${host_ipAddr} ${cluster_ips} ${etcd_cluster}
        rsync -avz /data/work/kube-apiserver-${host}.conf ${host}:/etc/kubernetes/kube-apiserver.conf >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-apiserver.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-apiserver.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kube-apiserver.service ${host}:/lib/systemd/system/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-apiserver.service is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/lib/systemd/system/kube-apiserver.service" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_keepalived_conf() {
    virtual_ip=$1
    shift
    for host in $@
    do
        if_name=`ssh ${host} "ifconfig" |grep -B1 -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"|grep -iw "UP"|grep -iv "LOOPBACK"|awk -F ":" '{print$1}'|grep -e "^e"`
        host_ipAddr=`ping ${host} -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        generate_keepalived_conf ${host} ${if_name} ${host_ipAddr} ${virtual_ip}
        rsync -avz /data/work/keepalived-${host}.conf ${host}:/etc/keepalived/keepalived.conf >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} keepalived.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/keepalived/keepalived.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/check_service.sh ${host}:/etc/keepalived/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} check_service.sh is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/keepalived/check_service.sh" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_haproxy_conf() {
    generate_haproxy_conf $@
    for host in $@
    do
        ssh ${host} "[ -e /etc/haproxy/haproxy.cfg ] && mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg`date +%F_%T`"
        rsync -avz /data/work/haproxy.cfg ${host}:/etc/haproxy/haproxy.cfg >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} haproxy.cfg is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/haproxy/haproxy.cfg" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_kube_controller_manager_conf() {
    generate_kube_controller_manager_conf $1 $2 $3
    shift 3
    for host in $@
    do
        rsync -avz /data/work/kube-controller-manager.kubeconfig ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-controller-manager.kubeconfig is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-controller-manager.kubeconfig" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kube-controller-manager.service ${host}:/lib/systemd/system/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-controller-manager.service is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/lib/systemd/system/kube-controller-manager.service" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kube-controller-manager.conf ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-controller-manager.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-controller-manager.conf" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_kubectl_conf() {
    generate_kubectl_conf $1
    shift
    for host in $@
    do
        rsync -avz /data/work/kube.config ${host}:/root/.kube/config >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube.config is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/root/.kube/config" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_kube_scheduler_conf() {
    generate_kube_scheduler_conf $1
    shift
    for host in $@
    do
        rsync -avz /data/work/kube-scheduler.kubeconfig ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-scheduler.kubeconfig is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-scheduler.kubeconfig" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kube-scheduler.conf ${host}:/etc/kubernetes/
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-scheduler.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-scheduler.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kube-scheduler.service ${host}:/lib/systemd/system/
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kube-scheduler.service is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kube-scheduler.service" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

put_kubelet_conf() {
    virtual_ip=$1
    cluster_dns=$2
    shift 2
    for host in $@
    do
        host_ipAddr=`ping ${host} -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o |awk 'NR==1{print $0}'`
        generate_kubelet_conf ${virtual_ip} ${host} ${host_ipAddr} ${cluster_DNS}
        rsync -avz /data/work/kubelet-bootstrap.kubeconfig ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kubelet-bootstrap.kubeconfig is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kubelet-bootstrap.kubeconfig" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kubelet.conf ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kubelet.conf is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kubelet.conf" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kubelet-${host}.yaml ${host}:/etc/kubernetes/kubelet.yaml >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kubelet.yaml is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kubelet.yaml" | tee -a /data/work/running.log
            exit 1
        fi
        rsync -avz /data/work/kubelet.service ${host}:/lib/systemd/system/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] The ${host} kubelet.service is transfer completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check ${host}:/etc/kubernetes/kubelet.service" | tee -a /data/work/running.log
            exit 1
        fi
    done
}

update_etcd_cert() {
    for host in $@
    do
        rsync -avz /data/work/ca*.pem ${host}:/etc/etcd/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} etcd ca certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} etcd ca certificate is failed" | tee -a /data/work/running.log
        fi
        rsync -avz /data/work/etcd*.pem ${host}:/etc/etcd/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} etcd certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} etcd certificate is failed" | tee -a /data/work/running.log
        fi
    done
}

update_apiserver_cert() {
    for host in $@
    do
        rsync -avz /data/work/ca*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} apiserver ca certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} apiserver ca certificate is failed" | tee -a /data/work/running.log
        fi
        rsync -avz /data/work/kube-apiserver*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} apiserver certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} apiserver certificate is failed" | tee -a /data/work/running.log
        fi
        rsync -avz /data/work/token.csv ${host}:/etc/kubernetes/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} token.csv is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} token.csv is failed" | tee -a /data/work/running.log
        fi
        rsync -avz /data/work/ca*.pem ${host}:/etc/etcd/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} etcd(used by apiserver) ca certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} etcd(used by apiserver) ca certificate is failed" | tee -a /data/work/running.log
        fi
        rsync -avz /data/work/etcd*.pem ${host}:/etc/etcd/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} etcd(used by apiserver) certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} etcd(used by apiserver) certificate is failed" | tee -a /data/work/running.log
        fi
    done
}

update_kubectl_cert() {
    for host in $@
    do
        rsync -avz /data/work/admin*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} kubectl certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} kubectl certificate is failed" | tee -a /data/work/running.log
        fi
    done
}

update_kube_controller_manager_cert() {
    for host in $@
    do
        rsync -avz /data/work/kube-controller-manager*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} kube-controller-manager certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} kube-controller-manager certificate is failed" | tee -a /data/work/running.log
        fi
    done
}

update_kube_scheduler_cert() {
    for host in $@
    do
        rsync -avz /data/work/kube-scheduler*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} kube-scheduler certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} kube-scheduler certificate is failed" | tee -a /data/work/running.log
        fi
    done
}

update_kubelet_cert() {
    for host in $@
    do
        rsync -avz /data/work/ca*.pem ${host}:/etc/kubernetes/ssl/ >/dev/null 2>&1
        if [ $? -eq 0 ];then
            echo "`date \"+%F %T \"`[info] update ${host} kubelet ca certificate is completed" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] update ${host} kubelet ca certificate is failed" | tee -a /data/work/running.log
        fi
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
        --endpoints=https://${host}:2379 \
        endpoint health | grep "Health" | awk '{print $3}'`
        if [ $check_result = true ];then
            echo "`date \"+%F %T \"`[info] etcd-cluster:${host} is healthy" | tee -a /data/work/running.log
        else
            echo "`date \"+%F %T \"`[error] please check etcd-cluster:${host} health" | tee -a /data/work/running.log
        fi
    done
}

etcd_service_restart() {
    for host in $@
    do
        ssh ${host} "systemctl daemon-reload && systemctl enable etcd && systemctl restart etcd"
    done
}

apiserver_service_restart() {
    for host in $@
    do
        ssh ${host} "systemctl daemon-reload && systemctl enable kube-apiserver && systemctl restart kube-apiserver"
    done
}

keepalived_service_restart() {
    for host in $@
    do
        ssh ${host} "systemctl daemon-reload && systemctl enable keepalived && systemctl restart keepalived"
    done
}

haproxy_service_restart() {
    for host in $@
    do
        ssh ${host} "systemctl daemon-reload && systemctl enable haproxy && systemctl restart haproxy"
    done
}

docker_service_restart() {
    for host in $@
    do
        ssh ${host} "systemctl daemon-reload && systemctl enable docker && systemctl restart docker"
    done
}

kubectl_create_clusterrolebinding() {
    kubectl create clusterrolebinding kube-apiserver:kubelet-apis \
    --clusterrole=system:kubelet-api-admin --user kubernetes
    kubectl create clusterrolebinding cluster-system-anonymous \
    --clusterrole=cluster-admin \
    --user=kubelet-bootstrap
    kubectl create clusterrolebinding kubelet-bootstrap \
    --clusterrole=system:node-bootstrapper \
    --user=kubelet-bootstrap
    echo 'source <(kubectl completion bash)' >> ~/.bashrc
    source ~/.bashrc
}

kube_approve_csr() {
    ssh ${masters} "kubectl certificate approve `kubectl get csr|awk '/node-csr-.*/{print$1}'` "
}

for host in ${etcds[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh ${host} "mkdir -p /etc/etcd/ssl /var/lib/etcd "
        expect { 
            "yes/no" { send "yes\r" }
        }
        expect eof
EOF
done

for host in ${masters[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh ${host} "mkdir -p /etc/kubernetes/ssl "
        expect { 
            "yes/no" { send "yes\r" }
        }
        expect eof
EOF
done

for host in ${nodes[@]}
do
    /usr/bin/expect <<EOF
        spawn ssh ${host} "mkdir -p /etc/kubernetes/ssl "
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
etcd_install ${etcd_version} ${etcd_url} ${etcds[@]}
put_etcd_conf ${etcds[@]}
update_etcd_cert ${etcds[@]}
etcd_check ${etcds[@]}
etcd_service_restart ${etcds[@]}
kube_install ${kubernetes_url} ${masters[@]}
put_apiserver_conf ${cluster_ips} ${masters[@]}
update_apiserver_cert ${masters[@]}
apiserver_service_restart ${masters[@]}
keepalived_install ${masters[@]}
put_keepalived_conf ${virtual_ip} ${masters[@]}
keepalived_service_restart ${masters[@]}
put_haproxy_conf ${masters[@]}
haproxy_service_restart ${masters[@]}
put_kubectl_conf ${virtual_ip} ${masters[@]}
update_kubectl_cert ${masters[@]}
kubectl_create_clusterrolebinding
put_kube_controller_manager_conf ${pod_ips} ${cluster_ips} ${virtual_ip} ${masters[@]}
update_kube_controller_manager_cert ${masters[@]}
put_kube_scheduler_conf ${virtual_ip} ${masters[@]}
update_kube_scheduler_cert ${masters[@]}
docker_install ${nodes[@]}
docker_service_restart ${nodes[@]}
put_kubelet_conf ${virtual_ip} ${cluster_DNS} ${nodes[@]}
update_kubelet_cert ${nodes[@]}
kube_approve_csr