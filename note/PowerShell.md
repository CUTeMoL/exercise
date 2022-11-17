# PowerShell

# 一、基本概念

1.启动

```powershell
start-process PowerShell -verb runas # powershell管理员身份运行
```

2.script

以`.ps1`结尾文件

```powershell
Set-ExecutionPolicy Unrestricted # 改变默认执行策略以执行脚本
```

## 二、基本命令

`command-lets`是`powershell`的轻量级命令通常遵守`verb-noun`的规律

| 命令                                | 说明                                         |
| --------------------------------- | ------------------------------------------ |
| `Add-content file_object message` | 将内容添加到指定的文件                                |
| `Add-Computer`                    | 将本地计算机添加到域或工作组                             |
| `Add-jobTrigger`                  | 将作业触发器添加到计划的作业中                            |
| `Clear-Content`                   | 删除文件的内容，但不删除该文件。                           |
| `Add-member`                      | 将自定义方法或属性添加到PowerShell对象的实例                |
| `Add-type`                        | 将Microsoft .NET框架类添加到Windows PowerShell会话中 |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |
|                                   |                                            |



`PowerShell`可以运行`Shell`的命令

| `ls`    |
| ------- |
| `cd`    |
| `pwd`   |
| `clear` |
| `cp`    |
| `rm`    |
| `echo`  |
|         |
|         |
|         |

`powershell`和`shell`不一样的

| Bash    | PowerShell | 描述         |
| ------- | ---------- | ---------- |
| `touch` | `new-item` | 创建一个新的文本文件 |
|         |            |            |
|         |            |            |
|         |            |            |
|         |            |            |
|         |            |            |
|         |            |            |
|         |            |            |
|         |            |            |

## 三、注释

`#`  单行注释

```powershell
<# 
多行注释
#>
```
