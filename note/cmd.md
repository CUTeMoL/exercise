# cmd

## 一、命令

### 1. set

设置变量

```cmd
set key=value
set /p key=comment # 接受用户输入value
set /a # 表达式计算
```

打印变量值

```cmd
set # 打印所有设置过的变量
set key # 打印^key的变量
```

取消变量

```cmd
set key=
```

使用变量

```cmd
%variable%
```

### 2. echo

回显

```cmd
echo on # 每一行的内容都要显示出来
echo off # 只显示执行结果
echo message # 显示消息(cmd中遇空格不换行)
echo "message" # 显示消息(不加引号时powershell中遇空格换行)
```

`@`本行只显示运行结果

```cmd
@echo on # 有@本行'echo on'不显示,只执行命令，其余行会显示
```

### 3. rem

注释

```cmd
rem message # 注释信息echo on下会回显
```

`::`也可以用于注释，和`rem`的区别在于`echo on`下是否回显

### 4. pause

暂停

```cmd
pause # 暂停，然后输入任意键继续
echo 注释信息 & pause > nul # 暂停并显示注释信息
```

### 5. title

```cmd
title title_message # 窗口的标题设置
```

### 6. goto

移动到`:label`这个标签的位置,可以创建循环

```cmd
:label1
set /a var+=1
echo %var%
if %var% leq 3 goto label1
pause
```

### 7. find

文件中搜索指定字符串

```cmd
find [option] "string" [drive:]\[path]\filename
/V 未包含
/C 包含字符串的行数
/N 显示行号
/I 忽略大小写
```

### 8. type

显示文件内容

```cmd
type [drive:]\[path]\filename
```

### 9. start

新建一个终端运行外部程序，无论是否成功都会继续执行之后的语句

```cmd
start explorer D:\
```

### 10. cls

清屏

### 11. assoc

文件拓展名关联，即使用后缀名关联决定文件的类型

```cmd
assoc # 显示所有文件拓展名的关联
assoc.txt # 显示.txt文件拓展名的关联
assoc.txt=Word.Document.8 # 修改.txt文件拓展名关联到word文档
```

### 12. ftype

文件类型关联的打开程序路径

```cmd
ftype # 显示所有文件类型的打开程序路径
ftype exefile # 显示exefile的打开程序路径
ftype exefile="%1" %*
```

### 13. whoami

查询计算机名及用户

```cmd
whoami /all
```

### 14. sysprep

重新生成SID

```cmd
sysprep
```

### 15. convert

转换硬盘格式

```cmd
convert e: /fs:ntfs
```

### 16. tasklist

列出进程

```cmd
tasklist 
/M # 列出调用的模块，若指定模块则列出使用此模块的进程
/SVC # 列出操控此进程的服务名
/FO # 指定输出格式"TABLE","LIST","CSV"
```

### 17. start

运行程序或命令

```cmd
start process_name
```

### 18. taskkill

```cmd
taskkill
/PID # 指定PID
/IM # 指定名称
/T # 包括子进程
/F # 强制
```

### 19. net

服务管理

```cmd
net start # 列出启动的服务
net start service_name # 启动服务
```

### 20. copy

复制

```cmd
copy dir\file_name dir\file_name
```

### 20. move

剪切

```cmd
move dir\file_name dir\file_name
```

### 21. del

删除

```cmd
del file_name
```

### 22. ren

```cmd
ren old_name new_name
```

## 二、管理工具

### 1. `secpol.msc`

本地安全策略(防火墙)

#### ipsec创建安全策略的步骤

创建IP安全策略, 不激活默认响应规则，不编辑属性

```cmd
netsh ipsec static add policy name="reject"
```

双击IP安全策略，不使用向导

添加阻止所有，添加IP筛选器名为`拒绝所有`，属性编辑好源地址、目标地址、协议为`任意`，筛选器操作为`阻止`（需要自己新建）

```cmd
netsh ipsec static add filteraction name="阻止" action=block # 添加筛选器操作
netsh ipsec static add filterlist name="拒绝所有" # 添加筛选器
netsh ipsec static add filter filterlist="拒绝所有" srcaddr=any dstaddr=any description="拒绝一切" protocol=any mirrored=yes # 编辑筛选器的属性，即具体生效的规则
netsh ipsec static add rule name="rejectlist" policy="reject" filterlist="拒绝所有" filteraction="阻止" # 关联前面创建的policy、filteraction、filterlist命名为rejectlist
```

然后放行个别添加IP筛选器名为`允许网段192.168.1.0`，属性编辑好源地址`192.168.1.0`、目标地址`我的IP地址`、协议为`TCP`，到端口`3389`筛选器操作为`允许`（需要自己新建）

### 2. `taskchd.msc`

查看计划任务

### 3. `services.msc`

查看服务以及编辑服务属性

#### 编辑服务属性

```cmd
net start service_name # 启动
net stop service_name # 停止
sc create service_name binpath= "dir/file"
sc config service_name start= disabled # 禁用
sc config service_name start= auto # 自动启动
sc delete service_name # 卸载命令
# 所有等号后面必须空一格！！！
```

### 4. `gpedit.msc`

组策略

### 5. `lusrmgr.msc`

用户和组分配权利和权限管理

### 6. `diskmgmt.msc`

磁盘分区管理

### 7. `appwiz.cpl`

程序与功能

### 8. `eventvwr`

系统日志

```cmd
eventvwr # 启动事件查看器
/l:<logfile> # 指定日志文件
/c:<channel> # 指定通道名称
/v:<query or view file> # 指定视图文件
# /l、/c、/v 互斥
/f:* # 筛选内容如果包含空格则需要使用双引号

eventvwr /c:System /f:*"[System[Execution[@ProcessID='4'] and (EventID='1')]]"
```

自定义筛选语法

```xml
<QueryList>
  <Query Id="0" Path="System">
    <Select Path="System">*[System[Execution[@ProcessID="4"] and (EventID="1" or EventID="6")]]</Select>
  </Query>
</QueryList>
```

| 关键字 | 说明                       |
| ------ | -------------------------- |
| `Path` | 指定通道                   |
| `[]`   | 包裹字段                   |
| `@`    | 当该标签包含多个字段时加上 |
| `and`  | 和                         |
| `or`   | 或                         |



### 9. `perfmon`

性能收集器

### 10. `msconfig`

系统配置

### 11. `explorer.exe`

文件管理器

### 12. `mmc`

控制台

### 13.`tzutil.exe`

时区设定

```cmd
tzutil.exe /g # 显示当前设定的时区
tzutil.exe /l # 列出可设定的时区
tzutil.exe /s "China Standard Time" # 设定时区
```

