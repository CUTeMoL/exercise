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

### 案例: python调用

```python
#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import docker
import docker.types
import optparse
import json
import re
import os
import platform
import logging
import traceback
import subprocess
import socket
from logging.handlers import TimedRotatingFileHandler

class InvalidResponse(Exception):
    def __init__(self, param):
        self.code = param['code']
        self.message = param['message']
        self.data = param.get('data', None)

def error_format(error_raw):
    return "{0};\r{1}".format(repr(error_raw), traceback.format_exc().replace("\n", ";\t"))

# 更新异常信息
def update_message(func):
    """
    logger增加一列脚本名
    :param func:
    :return:
    """

    def wrapper(self, msg, *args):
        if self.name != "":
            msg = "{0}: {1}".format(self.name, msg)
        return func(self, msg, *args)

    return wrapper

# 执行外部命令类
class ExternalCmd(object):
    def __init__(self, loggger, passwd_list=None):
        self.logger = loggger
        self.passwd_list = []
        if passwd_list is not None:
            self.passwd_list = passwd_list

    def execute_cmd(self, cmd, need_record=True):
        """
        执行命令的方法
        :param cmd: string
        :param need_record: bool
        :return: int, string
        """
        if need_record is True:
            # 脱敏处理
            desensitization_cmd = cmd
            for key_line in self.passwd_list:
                desensitization_cmd = desensitization_cmd.replace(key_line, "xxxxxxxxxxxxxx")
            if platform.uname()[0] == "Windows":
                desensitization_cmd = desensitization_cmd.decode("cp936").encode("utf-8")
            self.logger.info("execute_cmd: {0}".format(desensitization_cmd))
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        if need_record is True:
            stdout = stdout.replace("\r\n", "\n")
            stderr = stderr.replace("\r\n", "\n")
            if platform.uname()[0] == "Windows":
                stdout = stdout.decode("cp936").encode("utf-8")
                stderr = stderr.decode("cp936").encode("utf-8")
            self.logger.info("exec finish\n{3}\nreturn_code:{0}\nstdout: {1}\nstderr: {2}\n{3}".format(
                p.returncode, stdout, stderr, "=" * 30)
            )
        if p.returncode != 0:
            return p.returncode, stderr
        return p.returncode, stdout


# 日志类
class GameLogger(object):
    def __init__(self, file_path, level, interval, backup_count,
                 fmt="[%(asctime)s] [%(process)d] [%(levelname)s] - %(message)s", script_name="", need_stdout=False):
        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            try:
                os.makedirs(file_dir)
            except Exception as err:
                err_msg = "{0};\r{1}".format(repr(err), traceback.format_exc().replace("\n", ""))
                raise SystemExit("Create log dir failed, {0}".format(err_msg))
        self.name = script_name
        self.logger = logging.getLogger(file_path)
        # 增加该脚本屏幕日志输出
        stream_handler = logging.StreamHandler()
        if level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        file_handler = TimedRotatingFileHandler(
            filename=file_path, when="MIDNIGHT", interval=interval, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.suffix = "%Y-%m-%d.old"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.old$")
        file_handler.setFormatter(
            logging.Formatter(fmt)
        )
        if need_stdout is True:
            # 设置屏幕输出格式
            stream_handler.setFormatter(
                logging.Formatter("[%(asctime)s] [%(process)d] [%(levelname)s] - %(message)s")
            )
            # 增加句柄
            self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    @update_message
    def error(self, msg):
        self.logger.error(msg)

    @update_message
    def info(self, msg):
        self.logger.info(msg)

    @update_message
    def debug(self, msg):
        self.logger.debug(msg)

    @update_message
    def warning(self, msg):
        self.logger.warning(msg)

    @update_message
    def critical(self, msg):
        self.logger.critical(msg)

def check_port(port):
    '''
    端口检查,0通,10035不通,用于检查进程是否停止
    '''
    telnet_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    telnet_object.settimeout(1)
    result = telnet_object.connect_ex(("localhost", int(port)))
    telnet_object.close()
    return True if result == 0 else False


# 工作目录: 配置文件存在这
WORK_PATH = "/ndgame/restore_db"
if not os.path.exists(WORK_PATH):
    os.makedirs(WORK_PATH)

# 定义日志
generallog_path = os.path.join(WORK_PATH, "logs","general.log")
general_logger = GameLogger(generallog_path, "info", 1, 30, script_name=os.path.basename(__file__), need_stdout=True)


def docker_create(taskID, project, simpleID, date, stoptime=None):
    '''
    功能:
        创建一个docker实例
    参数:
        taskID: 蓝鲸默认带有的全局变量,主日志general_logger标注任务用
        project: 用来决定路径,从文件中读取数据库名和维护时间
        simpleID: 用来决定路径
        date: 用来决定路径
        stoptime: 用来决定路径
    '''
    try:
        # 如果不存在stoptime那么stoptime等于None
        if stoptime == "" and stoptime == None:
            stoptime = None

        # 读取数据库恢复使用的的根路径
        with open(os.path.join(WORK_PATH, "conf", "restore_db.json"), "r") as restore_conf:
            restore_config = json.load(restore_conf)
            restore_path = restore_config["path"]
            restore_port_range = restore_config["port_range"]
        # 读取维护时间
        with open(os.path.join(WORK_PATH, "conf", "projectinfo.json"), "r") as project_conf:
            project_info = json.load(project_conf)[project]
            maintenance_time = project_info["Maintenance_time"]
            mysql_version = project_info["mysqlversion"]

        # 终点时间定义:如果存在stoptime参数则使用stoptime,不存在则使用维护时间
        endtime = stoptime if stoptime else maintenance_time

        # 当前任务的存储路径: "/ndgame/restore_db/项目名/simpleID_日期_终点时间"
        store_path = os.path.join(restore_path, project, "{}_{}_{}".format(simpleID, date.replace("-", ""), endtime.replace(":", "")))
        # 当前任务的datadir
        datadir = os.path.join(store_path, "data")
        # 创建docker的客户端
        docker_socket = docker.from_env()
        # 创建挂载关系
        mountpoint = docker.types.Mount("/usr/local/mysql/data", datadir, "bind")
        # 选择端口
        port_start, port_end = restore_port_range.split("-")
        for port in range(int(port_start), int(port_end)+1):
            result = check_port(port)
            # 如果端口不通,则选择这个端口启动
            if not result:
                mysql_port = port
                general_logger.info("[%s] restore use port: %s"%(taskID, mysql_port))
                break
        if not mysql_port:
            general_logger.error("[%s] No ports available"%(taskID))
            raise InvalidResponse({'code': 1, 'message': "No ports available"})
        # 创建容器
        if mysql_version == "4.0":
            container = docker_socket.containers.run(
                "mysql:4.0.27",
                detach=True,
                mounts=[mountpoint, ],
                restart_policy={"Name": "always"},
                ports={"3306/tcp": mysql_port},
                labels={"project": project, "simpleID": simpleID, "date": date, "time": endtime}
            )
        elif mysql_version == "5.6":
            container = docker_socket.containers.run(
                "mysql:5.6.21",
                detach=True,
                mounts=[mountpoint, ],
                restart_policy={"Name": "always"},
                ports={"3306/tcp": mysql_port},
                labels={"project": project, "simpleID": simpleID, "date": date, "time": endtime}
            )
        container_id = container.attrs["Id"]
        general_logger.info("[%s] Create container %s, project: %s simpleID: %s datetime: '%s %s'" %(taskID, container_id, project, simpleID, date, endtime))

        return True
    
    except InvalidResponse as err:
        raise err
    except Exception as err:
        raise InvalidResponse({'code': 1, 'message': "script crash, reason: {0}".format(error_format(err))})

if __name__ == "__main__":
    Parser = optparse.OptionParser()
    Parser.add_option("--project", dest="project")
    Parser.add_option("--simpleID", dest="simpleID")
    Parser.add_option("--date", dest="date")
    Parser.add_option("--taskID", dest="taskID")
    Parser.add_option("--stoptime", dest="stoptime")
    (opt, args) = Parser.parse_args()
    docker_create(
        getattr(opt, "taskID"),
        getattr(opt, "project"),
        getattr(opt, "simpleID"),
        getattr(opt, "date"),
        getattr(opt, "stoptime")
    )

```