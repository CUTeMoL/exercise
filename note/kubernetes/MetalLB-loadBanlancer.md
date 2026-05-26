
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
  - 192.168.1.120-192.168.1.130
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

以kube-dns为例创建一个LoadBalancer

```shell
kubectl patch svc coredns -n kube-system -p '{"spec": {"type": "LoadBalancer"}}'

```