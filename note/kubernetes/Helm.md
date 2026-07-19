# Helm

## 一、Helm 概念及组件简介

Helm 是一个包管理工具，用于Helm Chart的创建、发布、安装、升级和卸载。

### 1. Chart

* Chart是一个Helm声明应用部署的单元,是Kubernetes资源清单文件的集合+Chart本身的元数据。
* Chart可以被安装到Kubernetes集群中(通过Chart运行的称作Release)
* Chart可以被推送到Chart仓库(Repository)中
* Chart可以被更新和卸载

### 2. Repository

* Repository是Chart的存储仓库，Chart被存储为Chart包，Chart包被存储为Chart仓库

### 3. Release

* Release是Chart在Kubernetes集群中的实例化

### 4. Helm Client

* Helm Client是Helm的命令行工具，用于Helm Chart的创建、发布、安装、升级和卸载

## 二、Helm 安装

1. HELM client 安装

```shell
wget https://get.helm.sh/helm-v3.21.0-linux-amd64.tar.gz -O helm-v3.21.0-linux-amd64.tar.gz
tar zxvf helm-v3.21.0-linux-amd64.tar.gz && mv linux-amd64/helm /usr/local/bin/helm
```

2. 建kubeconfig文件

3. 添加仓库地址

```shell
helm repo add aliyun https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm repo list # 验证是否成功

CHART_NAME=nginx
REPO_NAME=aliyun
helm search hub ${CHART_NAME} # 搜索官方仓库Chart
helm search repo ${REPO_NAME} # 搜索仓库
helm search repo ${CHART_NAME} # 搜索Chart 
helm pull repo ${CHART_NAME} # 下载一个chart

```

## 三、Helm 创建Chart

1. 创建Chart

```shell
helm create nginx # 创建Chart模板
APP_NAME=Nginx-123456
helm install ${APP_NAME} bitnami/nginx -n default # 从仓库安装Chart,并命名
     --generate-name # 随机生成Release名称,不需要${APP_NAME}了
```

2. 查看Chart列表

```shell
helm list -n default # 查看命名空间default下 Chart
helm show values bitnami/nginx # 查看Chart的可修改参数
helm show chart bitnami/nginx # 查看Chart的详细信息
helm show all bitnami/nginx # 查看Chart的所有信息
helm status nginx -n default # 查看Chart的状态
```
3. 卸载Chart

```shell
helm uninstall nginx -n default --keep-history # 卸载Chart(注意名称)
  --keep-history 保留历史记录
helm delete nginx -n default
```

4. 修改Chart参数

(1) 通过文本修改

1) 创建一个values.yaml文件

```yaml
services:
  type: NodePort
```

2) 安装Chart
```shell
APP_NAME=Nginx-123456
helm install -f values.yaml ${APP_NAME} bitnami/nginx -n default 
```

(2) 通过命令行修改

```shell
helm install nginx bitnami/nginx -n default \
    --set services.type=NodePort \
    --set image.tag=1.23.0 \
    --set ingress.enabled=true \
```

5. 更新部署Chart

```shell
helm upgrade --install csi-driver-nfs ./  --namespace csi-driver   --create-namespace   -f values.yaml --set feature.enableVolumeSnapshot=false
```