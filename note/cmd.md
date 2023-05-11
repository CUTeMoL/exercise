# cmd

## 一、命令

## 0.cmd

进入解释器

```cmd
cmd
cmd /C # 执行字符串指定的命令后终止(退出终端)
cmd /K # 保持cmd终端状态
```

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

内置变量

```cmd
%errorlevel%  # 上一条命令的执行结果,0正常
``


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
@echo on # 有@本行'echo on'不显示,只执行命令,其余行会显示
```

### 3. rem

注释

```cmd
rem message # 注释信息echo on下会回显
```

`::`也可以用于注释,和`rem`的区别在于`echo on`下是否回显

### 4. pause

暂停

```cmd
pause # 暂停,然后输入任意键继续
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

新建一个终端运行外部程序,无论是否成功都会继续执行之后的语句

```cmd
start explorer D:\
```

### 10. cls

清屏

### 11. assoc

文件拓展名关联,即使用后缀名关联决定文件的类型

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
/M # 列出调用的模块,若指定模块则列出使用此模块的进程
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
/S # 删除所有子目录中的指定的文件
/Q # 安静模式.删除全局通配符时,不要求确认
```

### 22. ren

```cmd
ren old_name new_name
```

### 23.xcopy

复制`src`文件夹中所有的内容到某一以存在的`dest`文件夹

```
xcopy /E /Q src dest
```

复制`src`文件夹中的内容到不存在的`dest`文件夹(相当与文件夹复制后重命名)

```cmd
xcopy /E /Q /I /Y src dest
/E # 复制目录和子目录,包括空目录
/Q # 复制时不显示文件名
/I # 如果目标不存在,且要复制多个文件,则假定目标必须是目录,并创建这个目录
/Y # 确认覆盖
```

### 24.tree

```cmd
TREE
显示当前文件夹下所有子目录
/F # 显示文件名
/A # 使用 ASCII 字符,而不使用扩展字符
```

### 25.chkdsk

```cmd
CHKDSK
/F # 将检查所有磁盘,并修复磁盘错误
```

### 26.dir

```cmd
DIR
/A:属性 # 根据属性筛选
属性         D  目录                R  只读文件
               H  隐藏文件            A  准备存档的文件
               S  系统文件            I  无内容索引文件
               L  重新分析点          O  脱机文件
               -  表示“否”的前缀
/B # 使用空格式,仅输出对象名称,一行一个对象
/C # 显示千位分割符(默认),-C不显示千位分割符
/D # 使用空格式,分栏输出,类似ls
/L # 小写
/N # 新的长列表格式,其中文件名在最右边(默认),/-N文件名在左
/O:规则 # 确定输出的排序规则
排列顺序     N  按名称(字母顺序)    S  按大小(从小到大)
               E  按扩展名(字母顺序)  D  按日期/时间(从先到后)
               G  组目录优先           -  反转顺序的前缀
/P # 在每个信息屏幕后暂停
/Q # 显示拥有者
/R # 显示文件的备用数据流
/S # 显示指定目录,及子目录的
/T:时间段 # 控制显示的时间段
时间段      C  创建时间
              A  上次访问时间
              W  上次写入的时间
/W # 显示宽格式,分栏输出,类似ls
/X # 显示为非 8dot3 文件名产生的短名称.格式是 /N 的格式,短名称插在长名称前面.如果没有短名称,在/其位置则显示空白.
/4 # 以四位数字显示年份
```

### 27.rar.exe

基础命令格式

```cmd
rar.exe <命令>  [ -args ]  <压缩文件>  [ <@列表文件...> ] [ <文件...> ]  [ <解压路径\> ]
命令:
a rarfile file # 添加文件到压缩文件中
m[f] rarfile file # "m"添加文件到压缩文件中,然后删除源文件,"mf"不删除空文件夹
x rarfile target_path # 带绝对路径解压
d rarfile file # 从压缩文件中删除文件
u rarfile file # 更新压缩文件中的文件,根据修改时间
f rarfile file # 更新压缩文件中的文件,根据修改时间,但是不添加新文件
l rarfile [file] # 列表输出压缩包中的文件,lt多行模式详细输出,lta多行模式详细输出同时给出服务器头,lb仅文件名
v rarfile [file] # 列表输出压缩包中的文件,比l多"压缩后的大小"、"压缩率"、"校验和",vt多行模式详细输出,vta多行模式详细输出同时给出服务器头,vb仅文件名
p rarfile [file] # 打印文件内容
c"注释" # 添加注释到压缩文件
e # 不带压缩路径解压文件(尽量使用x)
i[cht]="string" rarfile file # 搜索压缩文件中的文件,不区分大小写
  c # 搜索压缩文件中的文件,区分大小写
  h # 十六进制搜索
  t # 使用 ANSI、UTF-8、UTF-16 和 OEM (仅 Windows)字符表
rn rarfile *.txt *.bak <源文件名1> <目标文件名1> <源文件名n> <目标文件名n># 重命名

args:
-o[+|-| ] # +覆盖同名文件,-不覆盖," "询问
-or # 如果相同名字的文件已经存在则自动重命名解压的文件
-mt[thread] # 设置线程数
-m[0|1|2|3|4|5] # 0不压缩,3标准,5高压
-ad[1|2] # "ad"和"ad1"批量解压时为每个压缩文件创建一个与压缩文件同名的目录,"ad2"不创建直接解压
-ag[YYYY-MM-DD] # 为压缩文件添加日期,使用默认"YYYYMMDDHHMMSS"格式
-r # 递归,"-r-"禁用递归
-y # yes
-x<file> # 排除指定的文件,可以数次指定参数'-x'来定义,使用 "*\filename" 语法排除所有目录中的所有"filename"
-ed # 排除空目录
-ep[1|2|3] # ep从文件名中排除目录(仅保留文件名),-ep1从文件名中排除命令行指定的目录,-ep2压缩时拓展为完全路径(无盘符),-ep2压缩时拓展为完全路径(有盘符)
-e+<attr> # 根据属性排除
-p # 密码,"-p-"不询问密码
-hp # 高级加密
-ai # 忽略文件属性在 Windows 中它影响存档、系统、隐藏和只读属性.在 Unix 中,用户、组和其它文件属性.
-ap # 设置添加文件到压缩文件中的内部路径,或者解压时不带此路径解压
-as # 同步压缩文件内容没有的文件会从压缩文件中删除,通常配合u使用
-f # 更新文件,解压或创建压缩文件时使用,解压时添加此参数则只有旧文件能被从压缩文件中解压的新版本替换
-df # 压缩后删除文件
-dr # 压缩后删除文件到回收站
-t # 压缩后测试文件,搭配"m"使用,压缩文件存在,才可以删除文件
-id[c,d,n,p,q] # 显示或禁用消息
  c # 禁用版权字符串
  d # 在操作结束禁止显示“完成”字符串
  n # 在创建、测试或提取压缩文件时,禁用已归档
  p # 禁止百分比指示
  q # 打开安静模式,仅错误消息和问题能被显示
-inul # 禁止所有消息
-ilog[文件名] # 记录错误到文件中
-s # 创建固实压缩文件
-ta[m,c,a,o]<日期> # 只处理指定日期之后修改的文件
-tb[m,c,a,o]<日期> # 只处理指定日期之前修改的文件
-tn[m,c,a,o]<时间> # 处理指定时间以后的新文件
-to[m,c,a,o]<时间> # 处理指定时间以前的旧文件
示例:
rar "ic=first level" -r c:\*.rar *.txt # 查询字符串

```

压缩

```cmd
rar.exe a -m[level] rarfile file
level:
0-5 # 0不压缩,3标准,5高压
```

解压

```cmd
rar.exe x -o+ %rarfile% %target_path%
x # 带绝对路径解压
-o # 覆盖前询问
-o+ # 覆盖所有
```

### 28.日期时间

```cmd
date # 输出日期
/T # 仅输出当前时间

time # 输出时间
/T # 仅输出当前时间

%date:~0,4%-%date:~5,2%-%date:~8,2%
```

### 29.chcp

```cmd
chcp [number] # 修改代码页
number:
936 # 简体中文GB2312
65001 # utf-8
```

## 二、管理工具

### 1. `secpol.msc`

本地安全策略(防火墙)

#### ipsec创建安全策略的步骤

创建IP安全策略, 不激活默认响应规则,不编辑属性

```cmd
netsh ipsec static add policy name="reject"
```

双击IP安全策略,不使用向导

添加阻止所有,添加IP筛选器名为`拒绝所有`,属性编辑好源地址、目标地址、协议为`任意`,筛选器操作为`阻止`(需要自己新建)

```cmd
netsh ipsec static add filteraction name="阻止" action=block # 添加筛选器操作
netsh ipsec static add filterlist name="拒绝所有" # 添加筛选器
netsh ipsec static add filter filterlist="拒绝所有" srcaddr=any dstaddr=any description="拒绝一切" protocol=any mirrored=yes # 编辑筛选器的属性,即具体生效的规则
netsh ipsec static add rule name="rejectlist" policy="reject" filterlist="拒绝所有" filteraction="阻止" # 关联前面创建的policy、filteraction、filterlist命名为rejectlist
```

然后放行个别添加IP筛选器名为`允许网段192.168.1.0`,属性编辑好源地址`192.168.1.0`、目标地址`我的IP地址`、协议为`TCP`,到端口`3389`筛选器操作为`允许`(需要自己新建)

策略导出

```cmd
netsh ipsec static exportpolicy secpol.ipsec
```

### 2. `taskschd.msc`

计划任务

```cmd
SCHTASKS /parameter [args]
parameter:
/Create # 创建计划任务
/Delete # 删除计划任务
/Query # 显示所有计划任务
/Change # 更改计划任务属性
/Run # 按需运行计划任务
/END # 终止正在运行的计划任务
/ShowSid # 显示与计划任务名称相对应的安全标识符
args:
/S system # 指定要连接的远程系统
/U username # 指定要执行的用户上下文
/P password # 指定密码
/TN taskname # 指定检索的任务名
```

查询计划任务

```cmd
SCHTASKS /Query [args]
args:
/FO [table|LIST|CSV] # 输出格式,TABLE模式下"/NH"可以不显示列标题
/V # 详细模式输出 
/XML # 输出为XML格式
/HRESULT # 为获得更出色的故障诊断能力,处理退出代码,将采用 HRESULT 格式
```

创建计划任务

```cmd
SCHTASKS /Create [args]
args:
/RU username # 指定任务在其下运行的“运行方式”用户帐户(用户上下文).对于系统帐户,有效值是 ""、"NT AUTHORITY\SYSTEM"或"SYSTEM".对于 v2 任务,"NT AUTHORITY\LOCALSERVICE"和"NT AUTHORITY\NETWORKSERVICE"以及常见的 SID 对这三个也都可用.默认情况下,任务使用本地计算机的当前用户的权限运行
/RP password # 指定运行用户的密码,"SYSTEM"用户不需要指定密码
/SC schedule # 计划任务频率

```



### 3. `services.msc`

查看服务以及编辑服务属性

#### 查询服务

```cmd
sc [<ServerName>] query [<ServiceName>] [type= {driver | service | all}] [type= {own | share | interact | kernel | filesys | rec | adapt}] [state= {active | inactive | all}] [bufsize= <BufferSize>] [ri= <ResumeIndex>] [group= <GroupName>]
state:
active # 已启动的服务
inactive # 未启动的服务
all # 所有状态的服务

type:
driver # 驱动
service # 服务,默认
all # 所有类型

type:
own # 不与其他服务共享可执行文件
share # 它与其他服务共享可执行文件
interact # 交互式服务
kernel # 指定驱动程序
filesys # 指定文件系统驱动程序
rec 
adapt
```

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

导出组策略

```cmd
secedit /export /cfg gpedit.inf
```

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

| 关键字    | 说明            |
| ------ | ------------- |
| `Path` | 指定通道          |
| `[]`   | 包裹字段          |
| `@`    | 当该标签包含多个字段时加上 |
| `and`  | 和             |
| `or`   | 或             |

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
tzutil.exe /s "China Standard Time" # 设定时区,时区添加后缀"_dstoff"将禁用夏令时调整
```

### 14.`wmic`

已经弃用,可以使用`Get-WmiObject`替代

```cmd
wmic cpu # 获取cpu信息
wmic process # 查询运行程序,可以查询commandline
wmic product # 查询已安装软件

筛选条件:
where key="value" # 条件查询
name="process name" get "item1,item2"
```

### 15.`regedit`

注册表,树形数据库管理配置文件

| 根键                    | 说明  |
| --------------------- | --- |
| `HKEY_CLASSES_ROOT`   |     |
| `HKEY_CURRENT_USER`   |     |
| `HKEY_LOCAL_MACHINE`  |     |
| `HKEY_USERS`          |     |
| `HKEY_CURRENT_CONFIG` |     |

### 命令行用法

```cmd
reg Operation [Parameter List]
Operation:
QUERY # 查询
ADD # 添加配合/f可以修改
DELETE # 删除
COPY # 复制
SAVE
LOAD
UNLOAD
RESTORE
COMPARE
EXPORT
IMPORT
FLAGS
```

#### 查询

```cmd
reg query "KeyName" [Parameter]
Parameter:
/v # 具体的注册表项值的查询
/ve # 查询默认值与/f冲突
/s # 循环查询所有子项,最后一位不能是"\"
/se # 为 REG_MULTI_SZ 在数据字符串中指定分隔符(长度只为 1 个字符),默认分隔符为 "\0"
/f # 指定包含的字符,如果字符串包含空格,请使用双引号.默认为 "*"
/k # 指定只在项名称中搜索,与/f配合使用
/d # 指定只在数据中搜索,与/f配合使用
/c # 指定搜索时区分大小写,与/f配合使用,默认不区分大小写
/e # 指定只返回完全匹配,默认返回所有匹配
/t # 指定数据类型,默认为所有类型
数据类型:
REG_SZ, REG_MULTI_SZ, REG_EXPAND_SZ, REG_DWORD, REG_QWORD, REG_BINARY, REG_NONE
/z # 详细: 显示值名称类型的数字等值
/reg:32 # 指定应该使用 32 位注册表视图访问的注册表项
/reg:64 # 指定应该使用 64 位注册表视图访问的注册表项
# 示例
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.10\PythonPath"
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.10\InstallPath"  /v ExecutablePath
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.10\InstallPath"  /ve

```

### 16.taskmgr.exe

任务管理器

## 三、语法

### for

```cmd
FOR %variable IN (set)DO command [command-parameters]
%variable # bat文件中要用%%variable
(set)# (file-set)、("string")、(`command`)

```

批量修改mysql库的引擎

```cmd
SET DBNAME=database
for /F "usebackq tokens=*" %i in (`mysql -uroot -p123456 -P3311 -s -N -e "select TABLE_NAME from information_schema.TABLES WHERE TABLE_SCHEMA='%DBNAME%' and ENGINE='MyISAM';" `) do mysql -uroot -p123456 -P3311 -s -N -e "ALTER TABLE %DBNAME%.%i ENGINE=INNODB;"
```

## 拓展linux命令

1.安装git

2.添加环境变量

打开系统高级设置

添加一下环境

```cmd
C:\Program Files\Git\bin
C:\Program Files\Git\usr\bin
```

# tmp

如果是非常驻进程修改了系统时间,那么通过上面步骤查看到的进程ID在任务管理器中是查看不到的,因为他们执行后就结束了,那么我们需要增加下系统日志的进程审核记录来获取到这些进程的信息.

```
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1
auditpol.exe /set /subcategory:"{0CCE922B-69AE-11D9-BED3-505054503030}" /success:enable /failure:enable
gpupdate /force
```
