# Nginx

## 一、安装部署

## 二、基础配置

main

> events
> 
> stream(四层代理)
> 
> > upstream
> > 
> > server
> 
> http
> 
> > server
> > 
> > > location
> 
> > upstream(七层代理)
> 
> mail
> 
> > server

```nginx
user www-data; # 运行Nginx的用户
worker_processes auto; # 运行程序的进程数，配置和CPU个数保持一致
pid /run/nginx.pid; # pid文件位置
include /etc/nginx/modules-enabled/*.conf; # 包含的配置文件路径
worker_rlimit_nofile 51200; # 最大文件打开数（连接），可设置为系统优化后的ulimit -HSn的结果
events {
    use epoll; # epoll是多路复用IO(I/O Multiplexing)中的一种方式,但是仅用于linux2.6以上内核,可以大大提高nginx的性能
    worker_connections 768; #每个worker进程⽀支持的最⼤大连接数
    # multi_accept on;
}
http {
    # Basic Settings
        sendfile on; # 高效传输模式
        tcp_nopush on; # sendfile开启情况下, 提⾼高⽹网络包的'传输效率'
        tcp_nodelay on; # 在keepalive连接下,提⾼高⽹网络的传输'实时性'
        keepalive_timeout 65; # 连接超时时间
        types_hash_max_size 2048;
        # server_tokens off; # 隐藏响应header和错误通知中的版本号
        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;
        include /etc/nginx/mime.types; # 文件拓展名和类型映射表
        default_type application/octet-stream; # 默认的文件类型
    # 设定请求缓存
        server_names_hash_bucket_size 128;
        client_header_buffer_size 512k;
        large_client_header_buffers 4 512k;
        client_max_body_size 100m;
    #FastCGI相关参数：为了改善网站性能：减少资源占用，提高访问速度，一般配合PHP
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
        fastcgi_buffer_size 64k;
        fastcgi_buffers 4 64k;
        fastcgi_busy_buffers_size 128k;
        fastcgi_temp_file_write_size 128k;
    #开启ssi支持，默认是off
        ssi on;
        ssi_silent_errors on;
    # SSL Settings
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on; # 启动加密算法
    # Logging Settings
        log_format json '{'
            '"@timestamp": "$time_iso8601", '
            '"server_name": "$server_name"'
            '"remote_addr": "$remote_addr", '
            '"remote_user": "$remote_user", '
            '"status": "$status", '
            '"body_bytes_sent": "$body_bytes_sent", '
            '"request_time": "$request_time", '
            '"request": "$request", '
            '"request_uri": "$request_uri", '
            '"request_method": "$request_method", '
            '"http_referer": "$http_referer", '
            '"http_x_forwarded_for": "$http_x_forwarded_for", '
            '"upstream_status": "$upstream_status", '
            '"upstream_response_time": "$upstream_response_time", '
            '"http_user_agent": "$http_user_agent"'
        '}';
    # 在处理中文时，默认使用16进制编码处理 escape=json 可以取消这个设定
    access_log /var/log/nginx/access.log json;
    error_log /var/log/nginx/error.log debug; # 日志输出级别有debug、info、notice、warn、error、crit可供选择，其中，debug输出日志最为最详细，而crit输出日志最少。
    # charset settings
        charset utf-8;
    # Gzip Settings
        gzip on; # 开启压缩
        gzip_min_length 1K; # 至少为这个值才会进行压缩
        gzip_comp_level 9; # 压缩比率1-9，数值越高压缩比率越大
        # gzip_vary on; # #vary header支持。该选项可以让前端的缓存服务器缓存经过GZIP压缩的页面，
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k; # 压缩缓冲区大小，表示申请16个单位为8K的内存作为压缩结果流缓存
        # gzip_http_version 1.1; # 压缩的版本
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    ##
    # Virtual Host Configs
    ##

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

## 三、开启Nginx状态页

```nginx
location /status {
    stub_status on;
}
```

Active connections: Nginx当前活跃连接数

server表示Nginx处理理接收握⼿手总次数。

accepts表示Nginx处理理接收总连接数。

请求丢失数=(握⼿手数-连接数)可以看出,本次状态显示没有丢失请求。

handled requests，表示总共处理理了了19次请求。

Reading: Nginx读取数据

Writing: Nginx写的情况

Waiting: Nginx开启keep-alive⻓长连接情况下, 既没有读也没有写, 建⽴立连接情况

## 四、开启目录浏览

```nginx
location / {
    root html;
    autoindex on;
    autoindex_localtime on; #显示时间
    autoindex_exact_size off; # 关闭详细文件大小统计，让文件大小显示MB，GB单位，默认为b；
}
```

## 五、访问控制

```nginx
location ~ ^/1.html {
    root /usr/share/nginx/html;
    index index.html;
    deny 192.168.56.1;
    allow all;
}
```

## 六、虚拟主机

```nginx
server {
    listen 80 ;
    root /usr/share/nginx/html;
    server_name cloud.lxw.com;
}
```

## 七、静态资源压缩

| 配置                | 选项       | 作用                                                                                                              |
| ----------------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| sendfile          | on\|off  | 启用sendfile()系统调用来替换read()和write()调用，减少系统上下文切换从而提高性能，当 nginx 是静态文件服务器时，能极大提高nginx的性能表现，而当 nginx 是反向代理服务器时，则没什么用了 |
| tcp_nopush        | on\|off  | sendfile开启情况下, 提⾼高⽹网络包的'传输效率'                                                                                   |
| tcp_nodelay       | on\|off  | 在keepalive连接下,提⾼高⽹网络的传输'实时性'                                                                                    |
| gzip              | on\|off  | 压缩                                                                                                              |
| gzip_comp_level   | level    | 压缩比率1-9,   1最快，9压缩率最高                                                                                           |
| gzip_http_version | 1.0\|1.1 | 压缩使⽤http哪个协议, 主流版本1.1                                                                                           |
| gzip_static       | on\|off  | 预读gzip功能                                                                                                        |
| expires           | 1h\|7d   | 缓存过期时间，添加Cache-Control Expires头                                                                                 |
|                   |          |                                                                                                                 |

静态资源压缩

```nginx
location ~* \.(jpg|png|jpeg|gif|bmp|pdf|svg) {
    gzip on;
    gzip_http_version 1.1;
    gzip_comp_level 2;
    gzip_types text/plain application/json application/x-javascript application/css application/xml application/xml+rss text/javascript application/x-httpd-php image/jpeg image/gif image/png;
    root /images;
}
```

不使用缓存

```nginx
location ~ .*\.(css|js|swf|json|mp4|htm|html)$ {
    add_header Cache-Control no-store;
    add_header Pragma no-cache;
}
```

静态资源防盗链

```nginx
location ~* \.(jpg|png|jpeg|gif|bmp|pdf|svg) {
    valid_referers none blocked www.lxw.com; # 允许的域名
    if ($invalid_referer) {
        return 403;
}
```

## 八、跨域访问

```nginx
server {
    listen 80;
    server_name kt.xuliangwei.com;
    sendfile on;
    access_log /var/log/nginx/kuayue.log main;
    location ~ .*\.(html|htm)$ {
        add_header Access-Control-Allow-Origin http://www.xuliangwei.com;
        add_header Access-Control-Allow-Methods GET,POST,PUT,DELETE,OPTIONS;
        root /soft/code;
    }
}
```

## 九、代理

| 配置                         | 选项                                 | 功能                                                    |
| -------------------------- | ---------------------------------- | ----------------------------------------------------- |
| proxy_pass                 | URL                                | 代理URL                                                 |
| proxy_buffering            | on\|off                            | 是否打开缓冲区                                               |
| proxy_buffer_size          | 8k                                 | 响应头的缓冲区大小                                             |
| proxy_buffers              | number x size                      | 页面缓冲 4  8K                                            |
| proxy_busy_buffer_size     | 16k                                | 分配一部分缓冲区来用于向客户端发送数据，大小通常是proxy_buffers单位大小的两倍。官网默认是8k |
| proxy_redirect             | default\|off\|redirect replacement | 重写后端返回的URL                                            |
| proxy_set_header           | field value                        | 设置传送至后端的变量值                                           |
| proxy_hide_header          | field                              | 隐藏响应头中的某些信息                                           |
| proxy_set_body             | value                              | Nginx服务器接收到的客户端请求的请求体信息                               |
| proxy_connect_timeout time | time                               | 连接超时                                                  |
| proxy_read_timeout         | time                               | 已建立连接等待后端返回页面的时间(低有概率504)                             |
| proxy_send_timeout         | time                               | 发送请求给upstream服务器的超时时间                                 |
| proxy_max_temp_file_size   | 0                                  | 设置临时文件的总大小(0无限制)                                      |
| proxy_temp_file_wirte_size | 16K                                | 设置同时写入临时文件的数据量的总大小。通常设置为8k或者16k                       |
| proxy_method               | POST\|GET                          | 请求方法，会覆盖客户端的                                          |
| proxy_ignore_headers       | field                              | Nginx服务器接收到被代理服务器的响应数据后不会处理被设置的消息头                    |
|                            |                                    |                                                       |
|                            |                                    |                                                       |
|                            |                                    |                                                       |

proxy

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    include /etc/nginx/proxy_params;
}
```

proxy_params

```nginx
proxy_redirect default;
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_connect_timeout 30;
proxy_send_timeout 60;
proxy_read_timeout 60;
proxy_buffer_size 32k;
proxy_buffering on;
proxy_buffers 4 128k;
proxy_busy_buffers_size 256k;
proxy_max_temp_file_size 256k;
```

## 十、七层负载均衡

client-请求-->nginx-proxypass-->upstream-->backend

proxy

```nginx
server {
    location / {
        proxy_pass https://upstream_name;
    }
}
```

upstream (server同一级别)

```nginx
upstream upstream_name {
    #ip hash;
    #hash $request_uri;
    #least_conn;
    server www.lxw.com weight=5;
    server www.linxw.com weight=3;
    server www.lxwei.com down;
    server www.lxuewei.com backup;
    server www.linxuew.com max_fails=100 fail_timeout=10;
    server www.linxwei.com max_conns=1024;
    server unix:/tmp/backend;
}
```

| 调度策略       | 负载均衡依据             |
| ---------- | ------------------ |
| 轮询（默认）     | 默认1:1,通过weight设置权重 |
| ip hash    | client的IP          |
| urlhash    | 请求的url             |
| least_conn | 最少连接               |
| hash key   | 自定义的关键字            |
|            |                    |
|            |                    |
|            |                    |
|            |                    |

| 负载均衡状态配置     | 功能                 |
| ------------ | ------------------ |
| down         | 不启用                |
| backup       | 备用                 |
| max_conns    | 限制最大连接数            |
| max_fails    | 允许请求失败的次数          |
| fail_timeout | 经过max_fails后服务暂停时间 |
| weight       | 轮询权重               |
|              |                    |
|              |                    |
|              |                    |

## 十一、四层代理

```nginx
stream {
    upstream ssh_proxy {
        hash $remote_addr consistent;
        server 192.168.56.103:22;
    }
    upstream mysql_proxy {
        hash $remote_addr consistent;
        server 192.168.56.103:3306;
    }
    server {
        listen 6666;
        proxy_connect_timeout 1s;
        proxy_timeout 300s;
        proxy_pass ssh_proxy;
    }
    server {
        listen 5555;
        proxy_connect_timeout 1s;
        proxy_timeout 300s;
        proxy_pass mysql_proxy;
    }
}
# stream和server都得定义在main层
```

## 十五、动静分离

```nginx
upstream static {
    server 192.168.51.113:80;
}
upstream java {
    server 192.168.51.113:8080;
}
server {
    listen 80;
    server_name 150.158.93.164;
    location / {
        root /soft/code;
        index index.html;
    }
    location ~ .*\.(png|jpg|gif)$ {
        proxy_pass http://static;
        include proxy_params;
    }
    location  ~ .*\.jsp$ {
        proxy_pass  http://java;
        include proxy_params;
    }
}
```

## 十六、根据客户端选择后端服务器

```nginx
http {
    upstream firefox {
        server 172.31.57.133:80;
    }
    upstream chrome {
        server 172.31.57.133:8080;
    }
    upstream iphone {
        server 172.31.57.134:8080;
    }
    upstream android {
        server 172.31.57.134:8081;
    }
    upstream default {
        server 172.31.57.134:80;
    }
...
}
//server根据判断来访问不同的⻚⾯
server {
    listen       80;
    server_name  www.xuliangwei.com;
    #safari浏览器访问的效果
    location / {
        if ($http_user_agent ~* "Safari"){
        proxy_pass http://dynamic_pools;
        }     
    #firefox浏览器访问效果
        if ($http_user_agent ~* "Firefox"){
        proxy_pass http://static_pools;
        }
    #chrome浏览器访问效果
        if ($http_user_agent ~* "Chrome"){
        proxy_pass http://chrome;
        } 
    #iphone⼿机访问效果
        if ($http_user_agent ~* "iphone"){
        proxy_pass http://iphone;
        }
    #android⼿机访问效果
        if ($http_user_agent ~* "android"){
        proxy_pass http://and;
        }
    #其他浏览器访问默认规则
        proxy_pass http://dynamic_pools;
        include proxy.conf;
        }
    }
}
```

## 十七、浏览器缓存

1.expires

```nginx
expires [time|epoch|max|pff]
```

例

```nginx
expires 30d;
expires 31 December2022 23:59:59GMT;
```

2.通过cache-control 缓存控制 HTTP头部信息

```nginx
location ~* ^.+\.(css|js|txt|xml|swf|wav)$ {
    add_header Cache-Control no-store; # no-store不保留副本
    add_header Cache-Control max-age=3600; # max-age最长时间类似expires,expires基于文件创建时间，max-age基于访问时间
    # add_header Cache-Control public; # 必须缓存此资源
    add_header Cache-Control only-if-cached; # 告知代理服务器客户端希望获取缓存的内容，若有，则不用向原服务器发去请求
    # add_header Cache-Control no-cache; # 不直接缓存，要求发起服务器新鲜度请求
    # add_header Cache-Control must-revalidate; # 当前资源一定向源服务器发送验证请求，请求失败会返回504（而非代理服务器上的缓存）
}
```

Cache-Control

| 请求中使用Cache-Control        | 含义                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------- |
| no-store                  | 不保留副本                                                                                 |
| no-cache                  | 告知代理服务器不使用缓存，要求发起服务器新鲜度请求                                                             |
| no-transform              | 告知代理服务器希望获取实体数据没有被转换过的资源                                                              |
| only-if-cached            | 告知代理服务器客户端希望获取缓存的内容，若有，则不用向原服务器发去请求                                                   |
| min-fresh=delta-seconds   | 告知代理服务器                                                                               |
| max-stale[=delta-seconds] | 告知代理服务器表示接受超过缓存时间的资源                                                                  |
| max-age=delta-seconds     | max-age最长时间类似expires,expires基于文件创建时间，max-age基于访问时间(s)，告知代理服务器，希望接收一个存在时间不大于max-age的资源 |

| 响应中使用Cache-Control 时   | 含义                                                                              |
| ---------------------- | ------------------------------------------------------------------------------- |
| public                 | 必须缓存此资源                                                                         |
| Private[="field-name"] | 表明报文中的全部或部分仅开放给某些用户作缓存使用，其他用户不缓存                                                |
| no-cache               | 不直接缓存，要求发起服务器新鲜度请求                                                              |
| no-store               | 不保留副本                                                                           |
| no-transform           | 告知代理服务器不得对实体数据做任何改变                                                             |
| only-if-cached         | 告知代理服务器客户端希望获取缓存的内容，若有，则不用向原服务器发去请求                                             |
| must-revalidate        | 当前资源一定向源服务器发送验证请求，请求失败会返回504（而非代理服务器上的缓存）                                       |
| proxy-revalidate       | 类似must-revalidate，但仅能应用于共享缓存（如代理）                                               |
| max-age=delta-seconds  | max-age最长时间类似expires,expires基于文件创建时间，max-age基于访问时间(s)，告知在delta-seconds内，此资源是新鲜的 |
| s-maxage=delta-seconds | 类似max-age，但仅能应用于共享缓存（如代理）                                                       |

3.Last-modified/If-Modified-Since

If-Modified-Since(请求头)

​    告诉服务端本地缓存的上次的最后修改时间，如果服务端判定没有改变，则返回304，重定向到本地缓存

If-Unmodified-Since(请求头)

​    告诉服务器如果时间不一致，返回状态码412

Last-modified (响应头)

​    告知文件最后修改日期

4.ETag/If-None-Match

If-None-Match(请求头)

​    发送hash值，匹配则返回304

If-Match(请求头)

​    告诉服务器如果不一致，返回状态码412

etag(响应头)

​    服务器通过某个算法对资源进行计算，取得一串值(类似于文件的md5值)

## 十八、Nginx缓存

语法

​    proxy_cache_path path [levels=levels] keys_zone=name:size [inactive=time] [max_size=size] [loader_files=number] [loader_sleep=time] [loader_threshold=time];

配置于HTTP段

| 缓存配置proxy_cache_path | 选项           | 含义                                                                                                                    |
| -------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| path                 | /nginx/cache | 缓存的路径                                                                                                                 |
| levels               | levels       | 层级1:2:3相当于第三层级有16^1\*16^2\*16^3个文件夹                                                                                   |
| keys_zone            | mycache:10m  | 指定一个共享内存空间zone(自定义名称),存KEY不存value，用来快速定位的                                                                             |
| inactive             | time         | inactive=30m,三十分以内没有被访问的文件，会被删除                                                                                       |
| max_size             | cache        | max_size=200m,存储的最大尺寸200M，如果不指定，会用掉所有磁盘空间，当尺寸超过，将会基于LRU算法移除数据，以减少占用大小。nginx启动时，会创建一个“Cache manager”进程，通过“purge”方式移除数据 |
| loader_files         | 200          | “cache loader”进程遍历文件时，每次加载的文件个数。默认为100                                                                                |
| loader_threshold     | 300          | 每次遍历消耗时间上限。默认为200毫秒。                                                                                                  |
| loader_sleep         | 100          | 一次遍历之后，停顿的时间间隔，默认为50毫秒。                                                                                               |
| use_temp_path        | off          | 关闭临时路径                                                                                                                |

| 其他缓存配置               | 选项              | 含义                                                       |
| -------------------- | --------------- | -------------------------------------------------------- |
| proxy_cache          | zone\|off       | 是否开启缓存，覆盖上层                                              |
| proxy_cache_valid    | [code ...] time | 为不同的响应状态码设置不同的缓存时间                                       |
| proxy_cache_key      | string          | 默认值:     proxy_cache_key $scheme$proxy_host$request_uri; |
| proxy_cache_min_uses | 1               | 当客户端发送相同请求达到规定次数后，nginx才对响应数据进行缓存                        |
| proxy_cache_bypass   | string          | 定义nginx不从缓存取响应的条件。如果至少一个字符串条件非空而且非“0”，nginx就不会从缓存中去取响应   |
| proxy_no_cache       | string          | 定义nginx不将响应写入缓存的条件                                       |

例

```nginx
http {
    # ...
    upstream cache_servers {
        server 192.168.69.111:8081;
        server 192.168.69.112:8082;
        server 192.168.69.113:8083;
    }
    upstream backend_servers {
        server 192.168.69.114:8081;
        server 192.168.69.115:8082;
        server 192.168.69.116:8083;
    }
    proxy_cache_path /data/nginx/cache keys_zone=mycache:10m loader_threshold=300
                     loader_files=200 max_size=200m use_temp_path=off;
    server {
        listen 8080;
        proxy_cache mycache; #对应key_zone
        location / {
            proxy_pass http://backend_servers;
        }
        location /some/path {
            proxy_pass http://cache_servers;
            proxy_cache_valid 200 304 12h;
            proxy_cache_valid any 20m;
            proxy_cache_min_uses 3;
            proxy_cache_bypass $cookie_nocache $arg_nocache $arg_comment;
            proxy_no_cache $http_pargma $http_authorization;
            add_header Nginx-Cache "$upstream_cache_status"; #可以查看缓存的状态
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504; #出现500/502/503/504 跳转到下一个后端
        }
    }
}
```

## 十九、rewrite

语法

rewrite regex replacement [flag];

| flag      | 含义                               |
| --------- | -------------------------------- |
| last      | rewrite之后，继续匹配location           |
| break     | 停止rewrite检测 不会进行匹配，会查找对应root站点目录 |
| redirect  | 返回302，显示跳转后的地址（下一次会再请求）          |
| permanent | 返回301，显示跳转后的地址（缓存记录跳转的位置）        |

## 二十、HTTPS

```nginx
http {
    server {
        listen       443 ssl;
        #绑定好域名
        server_name  www.lxw.com;
        #指定证书相关位置
        ssl_certificate      /usr/local/nginx/conf/cert/server.crt; #公钥
        ssl_certificate_key  /usr/local/nginx/conf/cert/server.key; #私钥
        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m; # session超时时间
        ssl_ciphers  HIGH:!aNULL:!MD5; # 加密算法
        ssl_prefer_server_ciphers  on; # 启动加密算法
        location / {
            root   html;
            index  index.html index.htm;
        }
    }
#http跳转到https
    server {
        listen 80；
        server_name www2.lxw.com;
        rewrite / https://150.158.93.164:443 permanent;
    }
}
```

## 二十一、location

=  精确匹配

```nginx
#  =  精确匹配
location = / {
    #规则
}

#  ~  正则 区分大小写
location ~ /.*\.html$ {
    #规则
}

#  ~*  正则 不区分大小写
location  ~* /.*\.html$ {
    #规则
}

#  ^~  以X开头的 正则
location  ^~ /abc {
    #规则
}

#  剩下不匹配的
location / {
   #规则
}

location /down {
    root /soft/down;
}    
一定要有个down文件夹

location /down/ {
    root /soft/up;
}    
不需要down文件夹

#匹配跳转从一个location跳转到另一个location
location /img/ {
    #如果状态码是404  就指定404的页面为什么
    error_page 404 = @img_err;
}    

location @img_err {    
    # 规则
    return  503；
}
```
