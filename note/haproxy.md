# HAProxy

```shell
global # 全局配置区
    maxconn 20000 # 最大连接数
    ulimit-n 16384
    log 127.0.0.1 local0 info
    uid 200
    gid 200
    chroot /var/empty # 工作目录
    nbproc 2 # 启动时可创建的进程数，要先设置为daemon模式
    daemon
    pidfile /var/log/haproxy.pid

defaults # 默认会被自动引用到frontend、backend、listen(相同配置会被frontend、backend、listen的设置覆盖)
    mode http # tcp四层、http七层、health基本废弃
    log global # 设置日志参照全局的设置
    option httplog # 详细记录http日志
    option dontlognull # 不记录空日志
    retries 3 # 连接后端的失败重试次数
    timeout connect 10s # 设置客户端请求转发至后端服务器的最长等待时间
    timeout client 20s # 连接客户端发送数据最长等待时间
    timeout server 30s # 客户端和服务端建立连接后，服务端回应客户端数据发送的最长等待时间
    timeout check 5s # 设置后端服务器的检测超时时间
    timeout http-keep-alive 10s # 持久连接超时时间
    timeout queue 1m # 队列超时时间
    timeout http-request 10s # http请求超时时间

frontend frontend_name # 前端
    bind 192.168.1.107:8443 # 绑定的ip地址，ip地址可以是*
    mode http
    option forwardfor # 转发客户端真实ip
    option httpclose # 客户端和服务器完成一次连接请求后，HAProxy主动关闭TCP连接请求
    maxconn 8000
    timeout client 30s
    default_backend backend_name # 定义后端

backend backend_name # 后端
    mode http
    option redispatch # 重新分发，ServerID对应的服务器宕机后，强制定向到其他运行正常的服务器
    option abortonclose # 服务器高负载情况下，会自动结束掉队列中处理时间比较长的链接
    option httpchk $method $uri $version # 表示启用健康检查method通常为HEAD,VERSION指HTTP版本号
    option httpchk GET /index.html
    balance roundrobin # 负载均衡算法
    cookie SERVERID # 允许向cookie插入SERVERID,每台的SERVERID可在下面的server关键字中使用cookie关键字定义
    server $name ${ip_addr}:${port} $param # 定义后端服务器param通常有check(代表检查)、inter(健康检查间隔时间)、rise(从故障转健康需要的次数)、fall(从健康转故障需要检查的次数)
    server web1 192.168.1.107:6443 cookie server1 weight 6 check inter 2000 rise 2 fall 3
    
listen admin_stats # dashboard
    bind *:9188
    mode http
    log 127.0.0.1 local0 err
    stats refresh 30s
    stats uri /haproxy-status
    stats realm welcome login\ HAProxy
    stats auth admin:admin~!@
    stats hide-version
    stats admin if TRUE # 可以在页面面上启用或禁用后端
```

负载均衡算法

```shell
roundrobin # 轮询
static-rr # 基于权重轮询
source # 基于源IP地址
leastconn # 基于后端最少连接
uri # 基于请求的uri
uri_param # 基于请求uri路径中的参数，可以保证在后端真实服务器数量不变时，同一个用户请求始终分发到同一台机器上
hdr # 根据http头进行转发
rdp-cookie # 基于cookie来锁定并hash每一次TCP请求
```

