# git

## 一、命令

1.本地建立仓库

```shell
git init # 会在工作区生成一个.git文件夹
```

2.查询状态

```shell
git status # 查看当前分支,工作区、暂存区信息比对
git log # 提交记录，可以查询提交的ID
git reflog # 回退版本后消失的记录
```

3.工作区到暂存区

```shell
git add ${file} # 添加文件到暂存区
git add . # 添加所有文件到仓库
git add -A # 添加所有文件到仓库
git rm ${file} # 删除暂存区的文件
```

4.暂存区到工作区

```shell
git checkout -- ${file} # 将文件从暂存区取到工作区
git checkout -- . # 将所有文件从暂存区取到工作区
```

5.从暂存区提交到正式仓库

```shell
git commit -m "提交信息" ${file} # 提交某文件到仓库
```

6.从正式仓库倒退版本

```shell
git reset --hard ${commit id}
--hard # 倒退版本时保持工作区和暂存区与正式仓库对应版本一致
```

7.从远程仓库下载

```shell
git clone ${url}
```

8.推送到远程仓库

```
git push 
```

9.更新本地的仓库

```
git pull
```

10.分支

```shell
git branch # 查看分支
git branch ${branchname} # 创建分支
git checkout ${branchname} # 切换分支
git merge ${branchname} # 合并分支
git branch -d ${branchname} # 删除分支
```

11.设置

```shell
git config 
-l # 查看当前设置
--global # 用于设置用户信息
--system # 系统设置
--local # 本地设置，远程路径、分支相关
```

