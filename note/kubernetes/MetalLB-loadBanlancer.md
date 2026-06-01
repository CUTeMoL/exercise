
# MEtalLB

## 一、安装

```shell
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.3/config/manifests/metallb-native.yaml
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

```

## 二、创建一个 IPAddressPool(可以使用节点同段为使用IP)

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: lan-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.120-192.168.1.130 # 空闲IP写进来
  serviceAllocation:
    priority: 10
    namespace: kube-system
    serviceSelectors:
    - matchLabels:
        app.kubernetes.io/name: coredns   # 匹配标签自动用这个IP池
---
# L2Advertisement
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: lan-pool-l2-adv
  namespace: metallb-system
```

## 三、使用


1. 参考(二)创建metallb池子

* 一个地址192.168.1.120给coredns使用
* 一个地址192.168.1.121给ingress-nginx-controller使用

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: lan-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.120/32
  serviceAllocation:
    priority: 10
    serviceSelectors:
    - matchLabels:
        app.kubernetes.io/name: coredns   # 注意这里的缩进
---
# L2Advertisement
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: lan-pool-l2-adv
  namespace: metallb-system
spec:
  # 必须明确指定要宣告的 IP 池名称
  ipAddressPools:
    - lan-pool
    - lan-pool2
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: lan-pool2
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.121/32
  serviceAllocation:
    priority: 9
    serviceSelectors:
    - matchLabels:
        app.kubernetes.io/component: controller
        app.kubernetes.io/instance: ingress-nginx
```

2. 为kube-dns创建一个LoadBalancer

```shell
kubectl patch svc coredns -n kube-system -p '{"spec": {"type": "LoadBalancer"}}'

```


3. 修改CoreDNS配置将ingress暴露出去

```conf
  Corefile: |
    lxw.com:53 {
        errors
        health
        hosts {
            # 把下面这个 IP 换成你 Ingress Controller 的 Cluster IP
            # 193.169.168.108 local.lxw.com
            192.168.1.121 grafana.lxw.com
            fallthrough
        }
    }

```

