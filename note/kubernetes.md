# kubernetes

## 一、组件

### master node manager

etcd: 数据库，存储kubernetes的事件信息

API Server: 集群注册管理、资源配置控制、提供安全机制、代理一些服务

​	Metrics server: 集群范围的资源使用情况的数据聚合器

​	kubernetes聚合器: 把第三方应用注册到API-server中

Scheduler: 调度、安排容器在哪个节点部署

Contaroller Manager: 控制器管理者，负责高级任务



### Minion node worker

容器运行态

kuberlet: 

​	管理容器

​	健康检查（存活检查、就绪检查）

​	cadvisor: 收集节点信息传给Metrics server

​	kubernetes proxy: 

​		负责容器网络、实现负载均衡（创建server时）

​		kube-proxy共有三种代理模式

​			userspace（早期，已弃用）

​			iptables（默认）: client访问iptables规则，有iptables负责转发数据包

​			ipvs（建议）: client访问ipvs(virtual server)通过路由转发到后端Backend Pod(real server)

## 二、基本单元及功能

### pod

kubernetes最小单元

#### 分类

有控制器管理的pod: 

​	必须处于高可用状态，具有restartPolicy重启策略Always|OnFailure|Never，当健康检查livenessProbe(存活检查)失败时将杀死容器，根据重启策略操作。当健康检查readinessProbe(就绪检查)失败时kubernetes会把pod从service endpoints中剔除

​	有replication controllers 保持定量的副本

​	使用replication controllers 实现pod滚动更新及回滚

无控制器的pod: 

​	自主式pod 故障不复存在，无法全局调度

静态pod:
	/var/lib/kubelet/config.yaml定义的staticPodPath(/etc/kubernetes/manifests)下的pod由kubelet管理

​	不走Scheduler调度的流程固定在节点运行

#### 特点

会创建一个Pause容器，其他容器共享Pause的网卡

pod中可以不止一个或一种容器

pod在调度中不可再分

多个容器之间共享多个紧密耦合的资源(volume、network) 

可以定义一次性容器initcontainers

### service

iptables或ipvs规则，感知pod的IP地址变化(服务发现，相当于pod的代理)

#### 特点

防止pod失连，通过label-selector关联pod

定义一组pod的访问策略（负载均衡 tcp|udp 4层）

由kube-proxy调用iptables or ipvs 生成的一组规则，虽然有IP地址，但是是虚拟出来的service

CoreDNS: 域名解析

​	会在每一个容器中建立/etc/resolv.conf

​	search default.svc.cluster.local svc.cluster.local cluster.local lxw.com   #域名会自动加上这些字段匹配匹配

### Ingress:

​	Ingress公开了从集群外部到集群内服务的Http、https路由的规则集合

​	具体实现流量路由是由Ingress Controller负责

​	一种抽象资源，给管理员提供暴露应用入口定义方法

​	7层负载均衡，例如根据域名分发到对应的service，再由service转发到pod

### label

标签key: value ，标识node，pod，service，RC等

### Namespace

命名空间kubernetes将资源对象逻辑上隔离，从而形成多个虚拟集群

应用场景: 

​    根据不同团队划分命名空间

​    根据项目划分命名空间

### label selector

标签查询筛选，可以对资源对象进行分组

### scheduler

NODE节点监控，pod资源适配

### Contaroller

工作负载控制器

#### 	replication controllers

​		保证高可用

​		replication controller manager: 控制器管理器，控制器监控防止kubernetes不可用，运行于master节点

##### 	Deployment

​        声明式更新控制器，只能管理无状态应用，使用较多

​		管理pod和ReplicatiSet

​			ReplicaSet: 副本集控制器，结合其他控制器一起使用

​    	上线部署、副本设定、滚动升级、回滚等功能

​    	提供声明式更新，例如之更新一个新的image

##### 	StatefulSet:

​    	管理有状态副本集

​		解决pod独立生命周期，保持pod启动顺序

​    	稳定唯一的网络标识符（通过DNS），使用headless service(没有clusterIP)

​		和持久化存储(使用volumeclaimtemplate创建，称为卷申请模板，创建persistentvolume时为每个pod分配并创建一个独一无二的pvc)

​      有序，优雅部署和扩展、删除和终止

​      有序，滚动更新

​		挂载原来的volume

##### 	DaemonSet: 

​		在所有Node(包括master)上运行pod副本，当node加入集群时创建pod，当node离开集群时回收pod，如果删除DaemonSet，其创建的所有pod也被删除，DaemonSet中的pod覆盖整个集群

​		运行存储守护，集群日志收集，节点监控

####   job

需要时启动，不需要时关闭

##### 	cronjob

周期性执行任务

### Ingress Controller

​	管理Ingress，根据ingress的定义生成具体的路由，具有负载均衡的功能

### ConfigMap

​	存储应用程序配置文件

​	使用方式: 

​		变量注入

​		数据卷挂载

### Secret

​	存储敏感数据，所有数据经过base64编码

​	三种类型:

​		docker-registry: 存储镜像仓库认证信息

​		generic: 从文件、目录或者字符串创建，例如存储用户名密码

​		tls: 存储证书，例如HTTPS证书

## 三、通信方式

### overlay概念

​	原始数据包经过vxlan再次封装

​		原始数据包: 

​			{Ethernet-IP-tcp/udp-data}

​		vxlan数据包: 

​			{out_ethernet-out_IP-out_UDP(vxlan_port:4789)-vxlan_header-{Ethernet-IP-tcp/udp-data}(原始数据包)}

### 节点网络 

​	服务器节点之间的通信

​	NodeIP是集群每个节点的物理网卡IP地址

### 集群网络 Overlay

​	Service⼀旦被创建，Kubernetes就会⾃动为它分配⼀个可⽤的、全局唯一的、不变的ClusterIP地址，可以通过这个虚拟IP地址+服务的端⼜直接访问该服务

​	ClusterIP必须与端口结合才能通信

​	DNS映射: 我们只要使⽤服务的名称（DNS名称）即可完成到⽬标服务的访问请求。

​	服务之间通过TCP/IP进⾏通信

​		service与外部网络: 

​			外部向NodeIP:NodePort发送数据包>DNAT→ClusterIP:port>经过负载均衡组件到Pod

​		containers通信方式: 

​			同一pod中的containers通过127.0.0.1/loop通信

​			共享Pause容器的IP,Pod IP(唯一)，由docker分配

​		pod之间: 

​			各node之间的相同pod通过Overlay Network(二层报文或三层隧道报文)进行直接通信(虚拟直连)

​			pod1发送数据包>网桥找不到pod2的MAC>转发到flannel0>封装成vxlan数据包>根据flannel内部MAC/路由发送另一个NodeIP:4789>flannel侦听4789接收到vxlan数据包，还原回原始数据包>发送给pod2

​		pod与其他service的pod通信: 

​			server的服务发现通过label标签找到各服务对应的pod，记录pod的IP:port

​		pod访问其他service: 

​			pod1发送数据包>本地网桥VBR>本地网桥VBR查找不到serverIP的MAC,转发给默认路由自己的serverIP>转发给想要通信的serverIP>对方的serverIP经过iptables-DNAT>pod的Pause容器网卡

## 四、监控|日志

### 查看kubelet日志

```shell
  journalctl -u kubelet
```

### pod或组件日志

```shell
kubectl logs pod_name -n namespace
```

### 系统日志

```shell
/var/log/messages
```



### 容器日志持久化保存位置

```shell
/var/log/docker/containers/<container-id>/<container-id>-json.log
/var/log/pods/<container-id>/
/var/log/containers/<container-id>
```

emptyDIR

```shell
/var/lib/kubelet/pods/<pod-id>/volumes/kubernetes.io~empty-dir/logs/access.log
```



### 日志收集方式

  针对标准输出：以DaemonSet方式在每个Node上部署一个日志收集程序，采集/var/lib/docker/containers/目录下所有容器日志
  针对容器中日志文件：在Pod中增加一个容器运行日志采集器，使用emtyDir共享日志目录让日志采集器读取到日志文件

## 五、kubernetes部署应用程序流程

### 1.制作镜像

  dockerfile

### 2.使用控制器部署镜像

  Deployment

​    升级方式: 

```shell
      kubectl apply -f xxx.yaml
      kubectl set image deployment deployment_name containers_name=image_name:version
      kubectl edit deployment deployment_name
```

​    扩缩容:

```shell
      kubectl scale deployment web --replicas=10
```

​      或修改yaml文件

  StatefulSet

  DaemonSet

### 3.对外暴露应用

  Service

  Ingress

### 4.日志、监控

### 5.日常运维

## 六、创建pod的流程

kubectl run > 发给api server > 请求的配置写入etcd > scheduler通过list/watch获取到pod配置 > 选择一个合适的节点bind pod，然后返回结果给api server > api server write etcd > 节点的kubelet 通过watch获取自己对应要创建的容器，创建后update pod status 返回结果 api server >api server write etcd

## 七、调度

1.容器资源限制：

• resources.limits.cpu

• resources.limits.memory

容器使用的最小资源需求，作为容器调度时资源分配的依据：

• resources.requests.cpu

• resources.requests.memory

2.节点选择

nodeName		最高，不经过调度器

taint			污点，根据策略不调度，除非pod带有污点容忍

nodeSelector=nodeAffinity	调度器协调

3.DaemonSet		

固定每个节点都运行副本，如果节点有污点，则需要设置容忍

```yaml
      tolerations:
      - operator: "Exists"
        effect: "NoSchedule"
```

## 八、volume

emptyDir卷: 是一个临时存储卷，与pod生命周期绑定，pod删除volume也删除

​	应用场景: pod中的容器数据共享

hostPath卷：挂载Node文件系统（Pod所在节点）上文件或者目录到Pod中的容器。

​	应用场景：Pod中容器需要访问宿主机文件

NFS卷：提供对NFS挂载支持，可以自动将NFS共享路径挂载到Pod中

​	应用场景：不同节点高可用共享存储

pv|pvc: 逻辑卷，有动态和静态2种供给方式

​	静态：pv|pvc一一对应

​	动态：从pvpool中分配,通过storageclass对象实现

​		一部分需要插件实现，如nfs

​		通过需求创建PV

```
status（状态）:
  available: 表示可用
  bound：表示pv绑定pvc
  released: pvc被删除，但是资源未被删除
  failed: 表示pv的自动回收失败
```

## 九、安全框架

### kubectl,API,UI 

↓

### /api/v1 /apis /healthz /logs /swagger-ui /metrics

↓

### Authentication(鉴权)

​	客户端访问API server 需要证书、Token或者用户名+密码

​		HTTPS 证书认证: 基于CA证书签名的数字证书认证

​		HTTP Token认证: 通过一个Token来识别用户

​		HTTP Base认证: 用户名+密码的方式认证

​	pod访问 需要ServiceAccount

↓

### Authorization(授权)

​	RBAC（Role-Based Access Control，基于角色的访问控制）

​		负责完成授权（Authorization）工作。

​		RBAC根据API请求属性，决定允许还是拒绝。

​		1.比较常见的授权维度：

​			user：用户名

​			group：用户分组

​		2.资源，例如pod、deployment

​		3.资源操作方法：get，list，create，update，patch，watch，delete

​		4.命名空间

​			API组

​		5.主体: 具体的用户、群组
​			user
​			group
​			ServiceAccount: 服务账号，针对程序
​		6.角色: 职业，权限的分组
​			Role: 授权特定命名空间的访问权限
​			ClusterRole: 授权所有命名空间的访问权限
​		7.角色绑定: 
​			RoleBinding: 将角色绑定到主体（即subject）
​			ClusterRoleBinding: 将集群角色绑定到主体
↓

### Admission Cintrol(准入控制)

​	Adminssion Control实际上是一个准入控制器插件列表，发送到API Server的请求都需要经过这个列表中的每个准入控制器插件的检查，检查不通过，则拒绝请求
↓

### pod svc controllers storage …

↓

### ETCD CLUSTER

十、网络策略|Network Policy

网络策略（Network Policy），用于限制Pod出入流量，提供Pod级别和Namespace级别网络访问控制。

一些应用场景：

• 应用程序间的访问控制。例如微服务A允许访问微服务B，微服务C不能访问微服务A

• 开发环境命名空间不能访问测试环境命名空间Pod

• 当Pod暴露到外部时，需要做Pod白名单

• 多租户网络环境隔离

Pod网络入口方向隔离：

• 基于Pod级网络隔离：只允许特定对象访问Pod（使用标签定义），允许白名单上的IP地址或者IP段访问Pod

• 基于Namespace级网络隔离：多个命名空间，A和B命名空间Pod完全隔离。

Pod网络出口方向隔离：

• 拒绝某个Namespace上所有Pod访问外部

• 基于目的IP的网络隔离：只允许Pod访问白名单上的IP地址或者IP段

• 基于目标端口的网络隔离：只允许Pod访问白名单上的端口

## 十一、故障分析

查看K8s有哪些资源

```shell
kubectl api-resources
```

当我们使用kubectl工具执行出现错误怎么排查？

```shell
kubectl -> kube-apiserver -> etcd
```

当get node有节点显示NotReady状态怎么排查？

```shell
kubelet -> runtime
```

当kubectl top执行出现错误怎么排查？

```
1、kubectl get apiservice，kubectl describe apiservice v1beta1.metrics.k8s.io
2、如果describe出现网络错误，在二进制部署环境，一般是master没有部署node组件或者没有启用k8s聚合层
3、kubectl logs metrics-server-84f9866fdf-vd22z -n kube-system
```

怎么查看k8s组件日志？

```
kubeadm搭建的集群：apiserver、etcd、controller-manager、scheduler，kubelet（我是systemd守护进程管理，其他组件都是采用容器部署）、kube-proxy
二进制搭建的集群：所有组件都是采用systemd守护进程管理
```

k8s查看标准输出日志流程：

```
kubectl logs -> apiserver -> kubelet -> docker（接管了容器标准输出日志并写入了/var/lib/docker/containers/<container-id>/<container-id>-json.log）
```

进入所有容器终端命令：

```shell
kubectl exec -it web-96d5df5c8-r7hkm -- bash
```

日志平台搭建哪个技术用的多？

```
ELK：重量级 Elasticsearch+Logstash（日志采集器，使用go写了filebeat替代日志采集功能）+Kibana
Graylog、Loki：轻量级
```

官方推荐的EFK日志系统是啥？ 

```
Elasticsearch+Flunend（日志采集器）+Kibana
```



### 1.针对应用

```shell
kubectl describe TYPE/NAME
kubectl logs TYPE/NAME [-c CONTAINER]
kubectl exec POD [-c CONTAINER] -it  
```

### 2.machine-log

kubeadm 除kubelet外，其他组件都是静态pod

二进制 全是systemd管理

```shell
journalctl -u kubelet|grep -i -E "error|failed"
```

常见问题：

​	网络

​	启动失败，查配置文件或者依赖服务

​	平台不兼容

### 3.kubernetes设置

service访问不通，排查顺序

​	是否关联pod

​		检查Selector和labels是否设置正确

​	pod_port是否正确

​	pod正常工作吗

​		telnet|curl测试一下pod_port

​		exec -it 进入pod查看详情

​	DNS解析是否正常

​		kube-proxy正常工作吗

```shell
			kubectl edit configmap kube-proxy -n kube-system
```

​		kube-proxy正常写iptables规则吗

​	cni网络插件是否正常工作

## 十二、部署方式

### kubeadm

  0.准备

​    关闭firewalld

​	同步时间

​    关闭swap

```shell
      swapoff -a
```

/etc/fstab

```shell
# swap # 注释
```

检查br_netfilter、overlay是否启用

```shell
      lsmod | grep br_netfilter # 检查
      modprobe br_netfilter # 启用模块
```

```shell
cat <<EOF | tee /etc/modules-load.d/k8s.conf
br_netfilter
overlay
EOF
cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl --system
```

​	或

```shell
cat > kubernetes.conf <<EOF 
net.ipv4.tcp_timestamps=1
net.ipv4.tcp_tw_reuse=1
net.bridge.bridge-nf-call-iptables=1 
net.bridge.bridge-nf-call-ip6tables=1 
net.ipv4.ip_forward=1 
net.ipv4.tcp_tw_recycle=0  #4.1以后内核版本已经抛弃了这个参数可以删除
vm.swappiness=0 # 禁止使用 swap 空间，只有当系统 OOM 时才允许使用它 vm.overcommit_memory=1 # 不检查物理内存是否够用 
vm.panic_on_oom=0 # 开启 OOM 
fs.inotify.max_user_instances=8192 
fs.inotify.max_user_watches=1048576 
fs.file-max=52706963 
fs.nr_open=52706963 
net.ipv6.conf.all.disable_ipv6=1 
net.netfilter.nf_conntrack_max=2310720 
EOF
sysctl --system
```

1.安装docker|containerd

2.安装 kubelet kubeadm kubectl

centos

```shell
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
yum install -y --nogpgcheck kubelet kubeadm kubectl
systemctl enable kubelet
```

3.kuberadmin init

```shell
kubeadm init \
  --apiserver-advertise-address=192.168.1.120 \
  --image-repository docker.io/gotok8s \
  --kubernetes-version v1.23.5 \
  --service-cidr=10.96.0.0/12 \
  --pod-network-cidr=10.244.0.0/16 \
  --ignore-preflight-errors=all
```

此时如果不能启动kubelet

​	/etc/docker/daemon.json

```json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
  "overlay2.override_kernel_check=true"
  ]
}
```

4.启动kubelet

```shell
systemctl start kubelet
```

5.非root用户没有访问/etc/kubernetes/admin.conf的权限，所以要

```shell
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

6.其余节点的加入

```shell
#24小时以内↓
kubeadm join 192.168.1.120:6443 --token egqnfa.7brw1qtgkhtu07dc --discovery-token-ca-cert-hash sha256:66cf62e11eed28bcdd90bf9ef79f9a0c68dd56a2c916f87fabfb70f883f817d4
#24小时以后↓
kubeadm token create --print-join-command
kubeadm join 192.168.1.120:6443 --token egqnfa.7brw1qtgkhtu07dc --discovery-token-ca-cert-hash sha256:66cf62e11eed28bcdd90bf9ef79f9a0c68dd56a2c916f87fabfb70f883f817d4
```

7.确认worker节点加入

```shell
    kubectl get nodes   #查看当前节点
    kubectl get cs    #检查健康度
```

8.部署网络插件

calico

```shell
curl https://projectcalico.docs.tigera.io/manifests/calico-typha.yaml -o calico.yaml
# 修改calico.yaml中的CALICO_IPV4POOL_CIDR为前面设置的pod的IP范围(可省略)
kubectl apply -f calico.yaml
kubectl get pods -n kube-system   #查看是否成功
```

9.部署dashboard

```shell
kubectl apply -f kubernertes-dashboard.yaml
kubectl get pods -n kubernetes-dashboard   #查看部署是否成功
kubectl create serviceaccount dashboard-admin -n kube-system  #创建一个用户
kubectl get serviceaccounts dashboard-admin -n kube-system -o yaml   #检查关联的密钥
kubectl get secret -n kube-system  dashboard-admin-token-47pnk -o yaml   #输出secret配置
kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=kube-system:dashboard-admin   #给用户授权：管理员
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/dashboard-admin/{print $1}')   #获取token
```

10.切换容器引擎为Containerd

启用overlay、br_netfilter

```shell
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system
```

安装containerd

```shell
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
yum update -y && sudo yum install -y containerd.io
mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
systemctl restart containerd
```

/etc/containerd/config.toml

```shell
   [plugins."io.containerd.grpc.v1.cri"]
      #sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.2"  
      sandbox_image = "docker.io/gotok8s/pause:3.7"  
         ...
         [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
             SystemdCgroup = true
             ...
        #[plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
          #endpoint = ["https://b9pmyelo.mirror.aliyuncs.com"]
```

```shell
systemctl restart containerd
```

配置kubelet使用containerd

/etc/sysconfig/kubelet 

```shell
KUBELET_EXTRA_ARGS=--container-runtime=remote --container-runtime-endpoint=unix:///run/containerd/containerd.sock --cgroup-driver=systemd
```

```shell
systemctl restart kubelet
systemctl restart containerd && systemctl enable containerd
systemctl disable docker 
```

11.metrics server部署

```shell
wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml -O metrics-server.yaml
```

metrics-server.yaml

```shell
containers:
- name: metrics-server
…………
  - --kubelet-insecure-tls
  - --kubelet-preferred-address-types=InternalIP
  image: docker.io/bitnami/metrics-server:0.6.1
```

查找dockerhub里的可用镜像，使用crictl下载

```shell
crictl pull docker.io/bitnami/metrics-server:0.6.1
kubectl apply -f metrics-server.yaml
```

12.ipvs代理模式

```shell
kubectl edit configmap kube-proxy -n kube-system
```

```shell
...
  mode: “ipvs“
...
```

需要重建kube-proxy

```shell
kubectl delete pod kube-proxy-btz4p -n kube-system
```

13.Ingress Controller

```shell
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.3/deploy/static/provider/cloud/deploy.yaml -O ingress-nginx.yaml
```

dockerd驱动

```shell
docker pull docker.io/willdockerhub/ingress-nginx-controller:v1.1.3
docker pull docker.io/dyrnq/kube-webhook-certgen:v1.1.1
```

containerd驱动

```shell
crictl pull docker.io/willdockerhub/ingress-nginx-controller:v1.1.3
crictl pull docker.io/dyrnq/kube-webhook-certgen:v1.1.1
```

修改部署文件(一共三处修改)

```yaml
...
  name: ingress-nginx-controller
  kind: DaemonSet
...
      hostNetwork: true
...
image: dokcer.io/willdockerhub/ingress-nginx-controller:v1.1.3
…
      tolerations:
      - key: ""
        operator: "Exists"
        effect: "NoSchedule"

image: docker.io/dyrnq/kube-webhook-certgen:v1.1.1
```

部署

```shell
kubectl apply -f ingress-nginx.yaml
```

## 十三、运维(kubeadm)

### 备份|还原ETCD数据库

备份

```shell
ETCDCTL_API=3 etcdctl \
snapshot save snap.db \
--endpoints=https://127.0.0.1:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt \
--cert=/etc/kubernetes/pki/etcd/server.crt \
--key=/etc/kubernetes/pki/etcd/server.key 

--endpoints   #指定宿主机IP
```

恢复:

先暂停kube-apiserver和etcd容器

```
mv /etc/kubernetes/manifests /etc/kubernetes/manifests.bak
mv /var/lib/etcd/ /var/lib/etcd.bak
```

恢复

```shell
ETCDCTL_API=3 etcdctl \
snapshot restore snap.db \
--data-dir=/var/lib/etcd
```

启动kube-apiserver和etcd容器

```shell
mv /etc/kubernetes/manifests.bak /etc/kubernetes/manifests
```

### 集群升级

升级管理节点：

查找最新版本号

```shell
yum list --showduplicates kubeadm --disableexcludes=kubernetes
```

升级kubeadm

```shell
yum install -y kubeadm-1.19.3-0 --disableexcludes=kubernetes
```

驱逐node上的pod，且不可调度

```shell
kubectl drain k8s-master --ignore-daemonsets
```

检查集群是否可以升级，并获取可以升级的版本

```shell
kubeadm upgrade plan
```

执行升级

```shell
kubeadm upgrade apply v1.19.3
```

取消不可调度

```shell
kubectl uncordon k8s-master
```

升级kubelet和kubectl

```shell
yum install -y kubelet-1.19.3-0 kubectl-1.19.3-0 --disableexcludes=kubernetes
```

重启kubelet

```shell
systemctl daemon-reload
systemctl restart kubelet
```

升级工作节点：

升级kubeadm

```shell
yum install -y kubeadm-1.19.3-0 --disableexcludes=kubernetes
```

驱逐node上的pod，且不可调度

```shell
kubectl drain k8s-node1 --ignore-daemonsets
```

升级kubelet配置

```shell
kubeadm upgrade node
```

升级kubelet和kubectl

```shell
yum install -y kubelet-1.19.3-0 kubectl-1.19.3-0 --disableexcludes=kubernetes
```

重启kubelet

```shell
systemctl daemon-reload
systemctl restart kubelet
```

取消不可调度，节点重新上线

```shell
kubectl uncordon k8s-node1
```

### 集群节点上下线

获取节点列表

```shell
kubectl get node
```

驱逐节点上的Pod并设置不可调度（cordon）

```shell
kubectl drain <node_name> --ignore-daemonsets
```

3、设置可调度或者移除节点

```shell
kubectl uncordon <node_name> 
kubectl delete node <node_name>
```

### CA认证及角色授权

 为指定用户授权不同命名空间权限

创建CA配置文件

```json
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "87600h"
    },
    "profiles": {
      "kubernetes": {
        "usages": [
            "signing",
            "key encipherment",
            "server auth",
            "client auth"
        ],
        "expiry": "87600h"
      }
    }
  }
}
EOF
```

用户CA信息

```json
cat > user_name-csr.json <<EOF
{
  "CN": "user_name",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "group_name",
      "OU": "System"
    }
  ]
}
EOF
```

生成用户CA证书

```shell
cfssl gencert -ca=/etc/kubernetes/pki/ca.crt -ca-key=/etc/kubernetes/pki/ca.key -config=ca-config.json -profile=kubernetes user_name-csr.json | cfssljson -bare user_name
```

生成kubeconfig授权文件

cluser

```shell
kubectl config set-cluster kubernetes \
--certificate-authority=/etc/kubernetes/pki/ca.crt \
--embed-certs=true \
--server=https://192.168.31.61:6443 \
--kubeconfig=user_name.kubeconfig
```

client

```shell
kubectl config set-credentials user_name \
--client-key=user_name-key.pem \
--client-certificate=user_name.pem \
--embed-certs=true \
--kubeconfig=user_name.kubeconfig
```

上下文

```shell
kubectl config set-context kubernetes \
--cluster=kubernetes \
--user=user_name \
--kubeconfig=user_name.kubeconfig
```

设置使用配置

```shell
kubectl config use-context kubernetes --kubeconfig=user_name.kubeconfig
```

创建RBAC权限策略

​	创建一个角色

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
#apiGroups 可以指定 kubectl api-versions 中的内容 如：apps
#resources 可以指定 kubectl api-resources 中的内容 如： deployments
#verbs 可以指定方法get、list、create、update、patch、watch、delete
```

将角色和用户绑定

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: user_name
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

使用

```shell
kubectl get pod --kubeconfig=user_name.kubeconfig
```

## 十四、kubectl

```shell
***常用
kubectl logs pod_name -n namespace_name
#查看pod日志
kubectl describe pod pod_name -n namespace_name
#查看pod事件
kubectl apply -f name.yaml
#应用部署、升级
kubectl delete  -f name.yaml
#删除部署
kubectl run -it --rm --image=busybox -- sh
#建立一个测试用的pod

###########基础
kubectl
  kubectl get
    node   #节点
    cs   #该node节点组件状态
    namespace   #查看namespace
      default: 默认的命名空间
      kube-system: k8s系统
      kube-public: 公开的命名空间，都可以访问
      kube-node-lease: K8S内部命名空间
    ep   #查看endpoint（k8s暴露的集群IP及端口、服务对应的pod的IP及端口）
    depolyment   #查看部署的工程
    pod   #容器
    svc   #服务
    pv   #查看逻辑卷池
    pvc   #查看逻辑卷
    sc   #查看存储类
      --show-labels   #查看资源的标签
      -l   #根据标签筛选资源
      -n   #指定namespace
  kubectl create   #部署一个工程
    deployment
      kubectl create deployment deploy_name --image=image_name
      -n   #指定namespace
      --dry-run=client   #测试，不实际生成资源
      -o #输出格式yaml、json
      > #将内容输出到文件配合-o使用
    secret
      kubectl create secret 
      docker-registry: #存储镜像仓库认证信息
      generic: #从文件、目录或者字符串创建，例如存储用户名密码
      tls: #存储证书，例如HTTPS证书
  kubectl expose   #将pod节点暴露出去
    kubectl expose deployment deploy_name --port=pod_port --targer-port=service_port --type=NodePort
      -n   #指定namespace
      --port #服务端口
      --targer-port #pod端口
      --type #指定暴露的类型
        =NodePort#指集群的端口（访问任意一个节点都可以使用）
  kubectl apply   #部署
    -f xx.yaml 指定部署的文件
  kubectl patch   #使用补丁方式修改、更新资源的某些字段
  kubectl replace   #从文件名或标准输入替换一个资源
  kubectl convert   #在不同API版本之间转换对象定义
  kubectl completion bash
    shell> source /usr/share/bash-completion/bash_completion
    shell> source <(kubectl completion bash)
    shell> bash
  kubectl run   #在集群中运行一个特定的镜像
  kubectl set   #在对象上设定特定的功能
    kubectl set image deployment deployment_name containers_name=image_name:version
      --record   #记录命令到kubectl rollout history deployment deployment_name中的CHANGE-CAUSE
  kubectl explain   #文档参考资料
    kubectl explain kind_name.fields_name1.fields_name2
  kubectl edit   #使用系统编辑器编辑一个资源
    kubectl edit deployment deployment_name   #在线编辑yaml文档
  kubectl delete   #通过文件名、标准输入、资源名称或标签选择器来删除资源

##########部署命令
  kubectl rollout   #管理Deployment,daemonset资源的发布（例如状态、发布记录、回滚等）
    kubectl rollout history deployment deployment_name   #查看历史记录
    kubectl rollout undo deployment deployment_name 
      --to-revision=2   #回滚指定的版本
  kubectl rolling-update   #滚动更新，仅限replication
  kubectl scale   #对Deployment,replicaset、rc或job资源扩容或缩容pod数量
  kubectl autoscale   #自动伸缩（依赖metrics-server和hpa）

########集群管理命令
  kubectl certificate   #修改证书资源
  kubectl cluster-info   #显示集群信息,api-server代理的url
    dump   #详细信息
  kubectl top   #查看资源利用率（依赖metrics-server）kubectl>apiserver>metrics-server>kubelet(cadvisor)
    node   #节点资源利用率
    pod   #pod的资源利用率
      kubectl top pod -A --no-headers --sort-by=cpu
        -A   #所有namespace
        --no-headers   #不输出标题
        --sort-by     #排序cpu、memory
  kubectl cordon   #标记节点不可调度
  kubectl uncordon   #标记节点可调度
  kubectl drain   #驱逐节点上的应用，准备下线维护
  kubectl taint   #修改节点taint标记
    kubectl taint node hostname key=value:effect   #设置节点的污点标记
      effect可选NoSchdule   PreferNoSchedule   NoExecute 
        NoSchdule一定不可调度
        PreferNoSchedule尽量不可调度
        NoExecute不仅不会调度，还会驱逐Node上的已有pod
    kubectl taint node hostname key=value:[effect]-   #去除污点
#########故障诊断和调试
  kubectl describe   #显示资源详细信息
  kubectl logs pod_name   #查看Pod内容器日志，如果Pod有多个容器，
    -f   类似tali -f ，动态输出
    -c   参数指定容器名称
    -n   指定namespace
  kubectl attach   #附加到Pod内的一个容器
  kubectl exec   #在容器内执行命令
    kubectl exec -it pod_name -- bash -n namespace   #进入容器终端
  kubectl port-forward   #为Pod创建本地端口映射
  kubectl proxy   #为Kubernetes API server创建代理
  kubectl cp   #拷贝文件或目录到容器中，或者从容器内向外拷贝

########设置命令
  kubectl label   #给资源设置、更新标签
    kubectl label nodes hostname key=value    #给节点打标签
  kubectl annotate   #给资源设置、更新注解

########其他
  kubectl api-resources   #查看所有资源（功能）
  kubectl api-versions   #打印受支持的API版本
  kubectl config   #修改kubeconfig文件（用于访问API，比如配置认证信息）
  kubectl help   #所有命令帮助
  kubectl version 查看kubectl和k8s版本
```

## 十五、yaml模板

### 定义namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: Namespace
#metadata一般定义三种数据labels|name|namespace 
#kubectl explain kind_name.metadata可以查看可定义的字段
```

### 定义ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: www.lxw.com-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
#要指定ingressClass为nginx
  ingressClassName: nginx
  rules:
  - host: server.lxw.com
    http:
      paths:
      - path: /
#pathType定义匹配方式
#Prefix前缀匹配|Exact精确匹配|ImplementationSpecific取决于ingressClass
        pathType: Prefix
#backend定义后端
        backend:
          service:
            name: nginx
            port:
              number: 80
```

### 定义ServiceAccount

```shell
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
```

### 定义service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: service_name
  namespace: namespace
#labels是给自己打标签selector是搜索对应pod的标签
  labels: 
    app: service_name
spec:
  ports:
    - port: 80
      name: http
      protocol: TCP
      targetPort: 80
    - port: 443
      name: https
      protocol: TCP
      targetPort: 443
      nodePort: 30001
#port.nodeport可定义对外指定监听的端口|port.port指service的端口|targetPort是pod的端口
##type指service的工作模式NodePort对集群外提供|ClusterIP集群内部使用（默认）|LoadBalancer对外暴露，适用于公有云
  type: NodePort
#selector选择标签，pod的标签
  selector:
    app: deployment_name
#来基于客户端的 IP 地址选择会话关联,None失效
  sessionAffinity: clientIP
```

### Deployment

```shell
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment_name
  namespace: namespace
  labels: 
    app: deployment_name
spec: 
#直接修改replicas可以实现水平扩容，缩容
  replicas: 1
#revisionHistoryLimit历史版本记录限制副本数，用来指定可以保留的旧的ReplicaSet数量
  revisionHistoryLimit: 10
  selector: 
    matchLabels: 
#需要筛选的pod的标签,在template.metadata.labels中定义的
      app: deployment_name
#strategy是指定该deployment的策略
#支持的类型有
#Rrecreate关闭版本A后部署版本B，会有停机时间
#RollingUpdate更新期间版本A或更新完成的B提供服务，完成后关闭A版本
#可以设置maxUnavailable决定更新过程中最大不可用POD的数量或百分比，默认25%
#maxSurge可创建超过期望的POD数量或百分比，默认25%（比如期望有4个pod运行，但不可用最多0个，这时就需要在 不停止旧POD的形况下新增一定数量的新pod
  strategy:
    type: RollingUpdate
    rollingUpdate: 
      maxUnavailable: 20%
      maxSurge: 1
#template指pod模板
  template:
    metadata: 
      labels: 
        app: deployment_name
    spec: 
#securityContext是安全上下文
      securityContext: 
        seccompProfile:
          type: RuntimeDefault
#指定节点运行，不经过调度器（优先度最高）
      nodeName: server.lxw.com
#nodeselector用于把pod调度到匹配label的node上，如果没有匹配的标签会调度失败
#标签是key: value的形式
#kubectl label nodes hostname key=value 可以给节点打标签
      nodeSelector: 
        disktype: "ssd"
#nodeAffinity节点亲和，比起nodeselector匹配更有逻辑性，不只是字符串的完全相等
#调度分为软策略和硬策略，而不是硬性要求
#硬策略 required 必须满足
#软策略 preferred 尝试满足，但不保证
#操作符 In NotIn （有没有）Exists DoesNotExist （key是否存在，不指定value） Gt Lt 
      nodeAffinity: 
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: kubernetes.io/os
              operator: In
              values:
              - linux
#↑必须kubernetes.io/os=linux
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 1
          preference:
            matchExpressions:
            - key: hostname
              operator: In
              values:
              - www.lxw.com
#↑尝试满足hostname=www.lxw.com，存在多个条件时weight的加和决定节点的选择
#tolerations允许pod运行到持有污点key=value的节点上时 （容忍它的NoSchedule性质）
      tolerations:
      - key: "key"
        operator: "Equal"
        value: "value"
        effect: "NoSchedule"
#不匹配key=value，全NoExecute污点标记容忍
      - operator: "Exists"
        effect: "NoExecute"
#pod重启策略配合健康检查使用Always|OnFailure|Never，默认Always
      restartPolicy: Always
      schedulerName: default-scheduler
#initContainers是一次性容器，最先启动
      initContainers:
        - name: busybox
          image: busybox
          command: ['sh', '-c', "until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for myservice; sleep 2; done"]
      containers: 
        - name: deployment_name
          image: image_name
#imagePullPolicy一共三种模式IfNotPresent|Always|Never
          imagePullPolicy: Always
#resources资源分配策略，requests最小分配，limits最大分配
          resources: 
            requests: 
              memory: "61Mi"
              cpu: "250m"
            limits: 
              memory: "128Mi"
              cpu: "500m"
          ports:
#containerPort容器的端口（不是port，port是pod端口）
            - containerPort: 8443
              protocol: TCP
#定义健康检查的方式和端口
          readinessProbe:
            tcpSocket: 
              port: 8443
#启动容器后多少秒进行健康检查
            initialDelaySeconds: 30
#之后多少秒检查一次
            periodSeconds: 10
          livenessProbe:
            tcpSocket:
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
#httpget的健康检查
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
              httpHeaders:
              - name: Custom-Header
                value: Awesome
            initialDelaySeconds: 3
            periodSeconds: 3
#args额外参数，类似添加在命令行的
          args:
            - --auto-generate-certificates
            - --namespace=kubernetes-dashboard
#volumeMounts挂载逻辑卷
          volumeMounts:
            - name: kubernetes-dashboard-certs
              mountPath: /certs
              # Create on-disk volume to store exec logs
            - mountPath: /tmp
              name: tmp-volume
            - mountPath: /html
              name: vol_name3
#定义volumes
      volumes:
        - name: vol_name1
          emptyDir: {}
#定义本地文件夹挂载
        - name: vol_name2
          hostPath:
            path: /tmp
            type: Directory
        - name: vol_name3
          persistentVolumeClaim:
            claimName: pvc0001
```

### stateful

```shell
apiVersion: v1
kind: Service
metadata:
  name: stateful-nginxsvc
  labels:
    app: stateful-nginxsvc
spec:
  ports:
  - port: 80
    name: www
#clusterIP必须为None，有状态采用pod之间直接通信
  clusterIP: None
  selector:
    app: nginxpod
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: stateful-nginx
spec:
#matchlabels必须匹配spec.template.metadata.labels
  selector:
    matchLabels:
      app: nginx-pod
#绑定svc
  serviceName: "stateful-nginxsvc"
  replicas: 2
  template:
    metadata:
#LABELS必须匹配spec.selector.matchLabels
      labels:
        app: nginx-pod
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
          name: www
        volumeMounts:
        - name: html01
          mountPath: "/usr/share/nginx/html"
#volumeClaimTemplates有状态专用
  volumeClaimTemplates:
  - metadata:
      name: html01
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "nfs-sc-001"
      resources:
        requests:
          storage: 1Gi
```

### 持久化数据卷定义PV

```shell
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
  labels: 
    pvName: pv0001
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
#accessModes一共有4种
#ReadWriteOnce单节点读写
#ReadOnlyMany多节点只读
#ReadWriteMany多节点读写
#ReadWriteOncePod被单个pod以读写方式挂载
  accessModes:
    - ReadWriteMany
#persistentVolumeReclaimPolicy回收策略retain保留|recycle回收|delete删除
  persistentVolumeReclaimPolicy: Recycle
  storageClassName: slow
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /nfs
    server: 192.168.51.53
```

### 卷需求模板PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc0001
  labels: 
    pvName: pvc0001
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 5Gi
  storageClassName: slow
  selector:
    matchLabels:
      pvName: pv0001
    #matchExpressions:
      #- {key: environment, operator: In, values: [dev]}
```

### pv静态供给

```yaml
#pv静态供给
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
  labels:
    pvName: pv0001
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteMany
  nfs:
    path: /nfs
    server: 192.168.51.53
```

### pv动态供给（通过storageclass实现）

```
#创建PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-0001
spec:
#指定创建的sc，可以使用kubectl get sc来获取
  storageClassName: "nfs-sc-001"
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
---
#使用pvc的pod
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pvc-dt-test
spec:
  containers:
  - name: nginx-pvc-dt-test
    image: nginx
    volumeMounts:
    - name: html01
      mountPath: "/usr/share/nginx/html"
  volumes:
  - name: html01
    persistentVolumeClaim:
      claimName: pvc-0001
---
#创建storageclass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-sc-001
#provisioner不要改动
provisioner: k8s-sigs.io/nfs-subdir-external-provisioner # or choose another name, must match deployment's env PROVISIONER_NAME'
#parameters参数: archiveOnDelete回收策略 false回收不删除数据
parameters:
  archiveOnDelete: "false"
---
#连接api-server
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-client-provisioner
  # replace with namespace where provisioner is deployed
  namespace: default
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: nfs-client-provisioner-runner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-nfs-client-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    # replace with namespace where provisioner is deployed
    namespace: default
roleRef:
  kind: ClusterRole
  name: nfs-client-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  # replace with namespace where provisioner is deployed
  namespace: default
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  # replace with namespace where provisioner is deployed
  namespace: default
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    # replace with namespace where provisioner is deployed
    namespace: default
roleRef:
  kind: Role
  name: leader-locking-nfs-client-provisioner
  apiGroup: rbac.authorization.k8s.io
---
#nfs非官方支持需要部署pod连接nfs后端
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-client-provisioner
  labels:
    app: nfs-client-provisioner
  # replace with namespace where provisioner is deployed
  namespace: default
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: nfs-client-provisioner
  template:
    metadata:
      labels:
        app: nfs-client-provisioner
    spec:
      serviceAccountName: nfs-client-provisioner
      containers:
        - name: nfs-client-provisioner
#镜像位置
          image: lizhenliang/nfs-subdir-external-provisioner:v4.0.1
#挂载到PV
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
#定义NFS相关信息（动态）
          env:
            - name: PROVISIONER_NAME
              value: k8s-sigs.io/nfs-subdir-external-provisioner
            - name: NFS_SERVER
              value: 192.168.51.53
            - name: NFS_PATH
              value: /nfs
##定义NFS相关信息（静态）
      volumes:
        - name: nfs-client-root
          nfs:
            server: 192.168.51.53
            path: /nfs
```

### configmap

```shell
apiVersion: v1
kind: ConfigMap
metadata:
  name: game-demo
data:
  # 类属性键；每一个键都映射到一个简单的值
  player_initial_lives: "3"
  ui_properties_file_name: "user-interface.properties"

  # 类文件键
  game.properties: |
    enemy.types=aliens,monsters
    player.maximum-lives=5    
  user-interface.properties: |
    color.good=purple
    color.bad=yellow
    allow.textmode=true
---
apiVersion: v1
kind: Pod
metadata:
  name: configmap-demo-pod
spec:
  containers:
    - name: demo
      image: alpine
      command: ["sleep", "3600"]
      env:
        # 定义环境变量
        - name: PLAYER_INITIAL_LIVES # 请注意这里和 ConfigMap 中的键名是不一样的
          valueFrom:
            configMapKeyRef:
              name: game-demo           # 这个值来自 ConfigMap
              key: player_initial_lives # 需要取值的键
        - name: UI_PROPERTIES_FILE_NAME
          valueFrom:
            configMapKeyRef:
              name: game-demo
              key: ui_properties_file_name
      volumeMounts:
      - name: config
        mountPath: "/config"
        readOnly: true
  volumes:
    # 你可以在 Pod 级别设置卷，然后将其挂载到 Pod 内的容器中
    - name: config
      configMap:
        # 提供你想要挂载的 ConfigMap 的名字
        name: game-demo
        # 来自 ConfigMap 的一组键，将被创建为文件
        items:
        - key: "game.properties"
          path: "game.properties"
        - key: "user-interface.properties"
          path: "user-interface.properties"
```

### secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
#Opaque				用户定义的任意数据
#kubernetes.io/service-account-token	服务账号令牌
#kubernetes.io/dockercfg		~/.dockercfg 文件的序列化形式
#kubernetes.io/dockerconfigjson	~/.docker/config.json 文件的序列化形式
#kubernetes.io/basic-auth		用于基本身份认证的凭据
#kubernetes.io/ssh-auth		用于 SSH 身份认证的凭据
#kubernetes.io/tls			用于 TLS 客户端或者服务器端的数据
#bootstrap.kubernetes.io/token	启动引导令牌数据
type: Opaque
data:
#必须经过base64加密   echo -n 'admin' | base64    >   YWRtaW4=
  username: YWRtaW4=
  password: MWYyZDFlMmU2N2Rm
```

### secret使用

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-demo-pod
spec:
  containers:
  - name: demo
    image: nginx 
  env:
  - name: USER
    valueFrom:
      secretKeyRef:
        name: db-user-pass 
        key: username
  - name: PASS 
    valueFrom:
      secretKeyRef:
        name: db-user-pass 
        key: password
    volumeMounts:
    - name: config
      mountPath: "/config"
      readOnly: true
  volumes:
  - name: config
    secret:
      secretName: db-user-pass 
      items:
      - key: username 
        path: my-username
```

### Role|ClusterRole|RoleBinding|ClusterRoleBinding

```yaml
#创建角色
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
#apiGroups 可以指定 kubectl api-versions 中的内容 如：apps
#resources 可以指定 kubectl api-resources 中的内容 如： deployments
#verbs 可以指定方法get、list、create、update、patch、watch、delete
---
#将角色和用户绑定
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: user_name
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 网络策略NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
#启用策略的pod
#podSelector: {}   代表所有POD
  podSelector:
    matchLabels:
      app: pod_name
#通过标签匹配pod
  policyTypes:
    - Ingress
    - Egress
#ingress入|egress出
  ingress:
    - from:
#根据ip地址172.17.0.0/16可以，但是172.17.1.0/24
        - ipBlock:
            cidr: 172.17.0.0/16
            except:
              - 172.17.1.0/24
#根据namespace标签决定，kubernetes.io/metadata.name: default可以
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: default
#根据pod标签podSelector: {}代表不允许
        - podSelector:
            matchLabels:
              role: frontend
#允许访问的端口及协议
      ports:
        - protocol: TCP
          port: 6379
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.0.0/24
      ports:
        - protocol: TCP
          port: 5978
```

