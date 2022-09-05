# kubernetes二进制

## 一、准备

### 1.配置IP地址，hostname，ssh免密，时间同步(所有主机)

| 主机 | IP            | 配置 | 服务                                                         | 角色   |
| ---- | ------------- | ---- | ------------------------------------------------------------ | ------ |
| k-m1 | 192.168.1.101 | 2C3G | kube-apiserver、kube-controller-manager、 kube-scheduler、etcd、haproxy、keepalived | master |
| k-m2 | 192.168.1.102 | 2C3G | kube-apiserver、kube-controller-manager、 kube-scheduler、etcd、haproxy、keepalived | master |
| k-m3 | 192.168.1.103 | 2C3G | kube-apiserver、kube-controller-manager、 kube-scheduler、etcd、haproxy、keepalived | master |
| k-n1 | 192.168.1.104 | 2C3G | kubelet、kube-proxy、docker                                  | node   |
| k-n2 | 192.168.1.105 | 2C3G | kubelet、kube-proxy、docker                                  | node   |
| k-n3 | 192.168.1.106 | 2C3G | kubelet、kube-proxy、docker                                  | node   |
| VIP  | 192.168.1.107 |      |                                                              |        |

/etc/hosts配置文件

```shell
127.0.0.1 localhost
192.168.1.101 k-m1 etcd1
192.168.1.102 k-m2 etcd2
192.168.1.103 k-m3 etcd3
192.168.1.104 k-n1
192.168.1.105 k-n2
192.168.1.106 k-n3
# 修改完hostname之后要查看/etc/hosts是否有误，因为修改hostname也会修改/etc/hosts
```

各主机免密登录脚本（需要准备IP.txt文件来让脚本获取到主机登录信息）

```shell
#!/bin/bash
[ -f /root/.ssh/id_rsa ] || ssh-keygen -P "" -f /root/.ssh/id_rsa
touch /root/ip_up.txt && touch /root/ip_down.txt
grep -v -e "^#" IP.txt|while read SERVER_IP SSHD_PORT LOGIN_NAME SSH_PASSWD
do
        ping -c1 $SERVER_IP
        if [ $? -eq 0 ];then
                touch /root/ip_up.txt
                echo "$SERVER_IP 连接成功 $(date +%F)" >> /root/ip_up.txt
                /usr/bin/expect <<-END
                spawn ssh-copy-id -p $SSHD_PORT $LOGIN_NAME@$SERVER_IP
                expect {
                        "yes/no" { send "yes\r";exp_continue }
                        "password:" { send "$SSH_PASSWD\r" }
                }
                expect eof
                END
                echo "完成向$SERVER_IP发送公钥"
        else
                touch /root/ip_down.txt
                echo "$SERVER_IP 无法连接 $(date +%F)" >> ip_down.txt
        fi
done
cat /root/ip_up.txt && cat /root/ip_down.txt
```

启用模块

```shell
modprobe  ip_vs
modprobe  ip_vs_rr
modprobe  ip_vs_wrr
modprobe  ip_vs_sh
modprobe  nf_conntrack_ipv4 # 高版本内核替换为nf_conntrack
```

模块持久化

```shell
cat <<EOF | tee /etc/modules-load.d/k8s.conf
br_netfilter
overlay
ip_vs
ip_vs_rr
ip_vs_wrr
ip_vs_sh
nf_conntrack_ipv4
EOF
```

启用iptables路由转发

```shell
cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl --system
```

安装ipvsadm

```shell
apt-get install ipvsadm -y
```

安装net-tools

```
apt-get install net-tools -y
```

### 2.生成k8s集群证书

k-m1>工作目录创建

```shell
mkdir -p /data/work # 之后的步骤基本在工作目录中完成
```

etcd集群目录创建

```shell
mkdir -p /etc/etcd/ssl #
mkdir -p /var/lib/etcd 
```

kubernetes集群目录创建

```shell
mkdir -p /etc/kubernetes/
mkdir -p /etc/kubernetes/ssl
mkdir -p /var/log/kubernetes
```

安装cfssl工具

```shell
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl_1.5.0_linux_amd64 -o /bin/cfssl
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssljson_1.5.0_linux_amd64 -o /bin/cfssljson
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl-certinfo_1.5.0_linux_amd64 -o /bin/cfssl-certinfo
chmod +x /bin/cfssl
chmod +x /bin/cfssljson
chmod +x /bin/cfssl-certinfo
# cfssl: 证书签发的工具命令
# cfssljson: 将cfssl 生成的证书( json格式)变为文件承载式证书
# cfssl-certinfo:验证证书的信息 
# cfssl-certinfo -cert <证书名称>
```

ca证书策略创建

```shell
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
# signing：表示该证书可用于签名其它证书；生成的 ca.pem 证书中 CA=TRUE
# server auth：表示可以该CA 对 server 提供的证书进行验证
# client auth：表示可以用该 CA 对 client 提供的证书进行验证
# expiry：也表示过期时间，如果不写以default中的为准
```

ca证书配置

```shell
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
```

生成ca根证书

```shell
cfssl gencert -initca /data/work/ca-csr.json | cfssljson -bare /data/work/ca
```

生成etcd证书

```SHELL
cat > /data/work/etcd-csr.json <<EOF
{
    "CN": "etcd",
    "hosts": [
        "127.0.0.1",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103",
        "k-m1",
        "k-m2",
        "k-m3",
        "etcd1",
        "etcd2",
        "etcd3"
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
# hosts如果为""则代表所有IP都可以通过
```

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes /data/work/etcd-csr.json | cfssljson -bare /data/work/etcd
```

TLS Bootstrapping 机制可以让api-server动态颁发客户端证书

```SHELL
cat > /data/work/token.csv << EOF
`head -c 16 /dev/urandom | od -An -t x | tr -d ' '`,kubelet-bootstrap,10001,"system:bootstrapper"
EOF
# 生成TOKEN提供给TLS Bootstrapping 使用
```

创建api-server证书的配置文件

```shell
cat > /data/work/kube-apiserver-csr.json <<EOF
{
    "CN": "kubernetes",
    "hosts": [
        "127.0.0.1",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103",
        "192.168.1.104",
        "192.168.1.105",
        "192.168.1.106",
        "192.168.1.107",
        "192.168.1.108",
        "192.168.1.109",
        "192.168.1.110",
        "k-m1",
        "k-m2",
        "k-m3",
        "k-n1",
        "k-n2",
        "k-n3",
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
# hosts如果为[]则代表所有IP都可以通过,但是不推荐
```

生成api-server证书

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-apiserver-csr.json | cfssljson -bare /data/work/kube-apiserver
```

创建kubectl证书配置文件

```shell
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
# 此处的name.O必须为system:masters，因为O指定该证书的 Group 为 system:masters，cluster-admin 将 Group system:masters 与 Role cluster-admin 绑定
```

生成kubectl证书

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare /data/work/admin
```

创建kube-controller-manager证书配置文件

```shell
cat > /data/work/kube-controller-manager-csr.json <<EOF
{
    "CN": "system:kube-controller-manager",
    "key":{
        "algo": "rsa",
        "size": 2048
    },
    "hosts": [
        "127.0.0.1",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103"
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
# kubernetes 内置的 ClusterRoleBindings kube-controller-manager 赋予 kube-controller-manager 工作所需的权限
```

kube-controller-manager证书创建

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-controller-manager-csr.json | cfssljson -bare /data/work/kube-controller-manager
```

创建kube-scheduler证书配置文件

```SHELL
cat > /data/work/kube-scheduler-csr.json<<EOF
{
    "CN": "system:kube-scheduler",
    "key":{
        "algo": "rsa",
        "size": 2048
    },
    "hosts": [
        "127.0.0.1",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103"
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
```

创建kube-scheduler证书

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-scheduler-csr.json | cfssljson -bare /data/work/kube-scheduler
```

创建kube-proxy证书配置文件

```shell
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
```

创建kube-proxy证书

```shell
cfssl gencert -ca=/data/work/ca.pem -ca-key=/data/work/ca-key.pem -config=/data/work/ca-config.json -profile=kubernetes /data/work/kube-proxy-csr.json | cfssljson -bare /data/work/kube-proxy
```

### 3.ETCD集群部署

下载ETCD

```shell
#!/bin/bash
ETCD_VER=v3.4.20 # 版本
GOOGLE_URL=https://storage.googleapis.com/etcd
GITHUB_URL=https://github.com/etcd-io/etcd/releases/download
DOWNLOAD_URL=${GOOGLE_URL} # 选择下载连接
wget ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz -P /data/work/ && \
tar -zxf /data/work/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /data/work/
for i in {etcd1,etcd2,etcd3}
do
    /usr/bin/expect <<EOF
    spawn ssh root@$i mkdir -p /etc/etcd/
    expect { 
        "yes/no" { send "yes\r" }
        }
    expect eof
EOF
    rsync -avz /data/work/etcd-${ETCD_VER}-linux-amd64/etcd* $i:/usr/local/bin/
done
```

etcd.conf

```shell
cat > /data/work/etcd.conf <<EOF
#[Member]
ETCD_NAME="etcd1"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.1.101:2380"
ETCD_LISTEN_CLIENT_URLS="https://192.168.1.101:2379,https://127.0.0.1:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.1.101:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.1.101:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://192.168.1.101:2380,etcd2=https://192.168.1.102:2380,etcd3=https://192.168.1.103:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
```

注释

```shell
ETCD_NAME # 节点名称，集群中唯一
ETCD_DATA_DIR # 数据目录位置
ETCD_LISTEN_PEER_URLS # 集群内部通信监听地址
ETCD_LISTEN_CLIENT_URLS # 客户端访问监听地址
ETCD_INITIAL_ADVERTISE_PEER_URLS # 集群通告地址
ETCD_ADVERTISE_CLIENT_URLS # 客户端通告地址
ETCD_INITIAL_CLUSTER # 集群间所有节点地址
ETCD_INITIAL_CLUSTER_TOKEN # 集群间的TOKEN
ETCD_INITIAL_CLUSTER_STATE # 加入集群的当前状态，new是新集群，existing表示加入已有集群
```

etcd.service

```SHELL
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
ExecStart=/usr/local/bin/etcd \
--cert-file=/etc/etcd/ssl/etcd.pem \
--key-file=/etc/etcd/ssl/etcd-key.pem \
--trusted-ca-file=/etc/etcd/ssl/ca.pem \
--peer-cert-file=/etc/etcd/ssl/etcd.pem \
--peer-key-file=/etc/etcd/ssl/etcd-key.pem \
--peer-trusted-ca-file=/etc/etcd/ssl/ca.pem \
--client-cert-auth \
--peer-client-cert-auth
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
chmod +x /data/work/etcd.service
```

复制各文件到对应的位置

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    /usr/bin/expect <<EOF
    spawn ssh root@$i mkdir -p /etc/etcd/ssl/ /var/lib/etcd/
    expect { 
        "yes/no" { send "yes\r" }
        }
    expect eof
EOF
    j=`ping $i -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o|awk 'NR==1{print $0}'` && \
    sed -e "2s|etcd1|$i|g" -e "4,9s|192.168.1.101|$j|g" /data/work/etcd.conf|ssh $i "cat > /etc/etcd/"
    rsync -avz /data/work/ca*.pem $i:/etc/etcd/ssl/
    rsync -avz /data/work/etcd*.pem $i:/etc/etcd/ssl/
    rsync -avz /data/work/etcd.service $i:/lib/systemd/system/
done
```

启动服务

```shell
systemctl daemon-reload
systemctl enable etcd
systemctl start etcd
```

检查集群状态

```shell
ETCDCTL_API=3 /usr/local/bin/etcdctl \
--write-out=table \
--cacert=/etc/etcd/ssl/ca.pem \
--cert=/etc/etcd/ssl/etcd.pem \
--key=/etc/etcd/ssl/etcd-key.pem \
--endpoints=https://192.168.1.101:2379,https://192.168.1.102:2379,https://192.168.1.103:2379 \
endpoint health
```

查看节点成员

```shell
ETCDCTL_API=3 /usr/local/bin/etcdctl \
--write-out=table \
--cacert=/etc/etcd/ssl/ca.pem \
--cert=/etc/etcd/ssl/etcd.pem \
--key=/etc/etcd/ssl/etcd-key.pem \
--endpoints=https://192.168.1.101:2379,https://192.168.1.102:2379,https://192.168.1.103:2379 \
member list
```

查看集群状态

```shell
ETCDCTL_API=3 /usr/local/bin/etcdctl \
--write-out=table \
--cacert=/etc/etcd/ssl/ca.pem \
--cert=/etc/etcd/ssl/etcd.pem \
--key=/etc/etcd/ssl/etcd-key.pem \
--endpoints=https://192.168.1.101:2379,https://192.168.1.102:2379,https://192.168.1.103:2379 \
endpoint status
```

### 4.下载、解压、分发kubernetes文件

```shell
#!/bin/bash
wget https://storage.googleapis.com/kubernetes-release/release/v1.23.10/kubernetes-server-linux-amd64.tar.gz -P /data/work && \
tar xf /data/work/kubernetes-server-linux-amd64.tar.gz -C /data/work/
k8sdir=/data/work/kubernetes/server/bin
for i in {k-m1,k-m2,k-m3}
do
    rsync -avz ${k8sdir}/kube-apiserver ${k8sdir}/kube-controller-manager ${k8sdir}/kube-scheduler ${k8sdir}/kubectl $i:/usr/local/bin/
done
for i in {k-n1,k-n2,k-n3}
do
    /usr/bin/expect <<END
    spawn rsync -avz ${k8sdir}/kubelet ${k8sdir}/kube-proxy $i:/usr/local/bin/
    expect {
        "yes/no" { send "yes\r" }
    }
    expect eof
END
done
```

### 5.部署api-server

服务文件kube-apiserver.service

```shell
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
```

kube-apiserver.conf

```shell
cat > /data/work/kube-apiserver.conf <<EOF
KUBE_APISERVER_OPTS="--enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \\
--anonymous-auth=false \\
--bind-address=192.168.1.101 \\
--secure-port=6443 \\
--advertise-address=192.168.1.101 \\
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
--service-cluster-ip-range=193.169.0.0/16 \\
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
--etcd-servers=https://192.168.1.101:2379,https://192.168.1.102:2379,https://192.168.1.103:2379 \\
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
```

注释

```shell
KUBE_APISERVER_OPTS="--enable-admission-plugins=NodeRestriction \
--anonymous-auth=false \
--bind-address=192.168.1.101 \
--secure-port=6443 \
--advertise-address=192.168.1.101 \
--insecure-port=0 \
--authorization-mode=Node,RBAC \
--requestheader-client-ca-file=/etc/kubernetes/ssl/ca.pem \
--proxy-client-cert-file=/etc/kubernetes/ssl/kube-proxy.pem \
--proxy-client-key-file=/etc/kubernetes/ssl/kube-proxy-key.pem \
--requestheader-allowed-names=aggregator \
--requestheader-extra-headers-prefix=X-Remote-Extra- \
--requestheader-group-headers=X-Remote-Group \
--requestheader-username-headers=X-Remote-User \
--enable-aggregator-routing=true
--runtime-config=api/all=true \
--enable-bootstrap-token-auth \
--service-cluster-ip-range=193.169.0.0/16 \
--token-auth-file=/etc/kubernetes/token.csv \
--service-node-port-range=30000-50000 \
--tls-cert-file=/etc/kubernetes/ssl/kube-apiserver.pem \
--tls-private-key-file=/etc/kubernetes/ssl/kube-apiserver-key.pem \
--client-ca-file=/etc/kubernetes/ssl/ca.pem \
--kubelet-client-certificate=/etc/kubernetes/ssl/kube-apiserver.pem \
--kubelet-client-key=/etc/kubernetes/ssl/kube-apiserver-key.pem \
--service-account-key-file=/etc/kubernetes/ssl/ca-key.pem \
--service-account-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \
--service-account-issuer=https://kubernetes.default.svc.cluster.local \
--etcd-cafile=/etc/etcd/ssl/ca.pem \
--etcd-certfile=/etc/etcd/ssl/etcd.pem \
--etcd-keyfile=/etc/etcd/ssl/etcd-key.pem \
--etcd-servers=https://192.168.1.101:2379,https://192.168.1.102:2379,https://192.168.1.103:2379 \
--enable-swagger-ui=true \
--allow-privileged=true \
--apiserver-count=3 \
--audit-log-maxage=30 \
--audit-log-maxbackup=3 \
--audit-log-maxsize=100 \
--audit-log-path=/var/log/kube-apiserver-audit.log \
--event-ttl=1h \
--alsologtostderr=true \
--logtostderr=false \
--log-dir=/var/log/kubernetes \
--v=4"

logtostderr # 启用日志
v # 日志等级
log-dir # 日志目录
etcd-server # etcd集群地址
bind-address # 监听地址
secure-port # https安全端口
advertise-address # 集群通告地址
allow-privileged # 启用授权
service-cluster-ip-range # service虚拟ip地址段
enable-admission-plugins # 准入控制模块
authorization-mode # 认证授权，启用RBAC授权和节点自管理
enable-bootstrap-token-auth # 启用TLS bootstrap机制
token-auth-file # TLS bootstrap的token文件
service-node-port-range # nodeport的默认分配端口
audit-log # 审计日志
# enable-admission-plugins 默认启用的插件
CertificateApproval, CertificateSigning, CertificateSubjectRestriction, DefaultIngressClass, DefaultStorageClass, DefaultTolerationSeconds, LimitRanger, MutatingAdmissionWebhook, NamespaceLifecycle, PersistentVolumeClaimResize, PodSecurity, Priority, ResourceQuota, RuntimeClass, ServiceAccount, StorageObjectInUseProtection, TaintNodesByCondition, ValidatingAdmissionWebhook
```

传送配置文件、证书

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    /usr/bin/expect <<EOF
    spawn ssh root@$i mkdir -p /etc/kubernetes/ssl/ /var/log/kubernetes/
    expect {
        "yes/no" { send "yes\r" }
        }
    expect eof
EOF
    rsync -avz /data/work/ca*.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/kube-apiserver*.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/token.csv $i:/etc/kubernetes/
    rsync -avz /data/work/kube-apiserver.service $i:/lib/systemd/system/
    j=`ping $i -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o|awk 'NR==1{print $0}'` && \
    sed "/bind-address\|advertise-address/s#192.168.1.101#$j#g" /data/work/kube-apiserver.conf|ssh $i "cat > /etc/kubernetes/kube-apiserver.conf"
done
```

测试apiserver

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    ssh $i "systemctl daemon-reload && systemctl enable kube-apiserver && systemctl start kube-apiserver" && \
    ssh $i "curl -s --insecure https://$i:6443/"
done
```

keepalived部署

```shell
#!/bin/bash
# 配置文件生成
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
        192.168.1.107
    }
    unicast_src_ip local_ip
    unicast_peer {
        192.168.1.101
        192.168.1.102
        192.168.1.103
    }
    track_script {
        check_service
    }
}
EOF
# 检测脚本生成
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
# 安装keepalived，分发配置文件
for i in {k-m1,k-m2,k-m3}
do
    ssh $i "apt install keepalived -y"
    rsync -avz /data/work/check_service.sh $i:/etc/keepalived/
    if [ ! -z $if_name ];then
        [ `ssh $i "ifconfig"| grep "$if_name"|wc -l` -ge 1 ] || echo "please check interfacename" && exit
    else
        if_count=`ssh $i "ifconfig" |grep -B1 -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"|grep -iw "UP"|grep -iv "LOOPBACK"|awk -F ":" '{print$1}'|grep -e "^e"|wc -l `
        if [ $if_count -eq 1 ];then
            if_name=`ssh $i "ifconfig" |grep -B1 -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"|grep -iw "UP"|grep -iv "LOOPBACK"|awk -F ":" '{print$1}'|grep -e "^e"`
        else
            echo "please check interfacename" && exit
        fi
    fi
    j=`ping $i -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o|awk 'NR==1{print $0}'`
    sed "/$j/d" /data/work/keepalived.conf | \
    sed -e "s#if_name#$if_name#g" -e "s#local_ip#$j#g" | \
    ssh $i "cat > /etc/keepalived/keepalived.conf && chmod +x /etc/keepalived/check_service.sh"
    ssh $i "systemctl enable keepalived && systemctl start keepalived"
done
```

HAProxy部署

```shell
#!/bin/bash
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
    server k-m1 192.168.1.101:6443 check inter 2000 rise 2 fall 3 weight 1
    server k-m2 192.168.1.102:6443 check inter 2000 rise 2 fall 3 weight 1
    server k-m3 192.168.1.103:6443 check inter 2000 rise 2 fall 3 weight 1
    
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

for i in {k-m1,k-m2,k-m3}
do
    ssh $i "apt install haproxy -y"
    ssh $i "[ -e /etc/haproxy/haproxy.cfg ] && mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg`date +%F_%T`"
    rsync -avz /data/work/haproxy.cfg $i:/etc/haproxy/haproxy.cfg
    ssh $i "systemctl enable haproxy && systemctl restart haproxy"
done
```

### 6.部署kubectl

```shell
#!/bin/bash
# 集群参数设置↓
kubectl config set-cluster kubernetes \
--certificate-authority=/data/work/ca.pem \
--embed-certs=true \
--server=https://192.168.1.107:8443 \
--kubeconfig=/data/work/kube.config
# 客户端认证参数设置↓
kubectl config set-credentials admin \
--client-certificate=/data/work/admin.pem \
--client-key=/data/work/admin-key.pem \
--embed-certs=true \
--kubeconfig=/data/work/kube.config
# 上下文参数设置↓
kubectl config set-context kubernetes \
--cluster=kubernetes \
--user=admin \
--kubeconfig=/data/work/kube.config
# 默认上下文设置↓
kubectl config use-context kubernetes \
--kubeconfig=/data/work/kube.config

for i in {k-m1,k-m2,k-m3}
do
    ssh $i "mkdir /root/.kube"
    rsync -avz /data/work/kube.config $i:/root/.kube/config
    rsync -avz /data/work/admin*.pem $i:/etc/kubernetes/ssl/
done

kubectl create clusterrolebinding kube-apiserver:kubelet-apis \
--clusterrole=system:kubelet-api-admin --user kubernetes
```

测试

```shell
kubectl cluster-info # 集群信息加上 dump 详细模式
kubectl get componentstatuses # 集群健康度检查
kubectl get all --all-namespaces # 全ns检查
```

kubectl命令补全

```shell
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

### 7.kube-controller-manager配置

kube-controller-manager服务配置

```shell
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
```

生成kube-controller-manager.conf配置文件

```shell
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
--cluster-cidr=10.0.0.0/16 \\
--service-cluster-ip-range=193.169.0.0/16 \\
--cluster-signing-cert-file=/etc/kubernetes/ssl/ca.pem \\
--cluster-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--root-ca-file=/etc/kubernetes/ssl/ca.pem \\
--service-account-private-key-file=/etc/kubernetes/ssl/ca-key.pem \\
--cluster-signing-duration=87600h0m0s"
EOF
# cluster-cidr 指pod的ip
# service-cluster-ip-range 指servive的ip
# experimental-cluster-signing-duration 动态签发证书的有效期，其实设置小了也无所谓到期kubelet会再申请证书
# leader-elect 选举，多master一定要True
# 启用的控制器列表，tokencleaner 用于自动清理过期的 Bootstrap token
# horizontal-pod-autoscaler-use-rest-clients 自动扩缩容(弃用了)
# horizontal-pod-autoscaler-sync-period 自动扩缩容检测间隔
# alsologtostderr 输出到文件的同时输出到错误输出
```

生成kube-controller-manager.kubeconfig连接apiserver配置文件

```shell
#!/bin/bash
# 设置集群参数
kubectl config set-cluster kubernetes \
--certificate-authority=/data/work/ca.pem \
--embed-certs=true \
--server=https://192.168.1.107:8443 \
--kubeconfig=/data/work/kube-controller-manager.kubeconfig
# 设置客户端认证参数
kubectl config set-credentials system:kube-controller-manager \
--client-certificate=/data/work/kube-controller-manager.pem \
--client-key=/data/work/kube-controller-manager-key.pem \
--embed-certs=true \
--kubeconfig=/data/work/kube-controller-manager.kubeconfig
# 设置上下文参数
kubectl config set-context system:kube-controller-manager \
--cluster=kubernetes \
--user=system:kube-controller-manager \
--kubeconfig=/data/work/kube-controller-manager.kubeconfig
# 设置默认上下文
kubectl config use-context system:kube-controller-manager \
--kubeconfig=/data/work/kube-controller-manager.kubeconfig

```

分发配置文件

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    rsync -avz /data/work/kube-controller-manager.kubeconfig $i:/etc/kubernetes/
    rsync -avz /data/work/kube-controller-manager*.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/kube-controller-manager.service $i:/lib/systemd/system/
    ssh $i "systemctl daemon-reload && systemctl enable kube-controller-manager && systemctl restart kube-controller-manager"
    rsync -avz /data/work/kube-controller-manager.conf $i:/etc/kubernetes/
done
```

检验

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    ssh $i "curl -s --cacert /etc/kubernetes/ssl/ca.pem https://127.0.0.1:10257/healthz"
done
```

### 8.kube-scheduler部署

生成kube-scheduler.config

```shell
#!/bin/bash
# 设置集群参数
kubectl config set-cluster kubernetes \
--certificate-authority=/data/work/ca.pem \
--embed-certs=true \
--server=https://192.168.1.107:8443 \
--kubeconfig=/data/work/kube-scheduler.kubeconfig
# 设置客户端认证参数
kubectl config set-credentials system:kube-scheduler \
--client-certificate=/data/work/kube-scheduler.pem \
--client-key=/data/work/kube-scheduler-key.pem \
--embed-certs=true \
--kubeconfig=/data/work/kube-scheduler.kubeconfig
# 设置上下文参数
kubectl config set-context system:kube-scheduler \
--cluster=kubernetes \
--user=system:kube-scheduler \
--kubeconfig=/data/work/kube-scheduler.kubeconfig
# 设置默认上下文
kubectl config use-context system:kube-scheduler \
--kubeconfig=/data/work/kube-scheduler.kubeconfig
```

生成kube-scheduler.service服务配置文件

```shell
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
```

生成kube-scheduler.conf配置文件

```shell
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
```

分发配置文件

```shell
#!/bin/bash
for i in {k-m1,k-m2,k-m3}
do
    rsync -avz /data/work/kube-scheduler*.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/kube-scheduler.conf $i:/etc/kubernetes/
    rsync -avz /data/work/kube-scheduler.service $i:/lib/systemd/system/
    rsync -avz /data/work/kube-scheduler.kubeconfig $i:/etc/kubernetes/
    ssh $i "systemctl daemon-reload && systemctl enable kube-scheduler && systemctl restart kube-scheduler"
done
```

### 9.节点docker部署

```shell
#!/bin/bash
for i in {k-n1,k-n2,k-n3}
do
    ssh $i "apt remove docker docker-engine docker.io containerd runc -y"
    ssh $i "apt-get update && sudo apt-get install ca-certificates curl gnupg lsb-release"
    ssh $i "mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -"
done
for i in {k-n1,k-n2,k-n3}
do
    ssh $i "add-apt-repository \"deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" && apt-get update"
    ssh $i "apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y"
    ssh $i "systemctl daemon-reload && systemctl restart docker"
done
```

### 10.工作节点kubelet部署

生成kubelet-bootstrap.kubeconfig

```shell
#!/bin/bash
# 设置集群参数
kubectl config set-cluster kubernetes \
--certificate-authority=/data/work/ca.pem \
--embed-certs=true \
--server=https://192.168.1.107:8443 \
--kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
# 设置客户端认证参数
kubectl config set-credentials kubelet-bootstrap \
--token=`awk -F , '{print $1}' /data/work/token.csv` \
--kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
# 设置上下文参数
kubectl config set-context default \
--cluster=kubernetes \
--user=kubelet-bootstrap \
--kubeconfig=/data/work/kubelet-bootstrap.kubeconfig
# 设置默认上下文
kubectl config use-context default \
--kubeconfig=/data/work/kubelet-bootstrap.kubeconfig

# 创造集群角色绑定
kubectl create clusterrolebinding cluster-system-anonymous \
--clusterrole=cluster-admin \
--user=kubelet-bootstrap
kubectl create clusterrolebinding kubelet-bootstrap \
--clusterrole=system:node-bootstrapper \
--user=kubelet-bootstrap
```

启动参数配置kubeconfig

```shell
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
# 可选
--hostname-override=host_name \\
--node-ip=ipAddr \\
--node-labels="kubernetes.io/hostname=host_name" \\
--rotate-certificates \\
--rotate-server-certificates \\
# kubeconfig 自动生成的连接apiserver的配置文件路径
# hostname-override 如果为非空，将使用此字符串而不是实际的主机名作为节点标识
# pod-infra-container-image 容器pause镜像下载
# rotate-certificates 用于自动轮换 kubelet 连接 apiserver 所用的证书
# rotate-server-certificates用于自动轮换 kubelet 10250 api 端口所使用的证书
```

kubelet.yaml子配置文件

```shell
cat > /data/work/kubelet.yaml <<EOF
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
address: "ipAddr"
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
  - "193.169.0.2"
EOF
# 可选
featureGates: 
  RotateKubeletClientCertificate: true
  RotateKubeletServerCertificate: true
# <servicename>.<namespace>.svc.<clusterdomain> DNS的域名规范
# RotateKubeletServerCertificate (可能废弃)用于自动续期 kubelet 10250 api 端口所使用的证书
# RotateKubeletClientCertificate (废弃)用于自动续期 kubelet 连接 apiserver 所用的证书
```

创建kubelet.service

```shell
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
```

分发文件

```shell
#!/bin/bash
for i in {k-n1,k-n2,k-n3}
do
    j=`ping $i -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o|awk 'NR==1{print $0}'`
    ssh $i "rm -rf /etc/kubernetes/ssl/* && rm -rf /var/lib/kubelet/*"
    ssh $i "mkdir -p /etc/kubernetes/ssl/ /var/lib/kubelet/"
    rsync -avz /data/work/ca.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/kubelet-bootstrap.kubeconfig $i:/etc/kubernetes/
    rsync -avz /data/work/kubelet.conf $i:/etc/kubernetes/
    ssh $i "sed -i -e \"s#host_name#$i#g\" -e \"s#ipAddr#$j#g\" /etc/kubernetes/kubelet.conf"
    sed "s#ipAddr#$j#g" /data/work/kubelet.yaml| ssh $i "cat > /etc/kubernetes/kubelet.yaml"
    rsync -avz /data/work/kubelet.service $i:/lib/systemd/system/
    ssh $i "systemctl daemon-reload && systemctl restart kubelet"
done
# 如果未生效则重启试试
```

master获取CSR请求

```shell
kubectl get csr
```

允许CSR请求

```shell
kubectl certificate approve `kubectl get csr|awk '/node-csr-.*/{print$1}'` 
```

### 11.工作节点kube-proxy部署

生成kube-proxy.kubeconfig

```shell
# 集群信息
kubectl config set-cluster kubernetes \
--certificate-authority=/data/work/ca.pem \
--embed-certs=true \
--server=https://192.168.1.107:8443 \
--kubeconfig=/data/work/kube-proxy.kubeconfig
# kube-proxy证书配置
kubectl config set-credentials kube-proxy \
--client-certificate=/data/work/kube-proxy.pem \
--client-key=/data/work/kube-proxy-key.pem \
--embed-certs=true \
--kubeconfig=/data/work/kube-proxy.kubeconfig
# 上下文设置
kubectl config set-context default \
--cluster=kubernetes \
--user=kube-proxy \
--kubeconfig=/data/work/kube-proxy.kubeconfig
# 默认上下文
kubectl config use-context default \
--kubeconfig=/data/work/kube-proxy.kubeconfig
```

kube-proxy.yaml配置文件生成

```shell
cat > /data/work/kube-proxy.yaml <<EOF
kind: KubeProxyConfiguration
apiVersion: kubeproxy.config.k8s.io/v1alpha1
bindAddress: ipAddr
clientConnection:
  kubeconfig: /etc/kubernetes/kube-proxy.kubeconfig
clusterCIDR: 10.0.0.0/16
healthzBindAddress: ipAddr:10256
metricsBindAddress: ipAddr:10249
mode: "ipvs"
EOF
```

kube-proxy.service服务文件

```shell
cat > /data/work/kube-proxy.service <<EOF
[Unit]
Description=Kubernetes Kube-Proxy Server
Documentation=https://github.com/kubernetes/kubernetes
After=network.target

[Service]
WorkingDirectory=/var/lib/kube-proxy
ExecStart=/usr/local/bin/kube-proxy \\
--config=/etc/kubernetes/kube-proxy.yaml \\
--alsologtostderr=true \\
--logtostderr=false \\
--log-dir=/var/log/kubernetes \\
--v=2

Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
```

分发文件

```shell
#!/bin/bash
for i in {k-n1,k-n2,k-n3}
do
    ssh $i "mkdir -p /var/lib/kube-proxy"
    j=`ping $i -c1|grep -e "\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}" -o|awk 'NR==1{print $0}'`
    rsync -avz /data/work/kube-proxy*.pem $i:/etc/kubernetes/ssl/
    rsync -avz /data/work/kube-proxy.kubeconfig $i:/etc/kubernetes/
    sed "s#ipAddr#$j#g" /data/work/kube-proxy.yaml | ssh $i "cat > /etc/kubernetes/kube-proxy.yaml"
    rsync -avz /data/work/kube-proxy.service $i:/lib/systemd/system/
    ssh $i "systemctl daemon-reload && systemctl enable kube-proxy && systemctl restart kube-proxy"
done
```

### 12.calico部署

```shell
curl https://projectcalico.docs.tigera.io/manifests/calico-typha.yaml -o /data/work/calico.yaml
sed -i -e 's/# - name: CALICO_IPV4POOL_CIDR/- name: CALICO_IPV4POOL_CIDR/g' \
-e 's|#   value: "192.168.0.0/16"|  value: "10.0.0.0/16"|g' /data/work/calico.yaml
kubectl apply -f /data/work/calico.yaml
kubectl get pods -n kube-system # 查看是否成功
```

### 13.coreDNS

```shell
wget https://raw.githubusercontent.com/coredns/deployment/master/kubernetes/coredns.yaml.sed -O /data/work/coredns.yaml
sed -i \
-e "s#kubernetes CLUSTER_DOMAIN REVERSE_CIDRS#kubernetes cluster.local in-addr.arpa ip6.arpa#g" \
-e "s#forward . UPSTREAMNAMESERVER#forward . /etc/resolv.conf#g" \
-e "s#clusterIP: CLUSTER_DNS_IP#clusterIP: 193.169.0.2#g" \
-e "s#}STUBDOMAINS#} STUBDOMAINS#g" /data/work/coredns.yaml
sed -i "/nameserver/a\
nameserver 223.5.5.5\n\
nameserver 119.29.29.29\n\
nameserver 8.8.8.8\n" /etc/resolv.conf
for i in {k-m1,k-m2,k-m3,k-n1,k-n2,k-n3}
do
    rsync -avz /etc/resolv.conf $i:/etc/resolv.conf
done
kubectl apply -f /data/work/coredns.yaml
```

### 14.Ingress Controller

```shell
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.3/deploy/static/provider/cloud/deploy.yaml -O /data/work/ingress-nginx.yaml
sed -i \
-e "s#image: k8s.gcr.io/ingress-nginx/controller:v1.1.3@sha256:31f47c1e202b39fadecf822a9b76370bd4baed199a005b3e7d4d1455f4fd3fe2#image: dyrnq/ingress-nginx-controller:v1.1.3#g" \
-e "s#image: k8s.gcr.io/ingress-nginx/kube-webhook-certgen:v1.1.1@sha256:64d8c73dca984af206adf9d6d7e46aa550362b1d7a01f3a0a91b20cc67868660#image: dyrnq/kube-webhook-certgen:v1.1.1#g" \
/data/work/ingress-nginx.yaml
kubectl apply -f /data/work/ingress-nginx.yaml
```



