# secret

## 一、加密算法

### 对称加密

加密、解密都使用相同的密钥进行

### 非对称加密

加密、解密都使用不相同的密钥进行，一个公钥，一个私钥

公钥加密的内容，可以用私钥解密

私钥加密的内容，可以用公钥解密

RSA运用最广泛

### 哈希算法

单向，只能加密不能解密

信息转为HASH值，但不能通过HASH找回原本的信息

## 二、数字证书

证明公钥生成者的身份

## 三、cfssl使用

安装

```shell
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl_1.5.0_linux_amd64 -o /bin/cfssl
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssljson_1.5.0_linux_amd64 -o /bin/cfssljson
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.5.0/cfssl-certinfo_1.5.0_linux_amd64 -o /bin/cfssl-certin
chmod +x /bin/cfssl
chmod +x /bin/cfssljson
chmod +x /bin/cfssl-certinfo
```

生成默认配置模板

```shell
/bin/cfssl print-defaults config > config.json # 默认配置模板
/bin/cfssl print-defaults csr > csr.json # 默认csr请求模板
```

config.json

```json
{
    "signing": {
        "default": {
            "expiry": "168h"
        },
        "profiles": {
            "www": {
                "expiry": "8760h",
                "usages": [
                    "signing",
                    "key encipherment",
                    "server auth"
                ]
            },
            "client": {
                "expiry": "8760h",
                "usages": [
                    "signing",
                    "key encipherment",
                    "client auth"
                ]
            }
        }
    }
}
```

csr.json

```shell
{
    "CN": "example.net",
    "hosts": [
        "example.net",
        "www.example.net"
   ],
    "key": {
        "algo": "ecdsa",
        "size": 256
    },
    "names": [
        {
            "C": "US",
            "ST": "CA",
            "L": "San Francisco"
        }
    ]
}

# CN: Common Name，浏览器使用该字段验证网站是否合法，一般写的是域名。非常重要。k8s中用来定义用户名
# key：生成证书的算法
# hosts：表示哪些主机名(域名)或者IP可以使用此csr申请的证书，可以多个域名使用一个CA证书，为空或者""表示所有的都可以使用
# names：一些其它的属性
# C: Country， 国家
# ST: State，州或者是省份
# L: Locality Name，地区，城市
# O: Organization Name，组织名称，公司名称(在k8s中常用于指定Group，进行RBAC绑定)
# OU: Organization Unit Name，组织单位名称，公司部门
```

ca根证书创建

```shell
cfssl gencert -initca csr.json | cfssljson -bare ca # 创建以ca为开头的根证书
```

查看生成的证书信息

```shell
cfssl certinfo -cert ca.pem   # 查看证书信息
cfssl certinfo -csr ca.csr   # 查看CSR证书签名请求信息
```

生成子证书(以ETCD为例)

etcd-csr.json

```json
{
  "CN": "etcd",
  "key": {
    "algo": "rsa",
    "size": 2048
  }
  "names": [
    {
      "C": "CN",
      "ST": "Beijing",
      "L": "Beijing",
      "O": "DC",
      "OU": "System"
    }
  ]
}
```

签发子证书

```shell
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes etcd-csr.json | cfssljson -bare 
# -profile指定采用ca-config.json中定义的profiles字段
```
