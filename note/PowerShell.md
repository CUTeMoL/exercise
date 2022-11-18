# PowerShell

# 一、基本概念

1.启动

powershell管理员身份运行

```powershell
start-process PowerShell -verb runas 
```

执行命令后退出

```powershell
powershell -Command "command"
powershell -c "command"
echo {Commmand} | powershell - # "-"代表接收管道 长脚本需要{}
powershell iex "command" # iex可以绕过脚本执行策略
```

获取帮助

```powershell
Get-Help
help
man 
```

2.script

以`.ps1`结尾文件

| 执行级别         | 执行策略                                              |
| ------------ | ------------------------------------------------- |
| AllSigned    | 必须有受信任的签名才运行                                      |
| Bypass       | 没有任何限制的执行，且没有安全提示                                 |
| Default      | 系统默认策略                                            |
| RemoteSigned | Windows Server默认策略，除非有有效数字签名，否则只运行本地脚本，不运行网络下载的脚本 |
| Restricted   | Windows默认策略，仅可执行单个语句，不可执行脚本                       |
| Unrestricted | 允许所有脚本运行，但会报警                                     |
|              |                                                   |



```powershell
Set-ExecutionPolicy Unrestricted # 改变默认执行策略以执行脚本
```

运行指定的脚本

```powershell
powershell -File /path [*args]
```

3.格式化输出

搭配`|`可以对回显内容格式化显示，精简过滤所需信息

`FL`键值对显示

```powershell
cmdlet |FL <key1>,<key2>
```

`FT`2元关系表显示

```powershell
cmdlet |FT <key1>,<key2> -autosize 
```

## 二、基本命令

`command-lets`是`powershell`的轻量级命令通常遵守`verb-noun`的规律

| 命令                                                                      | 说明                                         |
| ----------------------------------------------------------------------- | ------------------------------------------ |
| `Get-Help cmdlet_object`                                                | 帮助文档                                       |
| `Get-Command`                                                           | 查看cmdlet、function、alias信息，支持通配符*匹配         |
| `Get-Service`                                                           | 获取服务                                       |
| `Set-Variable object value`                                             | 设置变量                                       |
| `Start-Process`                                                         | 打开文件                                       |
| `Add-content file_object message`                                       | 将内容添加到指定的文件                                |
| `Add-Computer`                                                          | 将本地计算机添加到域或工作组                             |
| `Add-jobTrigger`                                                        | 将作业触发器添加到计划的作业中                            |
| `Clear-Content`                                                         | 删除文件的内容，但不删除该文件。                           |
| `Add-member`                                                            | 将自定义方法或属性添加到PowerShell对象的实例                |
| `Add-type`                                                              | 将Microsoft .NET框架类添加到Windows PowerShell会话中 |
| `(New-Object System.Net.WebClient).DownloadFile("src_path","filename")` | 下载文件                                       |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |
|                                                                         |                                            |

`PowerShell`可以运行`Shell`的命令

| `ls`      |
| --------- |
| `cd`      |
| `pwd`     |
| `clear`   |
| `cp`      |
| `rm`      |
| `rmdir`   |
| `echo`    |
| `sleep`   |
| `history` |
| `kill`    |
| `ps`      |
| `man`     |

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
