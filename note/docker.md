# docker

## 一、docker使用

```shell
docker info
    查看信息
docker ps
    查看运行状态
    -a 所有
    -q 显示ID
docker run -d -p 8080:80 nginx
docker container run -d -p 8080:80 nginx
    run 运行容器
    -d 后台运行
    -i 交互
    -t 分配一个伪终端
    -e 设置环境变量
    -p nat宿主机端口:容器端口
    -P 发布所有容器端口到主机端口
    --name 指定容器名称
    -v /opt/wwwroot:/usr/share/nginx/html 挂载宿主机:容器 持久化
    -h 指定容器主机名
    --ip 指定容器IP 只能用于自定义网络
    --network 连接容器到一个网络
    -v 将文件系统附加到容器
    --restart no|always|on-failure 容器退出时的重启策略
    -m="500m" 设置内存
    -memory-swap 允许交换到磁盘的内存量
    –memory-swappiness=<0-100> 容器使用SWAP分区交换的百分比（0-100，默认为-1）
    --cpus="2" 设置CPU
    –cpuset-cpus 限制容器使用特定的CPU核心，如(0-3, 0,1)
    –cpu-shares CPU共享（相对权重）
docker history nginx
    build的历史
docker pull nginx
    下载镜像
docker push nginx
    推送镜像
docker image rm hello-world:latest
    删除镜像
docker image prune -a
    删除没有使用的镜像
    -a 没有在容器使用中的镜像
docker image tag
    标签
docker image save -o
    保存镜像到指定位置
docker image load -i
    导入镜像从指定位置
```

## 二、docker管理命令

```shell
docker top cbb649424924
    查看进程
docker exec -it cbb649424924 bash
    进入运行中的容器
docker exec cbb649424924 ls
    对容器运行ls指令
docker inspect nginx
    输出详细信息
docker container ls -a
    列出所有容器
    -a 列出所有
docker container start/stop 3df3ab517bbd
    启动停止容器（可以使用ID或名称）
docker container rm 3df3ab517bbd
    删除容器
docker container prune
    移除已停止容器
docker rm -f $(docker ps -qa)
    删除所有（包括运行中的）容器
docker commit cf1b8cac5454 image_name 
    创建一个新镜像来自一个容器
docker cp ./a.txt web:/
    复制文件
docker logs cbb649424924
    获取一个容器日志
docker port cbb649424924
    列出或指定容器端口映射
docker container stats cbb649424924 --no-stream
    显示容器资源使用统计
    --no-stream 只显示一次
```

docker远程管理

/usr/lib/systemd/system/docker.service

```shell
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H fd:// --containerd=/run/containerd/containerd.sock
systemctl daemon-reload && systemctl restart docker
```

## 三、dockerfile

创建一个目录，用于存储Dockerﬁle所使用的文件

在此目录中创建Dockerﬁle文件及制作镜像所使用到的文件

在此此目录中使用docker build创建镜像(读取Dockerﬁle文件)

使用创建的镜像启动容器

### 创建的命令

```shell
docker build -t image_name -f Dockerfile_name path|url|-[flags]
    -t 指定镜像名称
    -f 指定dockerfile文件名
```

### dokcerfile编写

```shell
dockerfile指令
FROM centos/systemd
    指定来源镜像
RUN yum install epel-release -y && \
    yum install nginx -y
    运行的命令
CMD ["nginx", "-g", "daemon off;"]
    运行容器时默认执行。如果有多个CMD，最后一个生效
LABEL
    标签
COPY
    复制文件到镜像
ADD nginx-1.15.5.tar.gz
    解压压缩包并复制
ENV PATH $PATH:/usr/local/nginx/sbin
    设置环境变量
USER
    为RUN、CMD、ENTPYPOINT执行指定用户
EXPOSE 80
    声明容器运行的服务端口
WORKDIR /usr/local/nginx
    为RUN、CMD、ENTPYPOINT、COPY和ADD设置工作目录
```

### 案例: dockerfile部署tomcat

1.

```shell
mkdir -p /dockerfile/tomcat
cp ${tomcat_path}/apache-tomcat-${version}.tar.gz ./
```

2.Dockerfile

```shell
FROM centos/systemd
MAINTAINER www.lxw.com
ENV VERSION=10.0.20
RUN yum install java-1.8.0-openjdk wget curl unzip iproute net-tools -y && \
yum clean all && \
rm -rf /var/cache/yum/*
ADD apache-tomcat-${VERSION}.tar.gz /usr/local/
RUN mv /usr/local/apache-tomcat-${VERSION} /usr/local/tomcat && \
sed -i '1a JAVA_OPTS="-Djava.security.egd=file:/dev/./urandom"' /usr/local/tomcat/bin/catalina.sh && \
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV PATH $PATH:/usr/local/tomcat/bin
WORKDIR /usr/local/tomcat
EXPOSE 8080
CMD ["catalina.sh", "run"]
```

3.

```shell
docker build -t tomcat:10.0.20 .
docker run -d -p 80:8080 tomcat:10.0.20
```

## 四、habor镜像仓库

1.先安装Docker和Docker Compose

```shell
chmod +x docker-compose
```

2.安装harbor http

```shell
tar zxvf harbor-offline-installer-v2.0.0.tgz
cd harbor
cp harbor.yml.tmpl harbor.yml
```

harbor.yml

```yaml
    hostname: reg.ctnrs.com
    https: # 先注释https相关配置
    harbor_admin_password: Harbor12345
```

```shell
./prepare
./install.sh
```

3.配置站点可信
/etc/docker/daemon.json

```json
{
    "insecure-registries": ["192.168.51.58:80"]
}
```

4.

```shell
docker tag tomcat:10.0.20 192.168.51.58:80/library/my_tomcat:10.0.20
docker login 192.168.51.58:80
docker push 192.168.51.58:80/library/my_tomcat:10.0.20
```

## 五、不同docker之间的通信

### 自定义网络

1.自定义网桥

```shell
docker network create --driver bridge virt_bridge01       #virt_bridge01是名字
docker network create --driver bridge  --subnet "10.3.3.0/24" --gateway "10.3.3.254" virt_bridge02
docker network create --driver overlay --subnet 192.168.100.0/24 virt_bridge03
```

2.连接到相同网络

```shell
docker run -it --network=virt_bridge01 --name=tomcat1 tomcat
docker run -it --network=virt_bridge01 --name=tomcat2 tomcat
```

3.测试

```shell
docker exec -it tomcat1 bash
ping tomcat2 
```

### 共享主机网络

```shell
docker network create -d host host0
```

### 共享网卡

1.创建容器web1

```shell
docker run -d -it --name=web1 httpd
```

2.创建依赖与web1的容器

```shell
docker run -d -it --network=container:web1 --name=php php
```

共享同一网络信息

## 六、docker swarm

### 部署

```shell
docker swarm init 
option:
    --advertise-addr 定义发布地址 IP|ifname
    --listen-addr 指出的是这个集群暴露给外界调用的HTTP API的socket地址 IP:PORT
    --data-path-addr是 数据传输的地址 IP|ifname
```

例

```shell
docker swarm init --advertise-addr 192.168.51.50:2377 --data-path-addr ens37 
docker swarm join-token manager # 查看添加进swarm manger集群的token
docker swarm join-token worker # 查看添加进swarm worker集群的token
docker node ls  # 验证已加入的节点
```

### 使用

```shell
docker service create --replicas 2 --publish 8090:80 --network virt_bridge --name nginxsvc nginx
--replicas 2  创建2个容器
--publish 8090:80  端口转换
--network 指定网络
--mount "type=bind,source=$PWD,target=/var/lib/registry" 挂载目录，实现持久化
docker service ls 
docker service scale nginxsvc=3 扩展或缩小容器数量
docker service update --image 192.168.122.100/library/centos-nginx:v2 nginxsvc  更新服务
docker service update --replicas 3 --image 192.168.122.100/library/centos-nginx:v2 --update-parallelism 1 --update-delay 30s nginxsvc  滚动更新
```

## 七、docker stack

通过yaml多service部署

### 编写docker-compose.yaml

```yaml
version: "3"
services:
  nginx:
    image: nginx:alpine
    ports:
      - 80:80
    deploy:
      mode: replicated
      replicas: 4
  visualizer:
    image: dockersamples/visualizer
    ports:
      - "9001:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
    deploy:
      replicas: 1
      placement:
        constraints: [node.role == manager]
  portainer:
    image: portainer/portainer
    ports:
    - "9000:9000"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
    deploy:
      replicas: 1
      placement:
        constraints: [node.role == manager]
```

### 部署应用

```shell
docker stack deploy -c docker-compose.yaml services_name #运行这个docker stack项目
docker stack ls #查看
```

### 案例: mysql-yaml编写

```yaml
services: 
  mysql: 
    image: mysql:5.7.35
    volumes: 
      - /mysqldata/data:/var/lib/mysql
      - /etc/localtime:/etc/localtime:ro
    restart: always
    environment:
      TZ: Asia/Shanghai
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: test_01
      MYSQL_USER: lxw
      MYSQL_PASSWORD: 123456
      MYSQL_ROOT_HOST: "%"
    command: 
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_general_ci
      --transaction_isolation=READ-COMMITTED
    ports: 
      - 3306:3306
    networks: 
      - mysqlnet
networks: 
  mysqlnet: 
    driver: bridge
```



### 案例: KMS容器

```shell
git clone https://github.com/Wind4/vlmcsd-docker.git vlmcsd
cd vlmcsd
docker-compose up -d
```

windows上激活

```powershell
cd /d "%SystemRoot%\system32" 
slmgr /skms 192.168.19.201 #设置KMS服务器地址
slmgr /ato # 激活
slmgr /xpr # #查看激活时间
```
