# shadowsocks-libev

## 一、服务端安装

### 1. Ubuntu20.04安装

```
apt install shadowsocks-libev -y
```

### 2. 配置文件修改

```/etc/shadowsocks-libev/config.json
{
    "server": "0.0.0.0",
    "mode":"tcp_and_udp",
    "server_port":8388,
    "password":"123456",
    "timeout":300,
    "method":"chacha20-ietf-poly1305"
}
```

## 二、本地客户端下载

### 1.链接

```
https://raw.githubusercontent.com/ShadowsocksHelp/Shadowsocks/master/Download/Shadowsocks-4.1.7.1.zip
```

### 2.验证

```
curl --socks5 127.0.0.1:1080 http://ipinfo.io
```

得到的是服务端所在IP即成功