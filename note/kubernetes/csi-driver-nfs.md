# csi-driver-nfs

## 一、部署

### 1. 下载helm包

```shell
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
helm repo update
helm pull  csi-driver-nfs/csi-driver-nfs --version v4.8.0
```

### 2. 解压

```shell
tar xvf csi-driver-nfs-v4.8.0.tgz
mv csi-driver-nfs csi-driver-nfs-4.8.0
cd csi-driver-nfs-4.8.0
```

### 3. 修改values.yaml

修改镜像下载地址

```diff
3c3
<     baseRepo: registry.k8s.io
---
>     baseRepo: k8s.m.daocloud.io
5c5
<         repository: registry.k8s.io/sig-storage/nfsplugin
---
>         repository: k8s.m.daocloud.io/sig-storage/nfsplugin
9c9
<         repository: registry.k8s.io/sig-storage/csi-provisioner
---
>         repository: k8s.m.daocloud.io/sig-storage/csi-provisioner
13c13
<         repository: registry.k8s.io/sig-storage/csi-snapshotter
---
>         repository: k8s.m.daocloud.io/sig-storage/csi-snapshotter
17c17
<         repository: registry.k8s.io/sig-storage/livenessprobe
---
>         repository: k8s.m.daocloud.io/sig-storage/livenessprobe
21c21
<         repository: registry.k8s.io/sig-storage/csi-node-driver-registrar
---
>         repository: k8s.m.daocloud.io/sig-storage/csi-node-driver-registrar
25c25
<         repository: registry.k8s.io/sig-storage/snapshot-controller
---
>         repository: k8s.m.daocloud.io/sig-storage/snapshot-controller
171a172
>
```

### 4. 安装

```shell
helm upgrade --install csi-driver-nfs ./  --namespace csi-driver   --create-namespace   -f values.yaml --set feature.enableVolumeSnapshot=false
```

### 5. 创建StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi-192-168-1-55
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: nfs.csi.k8s.io
parameters:
  server: 192.168.1.55
  share: /data/nfs_data_volume
  mountPermissions: "0"
  subDir: ${pvc.metadata.namespace}/${pvc.metadata.name}/${pv.metadata.name} 
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

### 6. 测试

(1) 应用这个配置

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: busybox-nfs-pvc
  # namespace: default   # 按需修改
spec:
  storageClassName: nfs-csi-192-168-1-55
  accessModes:
    - ReadWriteMany       # NFS 支持多节点读写
  resources:
    requests:
      storage: 1Gi        # 实际容量只要不超过共享总空间即可，这里按声明大小
---
apiVersion: v1
kind: Pod
metadata:
  name: busybox-nfs-test
  # namespace: default
spec:
  containers:
  - name: busybox
    image: busybox:stable
    command: ["sleep", "3600"]
    volumeMounts:
    - name: nfs-storage
      mountPath: /data
  volumes:
  - name: nfs-storage
    persistentVolumeClaim:
      claimName: busybox-nfs-pvc
  restartPolicy: Always
```

(2) 进入容器后在/data里创建文件

```shell
kubectl exec -it busybox-nfs-test -- sh 
```

(3) 验证nfs服务器上已经出现文件

由于前面指定了`subDir=${pvc.metadata.namespace}/${pvc.metadata.name}/${pv.metadata.name}`,所以可以参考以下路径找`/data/nfs_data_volume/default/busybox-nfs-pvc/pvc-986d7e0e-8706-4f0a-ad55-f2caa4b22ab2`