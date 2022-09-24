# shell

## 一、变量

### 创建变量

```shell
declare
-i   ：将变量看成整数
-r   ：变量设为只读
-x   ：等同于export
-a   ：指定为索引数组
-A   ：指定为关联数组
```

将命令的执行结果存到变量

```shell
`command`
$(command) 
```

交互式定义变量

```shell
read
-p  提示信息
-n  限制在N字符数以内
-s  不显示（密码）
-t   超时时间（秒）
```

临时全局生效

```shell
export variable_name=value
```

永久全局生效

```shell
echo 'export variable_name=value' >>  /etc/profile
```

永久某用户生效 

```shell
echo 'export variable_name=value' >> ~/.bashrc
```

### 内置变量

```shell
$?:上一条命令的返回状态0成功、127没这命令、126无有权限执行、1&2没有文件或目录
$$:当前终端进程号
$!:当前终端后台运行的最后一个进程号
!$:最后一条命令历史中的参数
!!:最后一条命令历史
$#:脚本后面的参数个数
$*:脚本后面的参数空格分开合成1条输出
$@:脚本后面的参数，独立输出
$0:当前执行的进程/程序名
$1~$9 and ${10}~${n}:位置参数10以后要{}
$RANDOM :0~32767
```

产生随机数

```shell
echo $[$RANDOM%51+50]   #50-100之间的随机数
```

### 取消变量

```shell
unset variable_name
```

### 使用变量

```shell
${variable_name}
```

## 二、数组

普通数组：只能使用整数作为数组索引(元素的下标)
关联数组：可以使用字符串作为数组索引(元素的下标)

### 创建数组

```shell
array[0]=v1
array=变量的名字
[0]=下标
v1=变量的数值
```

一次赋值多个

```shell
array=(var1 var2 var3 var4)
array1=(`cat /etc/passwd`)   
#文件的每一行赋值给数组
array2=(`ls /root`)
array3=(harry amy jack "Miss Hou")
array4=(1 2 3 4 "hello world" [10]=linux)
echo ${array4[2]}       3
echo ${array4[4]}       hello world
echo ${array4[10]}      linux
```

### 使用数组

```shell
${array[i]}  要用{}不然只会显示第一个
${array[*]}  获取所有元素
${#array[*]}  获取所有元素个数
${!array[@]}  获取所有元素索引下标
${array[@]:1:2} 从1开始，获取后面的2个元素
```

## 三、函数

```shell
function function_name() {
    command1
    command2
    return 0 # 函数中可以添加return，反应此函数的运行状态,return会退出函数
}

function $para ${array[@]} # 可以传递参数，参数可以是变量、数组
```

## 四、四则运算

```shell
$((表达式))
$[表达式]
expr 表达式
let 表达式
let n+=1  == let n=n+1
let n=i++   先赋值再运算
let n=++j   先运算再赋值
```

## 五、条件判断

正确 return 0

用法

```shell
test [option] file
-e   是否存在
-f   是否为普通文件
-d   是否为目录
-s   判断是否非空  非空为真
-S   socket
-p   pipe
-c   character
-b   block
-L   软link
-r   是否可读
-w   是否可写
-x   是否可执行
-u   是否有SUID
-g   是否有SGID
-k   是否有t位
```

```shell
test -e file
[ -d /shell ]
[ ! -d /shell ]
[[ -f /shell/1.sh ]]   
```

[]可以在判断式中使用正则

文件之间的比较：

```shell
[ file1 -nt file2 ]  比较是否更新
[ file1 -ot file2 ]  比较是否更旧
[ file1 -ef file2 ]  是否为同一个文件（硬链接相同inode）
```

整数之间比较：

```shell
-eq   相等
-ne   不等
-gt   大于
-lt   小于
-ge   大于等于
-le   小于等于
```

字符串之间的判断：

```shell
-z   是否为空的字符串，长度为零成立
-n   字符串非空成立
[ $A = $B ]    判断两个字符串是否相等
[ $A != $B ]    判断两个字符串是否不相等
[ "A" != "B" ] 
```

多重条件逻辑判断：

```shell
[ 1 -eq 1 -a 1 -ne 0 ]        true
[ 1 -eq 1 ] && [ 1 -ne 0 ]    true
[ 1 -eq 0 ] || [ 1 -ne 0 ]    true
```

类C风格:

```shell
使用((   ))
=   表示赋值
==   表示判断
((2==2))    true
((3>=2))    true
((3!=2))    true
((a=2))    a=2
```

## 六、条件判断

### if 、else判断

```shell
if [   ];then
    command1
elif [   ];then
    command2
else
    command3
    if [];then
        command4
    else
        command5
    fi
fi
```

### case判断

```shell
case var in
    value1|v1)
        command1
    ;;
    value2|v2)
        command2
    ;;
    value3|v3)
        command3
    ;;
    *)
        command4
    ;;
esac
```

## 七、循环

循环中的标志

```shell
continue 直接跳到下一次循环
break 跳出循环，执行循环后的代码
exit n 直接跳出程序 并返回n
shift n 参数向左移动n位 默认1位
```

### for循环

```shell
for variable in {  }
do
    command
done
```

用户定义变量

```shell
for variable
do
    command
done
```

类C风格

```shell
for (( i=1;i<=5;i++ ))
do
    echo $i
    continue
    break
    exit
done
```

### while、until循环

while

条件为真则一直执行循环体

```shell
while [ true ]
do
    command
done
```

until

一直执行循环体直到条件为真

```shell
until [ false ]
do
    command
done
```

从文件中获取变量

```shell
cat file|while read var1 var2
do
    command
done
```

## 八、expect

```shell
/usr/bin/expect <<-END 
    spawn command
    set timeout 3
    expect {
        "message" { send "command/$var\r";exp_continue }
        "message" { send "command/$var\r" }
    }
    expect eof
END
```

`/usr/bin/expect <<END`  表示接下里要启用expect交互,直到遇见END

`spawn` 启动一项程序

`set timeout n`设置`expect`的等待时间`-1`永不超时

`expect "message" { send "command/$var\r" }` 从进程接收信息,表示捕捉到某一条消息就执行某一些操作

`send "command"`发送字符串

`exp_continue` 表示如果不存在就跳过这一步

`expect eof` 表示此expect结束了

`interact`允许用户交互

## 九、常用命令

### 文本处理类

#### grep

```shell
grep  [option]  [file]
# 行 文本 匹配
-i:不区分大小写
-v:查找不包含指定内容的行（取反）
-w:按单词搜索
-o:仅打印匹配关键字
-c:统计匹配到的次数（行数）
-n:显示行号
-r:逐层遍历目录查找（这样grep就可对目录使用）
-A:显示匹配行及后面n行
-B:显示匹配行及前面n行
-C:显示匹配行及前后后n行
-l:只列出匹配的文件名（配合-r）
-L:列出不匹配的文件名（配合-r）
-e:使用正则匹配
-E:使用拓展正则
^key:以关键字开头
key$:以关键字结尾
^$:匹配空行
--color=auto:可以将找到的关键词部分加上颜色的显示
```

#### sed

```shell
sed [option] '地址定位 sed命令' filename
使用变量时用双引号
option:
-e多项编辑
-n取消默认的输出
-f指定sed脚本的文件名
-r使用扩展正则
-i修改源文件
-i.bak备份原文件并修改源文件

地址定位
1   定位第一行
3，5   定位3到5行
$   最后一行
!   反向选择
/key/   匹配/key/中的内容（可以使用正则）
/key1/,/key2/   两个关键词之间的行
/key1\|key2/   包含关键词1或关键词2的行
/key/,n   关键词到n行之间
/key/,+4   关键词后的4行
/key/,~3   关键词到3的倍数行
n,m!   不包含n~m之间的行
1~2   奇数行
0~2   偶数行
如果没有定位，则代表每一行

sed命令
p   打印行
=   打印行号（类似p，与p不兼容）
d   删除行
i   定位的行之前添加要添加的内容
a   定位的行之后添加要添加的内容
c   将定位到的内容全部替换为新的字符
r   从文件中读取输入行
w   将所选的行写入文件
s   用一个字符串替换另一个
g   在行内进行全局替换
&   保存字符的内容在替换串中引用
y   字符一比一替换
q   退出

详细举例
i   定位的行之前添加要添加的内容
a   定位的行之后添加要添加的内容
例如：
sed  '1,3a\
lxw\
huanhang' /etc/passwd
输出
root:x:0:0:root:/root:/bin/bash
lxw
huanhang
bin:x:1:1:bin:/bin:/sbin/nologin
lxw
huanhang
daemon:x:2:2:daemon:/sbin:/sbin/nologin
lxw
huanhang
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin

c   将定位到的内容全部替换为新的字符
例如：
sed '1,3cweirun' /etc/passwd
输出
weirun
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
前三行替换为1行

r   从文件中读取输入行
w   将所选的行写入文件
例如
sed '3r /etc/hosts' /etc/passwd|head -n 7
3这个定位是passwd这个文件的   r的读取对象是hosts这个文件
读取hosts的内容放到passwd的第三行之后
执行结果如下
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin

sed '1,3w ./a.txt' /etc/passwd
把passwd的第一到三行写入当前目录下的a.txt中
会产生实际操作

s   用一个字符串替换另一个
g   在行内进行全局替换(没有g则是匹配到的行的第一个)
&   保存字符的内容在替换串中引用
例如
sed -n 's/root/#&/gp' /etc/passwd
把root替换为#root
```

#### awk

```shell
awk [option] '地址定位 awk命令' file
引用变量时是""
option:
-F   定义字段分割符号，默认空格
-v   定义变量并赋值
-f   从指定文件获取程序

内置变量:
$0   当前行的所有记录
$1……$n   当前行每列的记录
NF   当前行的列数
$NF   最后一列
$NF-1   倒数第二列
FNR/NR   行号
FS   定义源的分隔符，默认空格
OFS   定义输出的分隔符，默认空格
RS   定义源的分割符，默认换行
ORS   定义输出的分割符，默认换行
FILENAME   当前的源文件

地址定位:
/key/   匹配到关键词的行
/key1/,/key2/   匹配到关键词1和关键词2之间的行
NR==1   第一行
NR==2,NR==5   第一到五行

可以使用运算符来增强定位能力
==   等于
!=   不等于
>   大于
<   小于
>=   大于等于
<=   小于等于
~   匹配
!~   不匹配
!   逻辑非
&&   逻辑与
||   逻辑或

awk命令:
用'{}'把awk语句包起来，每条语句用';'隔开
BEGIN{awk语句};{awk语句};{awk语句;awk语句};END{awk语句}
如果需要用BEGIN，那一定是每个awk语句的开始，甚至要优先于地址定位
同时BEGIN也是不匹配行号的，先进行awk语句的运行

awk语句:
print   打印某项内容
printf   定义输出格式

awk函数:
length()   字符数量
可以用来统计    
awk'{ nc = nc + length($0) + 1 nw = nw + NF}END { print NR, "lines,", nw, "words,", nc, "characters" }'

例如：
用BEGIN定义文件的格式
awk 'BEGIN{FS=":";OFS="\t";ORS="###\n###"};/\/bin\/bash$/{print $1,$NF}' /etc/passwd
root    /bin/bash###
###lxw     /bin/bash###
###

打印匹配关键字的行
awk -F: '/^root/ || /^lp/{print $0}' /etc/passwd
awk -F: '/^root/;/^lp/{print $0}' /etc/passwd     等效
root:x:0:0:root:/root:/bin/bash
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin

awk 'NR>=30 && NR<=39 && $0 ~ /bash$/{print $0}' /etc/passwd 
$0 ~ /bash$/等效于/bash$/等效于$NF ~ /bash/

变量使用
源文件
a
b
c
d
e

awk '{ names = names $1 " "}END { print names }' 1.txt
a b c d e
```

#### cut

```shell
cut  [option]  [file]
# 字符截取
-c   : 截取第几个字符，可以是范围
-d   : 定义分割符默认为\t
-f   : 截取列
```

#### sort

```shell
sort  [option]  [file]
# 排序
-u  ：去除重复行
-r   ： 降序排列
-o   ：将排序的结果输出到文件中
-n   ：以数字排序，默认字符排序
-t   ：分隔符
-k   ：第n列
-b   ：忽略前导空格
-R   ：随机排序
```

#### uniq

```shell
uniq  [option]  [file]
# 去除重复行
-i   ：忽略大小写
-c   ：统计重复行次数
-d   ：只显示重复行
```

#### tee

```shell
tee  [option]  [file]
# 输出重定向
-a   ：以追加的方式重定向
```

#### tr

```
tr "old" "new"
字符转换
```

#### wc

```shell
wc
-l   行数
-c   字符
-w   单词数
```

#### paste

```shell
paste
#合并文件行
-d   ：自定义间隔符
-s   ：串行处理，非并行
```

#### diff

```shell
diff  [option]  [file1] [file2]
#文件内容比对
-b   ：不检查空格
-B   ：不检查空行
-i    ：不检查大小写
-w  ：忽略所有的空格
--normal   ：正常格式显示（默认）
-c   ：上下文格式显示
-u   ：合并格式显示
diff -uN file1 file2 > file.patch
patch file1 file.patch
```

#### printf

```shell
printf "text%[标志][宽度][.精度][数据类型]text" text

%   表示此处是一个受到定义其格式的字符

标识
+   表示为正数
-   表示左对齐输出
#   使用替代格式输出，格式取决于数据类型，八进制+0；十六进制+0x
''   为正数生成一个前导空格符

宽度
指定一个字段的最小宽度（定下限）

精度
保留小数点后的位数
在字符串中限制字符串的长度（定上限）

数据类型
d  格式化为有符号的十进制数
f   格式化为浮点数
o  格式化为八进制数
s   格式化字符串
x   格式化为16进制数（小写字母）
X   格式化为16进制数（大写字母）
%  普通

一些示例：
380    "%d"    380
380    "%#x"    0x17c
380    "%05d"    00380
380    "%05.5f"    380.00000
380    "%010.5f"    0380.00000
380    "%+d"    +380
380    "%-d"                 380
abcdefg    "%5s"    abcdefg
abcdefg    "%.5s"    abcde
3.1415926    "%15.3f"    3.142
```

### 文件处理类

#### ls

```shell
ls # 列出目录
-l # 详细信息
-h # 高可读
-t # 按建立时间
-a # 显示隐藏
--hide=PATTERN # 隐藏
-F # *为可执行文件,/为目录
--full-time # 完整实际格式相当于--time-style=full-iso
--time-style="+%Y-%m-%d %H:%M" # 定制时间显示格式
alias ll='ls -alhF --time-style="+%Y-%m-%d %H:%M"'
```



#### basename

```shell
basename # 取出名字
```

#### dirname

```shell
dirname # 取出目录名
```

#### find

```shell
find (dir) [option]=[value]
# 文件查找
option:
-name   名字    可用*作为通配符
-type   类型f、d
-mtime   修改日期   +3（3天之前） -3（3天之内）
-exec    扩展外部指令如rm -rf
    find /var/log -name "*.log" -mtime +10 -exec rm -rf {} \;
-size   文件大小  +5M(大于5m) -5m（小于5m）
```

#### rsync

```shell
rsync
文件同步复制
-a   归档，保留原有属性
-v   详细模式输出
-r   递归
--delete   不传相同
-l   保留软链
-p   保留权限
-t   保留修改时间
-g   保留组
-o   保留主
-D   等于--devices  --specials    表示支持b,c,s,p类型的文件
-R   保留相对路径
-H   保留硬链接
-A    保留ACL策略
-e    指定执行的shell命令
-E   保留可执行权限
-X   保留扩展属性信息

--daemon    服务模式
echo '
[replication]
path=/mysqld/data
log file=/var/log/rsync.log
'  >> /etc/rsyncd.conf
rsync -av $user@$IP::replication /mysqld_bak/data
```

#### scp

```shell
scp [option] root@$IP:/root/1.txt ./
前 >> 后
-r   递归（文件夹）
-P   端口
```

### 监控类

#### uptime

```shell
uptime # top的第一行
```

#### w

```shell
w #uptime的详细情况+用户登陆信息
```

#### who

```shell
who #用户登陆信息
```

#### whoami

```shell
whoami #用户登陆信息(简)
```

#### netstat

```shell
netstat
-t   tcp/udp
-n   端口
-l   状态
-p   pid和进程名
```

#### vmstat

```shell
vmstat
5 # 间隔5s采样一次
-t # 显示时间
-w # 提高可视性
-d # 磁盘状态
-D # 磁盘总信息
-s # 纵向展示
# procs中的r是等待b是休眠
```

#### iostat

```shell
iostat
-x # 详细信息
-d # 显示磁盘
-k # kb
-m # mb
-t # 间隔时间
-p # 磁盘分区情况
rrqm/s # 每秒读请求
wrqm/s # 每秒写请求
r/s和w/s # 每秒读写请求数
avgrq-sz # 请求扇区数
avgqu-sz # 在设备队列中等待的请求数
await # 每个IO请求花费的时间
svctm # 实际请求服务的时间
%util # 至少有一个活跃请求所占的时间百分比
tps # 每秒IO请求数
Blk_read/s # 每秒读取的block数.
Blk_wrtn/s # 每秒写入的block数.
Blk_read # 读入的block总数.
Blk_wrtn # 写入的block总数
```

#### dstat

```shell
dstat
-c # cpu
-d # disk
-g # 分页统计
-i # interrupt
-l # load-avvg
-m # memory-usage
-n # network
-p # process runnable可运行态 uninterruptible等待态 new新进程
-r # io
-s # swap
-t # time
-y # system int中断 csw上下文
```

#### pidstat

```shell
pidstat
-u # 默认的参数
-r # 显示内存
-d # IO
-p # 指定PID
-w # 上下文切换
-t # 显示选择任务的线程的统计信息外的额外信息
-l # 显示命令名和所有参数
```

#### top

```shell
top
```

#### htop

```shell
htop
```

#### mpstat

```shell
nmstat -P all 1
```

#### ps

```shell
ps
-e # all
-f # 格式化输出
-o # 自定义输出项 pid,pcpu,pmem,stat,cmd
--sort= # 排序
```

#### strace

```shell
strace # 跟踪程序执行过程中产生的系统调用及接收到的信号，帮助分析程序或命令执行中遇到的异常情况。
-c # 统计某文件或进程的的系统调用情况
-o # 重定向到文件
-T # 显示系统调用的时间-t秒、-tt毫秒、-ttt微秒
-p # 追踪具体的进程
```

#### lsof

列出当前系统打开文件的工具

```shell
lsof /boot # 查看文件系统堵塞
lsof -i：3306 # 查看端口被那个进程占用
lsof -u lxw # 查看用户打开的进程
lsof -p ${pid} # 查看进程打开哪些文件
lsof -i @150.158.93.164 # 查看远程已打开的网络链接
```

#### inotifywait

```shell
inotifywait
#监控目录
-m   #监控改变
-r    #递归
q    #获取操作信息
-e   #定义需要监控的行为

#示例：
inotifywait -mrq -e modify,delete,create,attrib,move /mysqld/data | while read events
do
    rsync -av --delete /mysqld/data/ root@10.1.1.100:/mysqld_bak/data
    echo "`date +%F\ %T`出现事件$events" >> /var/log/rsync.log 2>&1
done
```

#### history

```shell
history
-c    # 清除
history详细模式
echo 'export HISTTIMEFORMAT="%F %T `whoami`" ' >> /etc/bashrc
```

#### getconf

```shell
getconf
-a   # 获取系统所有信息
LONG_BIT   # 查看系统位数
PAGE_SIZE   # 查看系统分页大小
```



### 网络管理

#### ip

```shell
ip [option]
address   当前网卡信息
ip route   路由信息，可+add、del
```

#### ifconfig

```shell
ifconfig
-a 全显示
-s 摘要
```

网卡启动关闭

```shell
ifconfig interface_name 
up #启动
down #关闭
```

添加IP地址

```shell
ifconfig ens33:0 192.168.51.23 netmask 255.255.255.0 up
ifconfig ens33:1 192.168.51.24 netmask 255.255.255.0 up
```

删除IP地址

```shell
ifconfig ens33 del 192.168.51.23 
```

启用或关闭ARP协议

```shell
ifconfig ens33 arp
ifconfig ens33 -arp
```

修改MAC地址

```shell
ifconfig eth0 hw ether 00:AA:BB:CC:DD:EE
```

设置MTU

```shell
ifconfig eth0 mtu 1500
```

#### netplan

```shell
cat <<EOF >/etc/netplan/00-installer-config.yaml
network:
  ethernets:
    ens33:
      addresses:
      - 192.168.1.121/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
        - 119.29.29.29
        - 223.5.5.5
        search: []
  version: 2
EOF
```

### 进程类

#### nohup

```shell
nohup command &
强制运行不挂起，即使终端推出
&   后台运行
```

#### kill

```shell
kill [-s signal] [process]
-1     -HUP      重新加载
-9     -KILL       杀死
-15   -TERM    正常停止
```

#### at

```shell
at
#一次性任务
atq   #查看没执行的任务
atrm   #根据任务号删除任务
#添加一次性任务
at 01am+3 days
at > /bin/ls > /root/readme.txt
at > ctrl+D 结束
```

#### crontab

```shell
crontab
# 定时任务
-l   查询当前计划
-e   编辑计划
# 分 时 日 月 周 执行的命令（要求使用完整路径,which命令）
```

### 安全类

#### 用户权限

```shell
chmod #权限
chown #用户
-r   递归

chage [option] $user #账号管理
-l    详细修改
-d    指定最后一次修改日期的期限
-m   修改密码的最短保留天数
-M   密码有效期
-w    到期前警告天数
-i    过期后的宽限天数
-E    修改失效的日期 yyyy-mm-dd

# 用户管理
useradd  usermod
-s   指定权限  /sbin/nologin或/bin/bash
-u    uid
-g    gid
-G   附属组
-d   家目录的位置
-r    指定为系统用户

userdel
-r   同时删除/home/$user
-f   强制

# 组管理
gpasswd [option] $group
-a   添加
-M    批量添加
-d    删除
-A    指定管理员

groupadd [option] $user
-g    指定组的gid

groupmod
-g   指定组的gid
-n    修改名字
```

#### passwd

```shell
passwd
--stdin   读取标准输入
示例：echo "123456"|passwd --stdin root
```

#### acl

```shell
getfacl
# 查询acl权限
setfacl
# 设置acl权限
-m   设置修改
-R   递归
-x    去除某用户或组的权限
-b   删除所有ACL
-d    默认ACL策略，只针对目录
示例
setfacl -m u:lxw:rw readme.txt
```

#### ssh

```shell
# 远程
ssh
-X # X11
-Y # X11(安全)
-i # 指定私钥的位置

#免密登陆密钥生成
ssh-keygen -P "" -f /$user/.ssh/id_rsa
-P # 密钥
-f # 指定文件位置名称
-t # 指定类型，默认rsa
-b # bit，默认长度2048
ssh-copy-id ${user}@${host}
# 会将ssh-keygen生成的rsa公钥发送到、${user}/.ssh/authorized_keys中
# 远程复制
scp [option] root@$IP:/root/1.txt ./
前 >> 后
-r   递归（文件夹）
-P   端口
```

#### pwgen

```shell
pwgen
# 生成密码
-c   至少1个大写字母
-A   不包含大写字母
-n   至少一个数字
-0   不包含数字
-y   至少包含一个特殊符号
-s   完全随机
-B   不生成歧义字符
-C    在列中打印生成的密码
-1   一行一个密码
-v   不使用元音
```

#### firewall-cmd

```shell
firewall-cmd
--get-default-zone    #默认的运行区域
firewall-cmd --get-zones    #所有支持的区域
firewall-cmd --list-all     #当前区域的策略
firewall-cmd --list-all-zones   #所有区域的策略
firewall-cmd --zone=public --add-port=端口号/tcp  --permanent   添#加端口进防火墙策略中
firewall-cmd --reload   #热重载
```

#### iptables

保存规则

```shell
iptables-save > /etc/sysconfig/iptables
```

载入规则

```shell
iptables-restore < /etc/sysconfig/iptables
```

删除规则

```shell
iptables -F
```

表

iptables表↓
filter 过滤
nat 地址转换
mangle 数据包重新封装，设置标记
raw 确定是否对数据包进行跟踪
security 是否定义强制访问控制规则；后加上的

| 表        | 功能                |
| -------- | ----------------- |
| filter   | 过滤                |
| nat      | 地址转换              |
| mangle   | 数据包重新封装，设置标记      |
| raw      | 确定是否对数据包进行跟踪      |
| security | 是否定义强制访问控制规则；后加上的 |

链

| 链           | 意义      |
| ----------- | ------- |
| input       | 数据包接受   |
| prerouting  | 路由转发前   |
| forward     | 路由转发    |
| postrouting | 路由转发后   |
| output      | 数据包输出输出 |

优先级raw->mangle->nat->filter

基本条件

| 基本匹配选项 | 功能          |
| ------ | ----------- |
| -p     | 指定规则协议tcp   |
| -s     | 指定数据包的源地址ip |
| -d     | 指定目的地址      |
| -i     | 输入接口        |
| -o     | 输出接口        |
| !      | 取反          |

​    无需扩展模块就可以生效

隐式匹配

-p tcp

| 隐式匹配选项      | 功能                            |
| ----------- | ----------------------------- |
| --sport     | 匹配报文源端口；可以给出多个端口，但只能是连续的端口范围  |
| --dport     | 匹配报文目标端口；可以给出多个端口，但只能是连续的端口范围 |
| --tcp-flags | mask comp 匹配报文中的tcp协议的标志位     |

-p udp

| 隐式匹配选项  | 功能                            |
| ------- | ----------------------------- |
| --sport | 匹配报文源端口；可以给出多个端口，但只能是连续的端口范围  |
| --dport | 匹配报文目标端口；可以给出多个端口，但只能是连续的端口范围 |

--icmp-type

| 隐式匹配选项 | 功能                      |
| ------ | ----------------------- |
| 0/0    | echo reply 允许其他主机ping   |
| 8/0    | echo request 允许ping其他主机 |

```shell
显式匹配使用选项及功能↓
multiport
iptables -I INPUT -d 192.168.2.10 -p tcp -m multiport --dports 22,80 -j ACCEPT
#在INPUT链中开放本机tcp 22，tcp80端口
iptables -I OUTPUT -s 192.168.2.10 -p tcp -m multiport --sports 22,80 -j ACCEPT
#在OUTPUT链中开发源端口tcp 22，tcp80

iprange
iptables -A INPUT -d 192.168.2.10 -p tcp --dport 23 -m iprange --src-range
192.168.2.11-192.168.2.21 -j ACCEPT
iptables -A OUTPUT -s 192.168.2.10 -p tcp --sport 23 -m iprange --dst-range
192.168.2.11-192.168.2.21 -j ACCEPT

time
iptables -A INPUT -d 192.168.2.10 -p tcp --dport 901 -m time --weekdays
Mon,Tus,Wed,Thu,Fri --timestart 08:00:00 --time-stop 18:00:00 -j ACCEPT
iptables -A OUTPUT -s 192.168.2.10 -p tcp --sport 901 -j ACCEPT

string
--algo {bm|kmp}：字符匹配查找时使用算法
--string "STRING": 要查找的字符串
--hex-string “HEX-STRING”: 要查找的字符，先编码成16进制格式

connlimit
--connlimit-upto n 连接数小于等于n时匹配
--connlimit-above n 连接数大于n时匹配

limit

state
追踪本机上的请求和响应之间的数据报文的状态。
--state state
NEW 新连接请求
ESTABLISHED 已建立的连接
INVALID 无法识别的连接
RELATED 相关联的连接，当前连接是一个新请求，但附属于某个已存在的连接
UNTRACKED 未追踪的连接
```

iptables动作target

| target     | 意义                                        |
| ---------- | ----------------------------------------- |
| ACCEPT     | 允许                                        |
| DROP       | 丢弃，不回应                                    |
| REJECT     | 拒绝，发送回应信息                                 |
| SNAT       | 源地址转换                                     |
| MASQUERADE | 伪装，动态的（发送数据的网卡上的IP）替换IP地址                 |
| DNAT       | 目标地址转换                                    |
| REDIRECT   | 在本机做端口映射                                  |
| LOG        | 在/var/log/message文件中记录日志信息，然后将数据包传递给下一条规则 |

```shell
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o eth1 -j SNAT --to-source 202.12.10.100
iptables -t nat -A PREROUTING -d 202.12.10.100 -p tcp --dport 80 -j DNAT --to-destination 192.168.10.1
# DNAT在PREROUTING链上SNAT在POSTROUTING链上进行
```

语法

```shell
iptables -t table_name command1 manage_chain chain_name condition1 condition2 modules target
```

```shell
-t    选择表 table_name=filter|nat|mangle|raw

command1
    -A --append chain rule-specification：追加新规则于指定链的尾部；
    -D --delete chain rulenum：根据规则编号删除规则；
    -D --delete chain rule-specification：根据规则本身删除规则；
    -L --list [chain]：列出规则；
    -F 清空规则
    -P 设置链的默认规则
    -I  --insert chain [rulenum] rule-specification：插入新规则于指定链的指定位置，默认为首部；
    -R--replace chain rulenum rule-specification：替换指定的规则为新的规则；
    -n --numeric：数字格式显示主机地址和端口号；
    -x --exact：显示计数器的精确值，而非圆整后的数据；
    --line-numbers：列出规则时，显示其在链上的相应的编号；
    -S, --list-rules [chain]：显示指定链的所有规则；

manage_chain # 用不上
    -N, --new-chain chain：新建一个自定义的规则链；
    -X, --delete-chain [chain]：删除用户自定义的引用计数为0的空链；
    -F, --flush [chain]：清空指定的规则链上的规则；
    -E, --rename-chain old-chain new-chain：重命名链；
    -Z, --zero [chain [rulenum]]：置零计数器；
        注意：每个规则都有两个计数器
        packets：被本规则所匹配到的所有报文的个数；
        bytes：被本规则所匹配到的所有报文的大小之和；
    -P, --policy chain target 制定链表的策略(ACCEPT|DROP|REJECT)

chain_name    INPUT|FORWARD|OUTPUT|PREROUTING|POSROUTING # 选择在链的位置启用规则

condition # 指定条件，可以写多个条件
    -p    指定协议tcp|udp
        -s    源地址
        -d    目标地址
        --sport    源端口
        --dport    目标端口
        --dports    multiport
    -i    --in-interface指定的设备名
    -o    --out-interface指定的设备名

modules # 指定模块
    -m modules_name    启用modules tcp|state|multiport

target #指定对数据包进行的操作
    -j    ACCEPT|DROP|REJECT|DNAT|SNAT
```

案例

```shell
案例1：
放行某源地址访问目标端口
iptables -t filter -I INPUT -p tcp -s 192.168.51.52 --dport=80 -j ACCEPT
放行本机源地址访问本机目标端口
iptables -I INPUT -d 127.0.0.1 -p tcp --dport=9000 -i lo -j ACCEPT
允许通过本地回环网卡访问本机
iptables -I INPUT -i lo -j ACCEPT
允许已建立的继续链接(针对能进不能出的情况)
iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

案例2:
FTP无法访问
解决方法1：
[root@localhost ~]# iptables -I INPUT -p tcp --dport 20:21 -j ACCEPT
[root@localhost ~]# vim /etc/vsftpd/vsftpd.conf
pasv_min_port=50000
pasv_max_port=60000
[root@localhost ~]# iptables -I INPUT -p tcp --dport 50000:60000 -j ACCEPT
解决方法2：使用连接追踪模块
[root@localhost ~]# iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
[root@localhost ~]# iptables -I INPUT -p tcp --dport 20:21 -j ACCEPT
[root@localhost ~]# modprobe nf_conntrack_ftp #临时方法,添加连接追踪模块
[root@localhost ~]# vim /etc/sysconfig/iptables-config
IPTABLES_MODULES="nf_conntrack_ftp"
#启动服务时加载
#针对数据端口连接时，nf_conntrack_ftp将三次握手第一次状态由NEW识别为RELATED

案例3:
iptables标准流程
iptables -F
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -s 192.168.2.0/24 -j ACCEPT #允许内网任何访问
iptables -A INPUT -p tcp --syn --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --syn --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --syn --dport 21 -j ACCEPT
iptables -A INPUT -j REJECT
modprobe nf_conntrack_ftp

案例4:
允许ping回应
iptables -t filter -I INPUT -p icmp -m icmp --icmp-type echo-reply -j ACCEPT 

案例5:
iprange
iptables -t filter -I INPUT -m iprange --src-range 192.168.2.10-192.168.2.100 -j REJECT

案例6:
multiport
iptables -t filter -I INPUT -p tcp -m multiport --dports 20,21,22,25,80,110 -j ACCEPT

案例7:
#-m tos 根据ip协议头部 type of service进行过滤
[root@localhost ~]# iptables -F
[root@localhost ~]# tcpdump -i eth0 -nn port 22 -vvv
#抓取远程主机访问本机的ssh数据包，观察TOS值
[root@localhost ~]# tcpdump -i eth0 -nn port 22 -vvv
#抓取远程从本机rsync或scp复制文件，观察TOS值
#ssh: tos 0x0 0x10
#scp: tos 0x0 0x8
#rsync: tos 0x0 0x8
[root@localhost ~]# iptables -t filter -A INPUT -p tcp --dport 22 -m tos --tos 0x10 -j ACCEPT
[root@localhost ~]# iptables -t filter -A INPUT -j REJECT

案例8:
#-m tcp 按TCP控制位进行匹配
Flags:SYN ACK FIN RST URG PSH ALL NONE
[root@localhost ~]# iptables -t filter -A INPUT -p tcp -m tcp --tcp-flags
SYN,ACK,FIN,RST SYN --dport 80 -j ACCEPT
[root@localhost ~]# iptables -t filter -A INPUT -p tcp --syn --dport 80 -j ACCEPT
#--tcp-flags SYN,ACK,FIN,RST SYN 检查四个标记位，只有SYN标记位才匹配，即只允许三次握手中的第一次
握手，等价于--syn

案例9:
#-m comment 对规则进行备注说明
iptables -A INPUT -s 192.168.2.250 -m comment --comment "cloud host" -j REJECT

案例10:
#-m mark 使用mangle表的标记方法,配合mangle表使用
[root@localhost ~]# iptables -t filter -A INPUT -m mark 2 -j REJECT

案例11:
#-j LOG 记录至日志中
[root@localhost ~]# grep 'kern.*' /etc/rsyslog.conf
kern.* /var/log/kernel.log
[root@localhost ~]# systemctl restart rsyslog
[root@localhost ~]# iptables -j LOG -h
[root@localhost ~]# iptables -t filter -A INPUT -p tcp --syn --dport 22 -j LOG --logprefix " localhost_ssh "
[root@localhost ~]# iptables -t filter -A INPUT -p tcp --syn --dport 22 -j ACCEPT
[root@localhost ~]# iptables -t filter -A INPUT -j REJECT

案例12:
#-j REJECT
当访问一个未开启的TCP端口时，应该返回一个带有RST标记的数据包
当访问一个未开启的UDP端口，结果返回port xxx unreachable
当访问一个开启的TCP端口，但被防火墙REJECT，结果返回port xxx unreachable
[root@localhost ~]# iptables -j REJECT -h
[root@localhost ~]# iptables -t filter -A INPUT -p tcp --dport 22 -j REJECT --rejectwith tcp-reset //返回一个自定义消息类型

案例13:
#-j MARK 进行标记，可在LVS调度器中应用
[root@localhost ~]# iptables -t mangle -L
[root@localhost ~]# iptables -j MARK -h
[root@localhost ~]# iptables -t mangle -A PREROUTING -s 192.168.2.110 -j MARK --setmark 1
[root@localhost ~]# iptables -t mangle -A PREROUTING -s 192.168.2.25 -j MARK --setmark 2
[root@localhost ~]# iptables -t filter -A INPUT -m mark --mark 1 -j ACCEPT //按照标记匹配
[root@localhost ~]# iptables -t filter -A INPUT -m mark --mark 2 -j REJECT

案例14:
client        firewall            web
ip:192.168.1.2    ens33:192.168.1.1        ip:192.168.3.2
        ens37:192.168.3.1
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o ens37 -j SNAT --to-source 192.168.3.1
或
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o ens37 -j MASQUERADE
vim /etc/sysconfig/iptables
#-A FORWARD -j REJECT --reject-with icmp-host-prohibited
# 要注释
```

### 硬盘操作类

#### dd

```shell
dd 
块复制
if=    来源的文件可以是/dev/zero
of=   输出到那个文件
bs=   每一块的数据量
count=   一共多少块
```

#### lvm

```shell
pvcreate [disk-partition] [disk-partition]
#将硬盘划分为PE
pvs | pvdisplay [disk-partition]
#查看
vgcreate [vgname] [disk-partition] [disk-partition]
#创建PE的分组，通常PE划分到1个VG就行
vgs | vgdisplay [disk-partition]
#查看
lvcreate -n [lvname] -l [PE-number] [vgname]
-n   lv的名称
-l   PE的数量|剩余空间%，如：50%free
-L   实际大小如2.5G
#扩容
pvcreate [disk-partition] [disk-partition]
vgextend [vgname] [disk-partition] [disk-partition]
lvextend -L [size] /dev/[vgname]/[lvname]
-L size是最终大小|+size增加大小
resize2fs /dev/[vgname]/[lvname]
xfs_growfs /dev/[vgname]/[lvname]
```

#### mount

```shell
mount 
#挂载
-o   #权限 rw|ro|sync|async
#读写|只读|同步|异步
-t   #类型
mount /dev/sr0 /mnt/cdrom

#自动挂载:
echo \
'"挂载设备/dev/sdb" "挂载目录/vm" "挂载格式ext4" "挂载方式default" 0 0'\
 >> /etc/fstab
```

### 用户权限类

#### su

```shell
su user   # 切换用户环境变量不变
su - user   # 切换用户环境变量和目录改变
-c program # 指定某用户执行程序
```

#### visudo

```visudo
#user    MACHINE=(RUN_AS_USER) COMMANDS
lxw    ALL=(ALL) ALL
#用户    主机=(身份) 命令

#组 %
%wheel    ALL=(ALL) ALL

lxw    ALL=/usr/sbin/ip, /usr/sbin/fdisk, !/usr/bin/less /etc/shadow
#不能用less看shadow
lxw     ALL=(ALL)       NOPASSWD: SOFTWARE
lxw     ALL=(ALL)       SERVICES, STORAGE
可以分行写
```

#### chattr

```shell
chattr [+a|-a|+i|-i|-d]
+a   #允许追加内容，不能删除
-a   #去除+a
+i   #锁定文件内容
-i    #去除-i
#系统重要命令文件防删除、防修改
find /bin /sbin /usr/sbin /usr/bin /etc/shadow /etc/passwd /etc/pam.d -type f -exec chattr +i {} \;
#日志文件防删除
chattr +a /var/log/messages /var/log/secure
lsattr   #查看文件属性
```

### 其他类:

#### mysql-cli

```shell
mysql
-s   去除边框
-S   SOCKET
-P   端口
-p   密码
-N   不显示标题
-X   XML输出
```

#### curl

```shell
curl
# 用于查看web页面，可以用来判断web见面是否正常工作
-I   网页信息
-o   内容重定向到
-w <format>   完成后使用输出格式
-s   静默访问
--connect-timeout  定义超时时间
```

#### date

```shell
date +[option]
%F   yyyy-mm-dd
%D  mm-dd-yy
%T   hh:mm:ss
%Y   yy
%m   mm月
%d   dd
%H   hh
%h   月缩写
%M   mm分
%S   ss
%A   星期
%a   星期缩写

-s  设定时间  "yyyy-mm-dd  hh:mm:ss"
```

#### sysctl

```shell
sysctl # 配置内核参数
-w key=value # 临时设置某个值
-p file # 从文件中读取配置，默认sysctl.conf
-a # 显示所有参数
```

## 十、运行级别

```shell
0   shutdown.target
1   emergency.target
2   rescure.target
3   multi-user.target   字符模式
4   无
5   graphical.target    图形模式
6   无
```

设置默认启动的级别

```shell
systemctl set-default multi-user.target
```

修改 /etc/inittab中的参数

```shell
id:3:initdefault
```

## 十一、文件权限

rwx读、写、执行

设置位S:为了让一般使用者临时具有该文件所属主/组的执行权限

沾滞位T:只允许文件的创建者和root用户删除文件（防止误删除权限位）

d   目录
l   软连接
b    块设备
c    字符设备
s    socket
p   管道

## 十二、本地YUM源配置

```shell
cat << EOF > local.repo
[local]
name=local yum
baseurl=file://[路径]
gpgcheck=0
enabled=1
EOF
```

## 十三、正则表达式

```shell
第一类正则^$.[]*
.  :  任意单个字符，除了换行符
*  ：*之前的一个字符可以出现零次或连续多次
.*  : 这个位置可以匹配任意长度字符
^  : 行的开头
$  : 行的末尾
^$  :空行
[]  :   匹配指定字符组内的任意单个字符
[^]  ： 匹配不在指定字符组内的任意字符,仅单个
^[]  ： 匹配以指定字符组内任意字符开头，仅单个
^[^]  ： 匹配不以指定字符组内任意字符开头，仅单个
\<  ：  取单词的头（类似^但只要单词的头）
\>  ： 取单词的尾（类似$但只要单词的尾）
\<\>  ：精确匹配单词
\{n\}   ： 匹配前导字符连续n次
\{n,\}   ：匹配前导字符至少n次
\{n,m\}  ：匹配前导字符n-m次之间
\(strings\)   ：保存匹配的字符，后面用1，2，3……表示

扩展正则^$.[]*(){}?+|
+  ： 匹配一个或多个前导字符（前导字符的数量不再为1）
？  ： 匹配0个或一个前导字符
a|b  ：匹配a或b
()  ：组字符  (my|your)self
{}  :  同正则但不需要\了

第二类正则
[:alnum:]  :  字母与数字
[:alpha:]  :字母字符（包括大小写字母）
[:blank:]  : 空格与制表符
[:digit:]  ： 数字
[:lower:]  ： 小写字母
[:upper:]  ： 大写字母
[:punct:]  ： 标点符号
[:space:]  ： 包括换行符，回车在内的所有空白
通常[0-9] [a-z] [A-Z] [a-zA-Z] [a-Z]就行

英文句子 "^[A-Z][a-z]*[ [A-Za-z]*]*\."
美国电话号码"^(\?[0-9]\{3\})\? [0-9]\{3\}-[0-9]\{4\}$"
IP地址 “\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}”
```

## 十四、案例

### 检测文件夹内容改动

```shell
#!/bin/bash
# 文件目录位置
MON_DIR=/opt
# 用inotifywait检测目录
inotifywait -mrq -e modify,delete,create,attrib,move $MON_DIR |while read events
do
        echo "`date +%F\ %T` 出现事件 $events" >> /log/dirModify.txt 2>&0
done
```

### 监控主从同步

```shell
#!/bin/bash
#mysql要先完成免密登录，这一步可以使用
#     mysql_config_editor set --login-path=my3306 --user=root --socket=/tmp/mysql.sock --password
#获取slave转态可以用
#     mysql --login-path=my3306 -e 'show slave status\G'|awk 'BEGIN{FS=":"};/Slave_.*_Running:/{print $1 $2}'
#用crontab -e定时运行此脚本

#1.用数组保存获取到的值
SLAVE_STATUS=(`mysql --login-path=my3306 -e 'show slave status\G'|awk 'BEGIN{FS=":"};/Slave_.*_Running:/{print $2}'`)
connection_time=0
mysql_log_slave=/mysqld/slave.log
#2.循环，正常就直接推出，失连就记录，不超过3次
while (( $connection_time < 3 ))
do
    if [ ${SLAVE_STATUS[0]} = Yes ] && [ ${SLAVE_STATUS[1]} = Yes ];then
        echo "`date '+%F %T'` Slave is running"  >> $mysql_log_slave
        exit
    elif [ ${SLAVE_STATUS[0]} = Connecting ];then
        let connection_time=connection_time+1
        echo "`date '+%F %T'` Slave disconnection $connection_time ." >> $mysql_log_slave
        sleep 5
    else
        echo "`date '+%F %T'` Slave status is working correctly ." >> $mysql_log_slave
        exit
    fi
done
```

### 监控网卡流量

```shell
#!/bin/bash
net_name=$1
while  true
do
    net_receive_old=`grep "$net_name" /proc/net/dev |awk '{print $2}'`
    net_send_old=`grep "$net_name" /proc/net/dev |awk '{print $10}'`
    sleep 1
    net_receive_new=`grep "$net_name" /proc/net/dev |awk '{print $2}'`
    net_send_new=`grep "$net_name" /proc/net/dev |awk '{print $10}'`
    in_stream=$(printf "%.1f%s"  "$((($net_receive_new-$net_receive_old)/1024))"  "KB/S")
    out_stream=$(printf "%.1f%s"  "$((($net_send_new-$net_send_old)/1024))"  "KB/S")
    clear
    echo "stream   status"
    echo -e "进流量   $in_stream\n出流量   $out_stream"
    sleep 1
done
```

### 查看进程CPU或MEM的占用排行

```shell
#!/bin/bash
read -p "请输入c|cpu or m|mem|memory:  " ps_sort_format
case $ps_sort_format in
    m|mem|memory)
        echo "....................................memory top10......................................."
        ps -eo pid,pcpu,pmem,stat,cmd --sort=pmem |tail -n10|sort -nr -k2
        ;;
    c|cpu)
        echo "......................................cpu top10........................................."
        ps -eo pid,pcpu,pmem,stat,cmd --sort=pcpu |tail -n10|sort -nr -k2
        ;;
    *)
        echo "please input c|cpu or m|mem|memory"
        ;;
esac
```

### 检测网页质量

```shell
#!bin/bash
#使用curl获取状态码  200正常
#例如:curl -s -o /dev/null --connect-timeout 3 -w "%{http_code}" http://www.baidu.com
# httplist.txt 存放需要检测的网址
cat httplist.txt | while read URL_LIST
do
    URL_FAIL=0
    for (( i=1;i<=3;i++))
    do
        HTTP_CODE=curl -s -o /dev/null --connect-timeout 3 -w "%{http_code}" $URL_LIST
        if [ $HTTP_CODE -eq 200 ];then
            echo "$URL_LIST is ok."
            break
        else
            let URL_FAIL++
        fi
    done
    if [ URL_FAIL -eq 3 ];then
        echo "$URL_LIST is failure"
    fi
done
```

### 批量创建用户

```shell
#!/bin/bash
#创建用户
cat user.txt|while read USER
do
    if ! id $USER &>/dev/null; then
        passwd_value=`echo $RANDOM | md5sum | cut -c 1-8`
        useradd $USER
        echo $passwd_value | passwd --stdin $USER
        echo "$USER    $passwd_value"  >>created_user.txt
        echo "$USER create successful"
    else
        echo "$USER already exists"
    fi
done
```

### 获取IP地址

```shell
ifconfig | grep -A1 "flags"| awk '/flags/{print $1};/inet/{print $2}'
```

### 获取服务器资源

```shell
#!/bin/bash
#CPU
function cpu(){
    util=$(vmstat|awk '{if(NR==3)print $13+$14}')
    iowait=$(vmstat|awk '{if(NR==3)print $16}')
    echo "CPU-使用率：${util}%,等待磁盘IO响应使用率：${iowait}%"
}
#内存
function memory(){
    total=$(free -m |awk '{if(NR==2)printf "%.1f", $2/1024}')
    used=$(free -m |awk '{if(NR==2)printf "%.1f",( $2-$NF)/1024}')
    available=$(free -m |awk '{if(NR==2)printf "%.1f", $NF/1024}')
    echo  "内存 - 总大小：${total}G,已使用：${used}G,剩余：${available}G"
}
#磁盘
disk(){
    fs=$(df -h |awk '/^\/dev/{print $1}')
    for p in $fs;do
        disk_mounted=$(df -h|awk -v p=$p '$1==p{print $NF}')
        disk_size=$(df -h |awk -v p=$p '$1==p{print $2}')
        disk_used=$(df -h |awk -v p=$p '$1==p{print $3}')
        disk_used_percent=$(df -h |awk -v p=$p '$1==p{print $5}')
        echo "硬盘-挂载点：$disk_mounted,总大小：$disk_size,已使用：$disk_used,使用率：$disk_used_percent"
done
}
tcp_status(){
    tcp_summary=$(netstat -antp|awk '{a[$6]++}END{for(i in a)printf i":"a[i]" "}')
    echo "TCP连接状态-$tcp_summary"
}
cpu
memory
disk
tcp_status
```

### nginx access log 统计

```shell
#!/bin/bash
#提取IP前十
echo "-----IP访问最多前十-----"
awk 'BEGIN{FS="|"};{print $1}' /usr/local/nginx/logs/access.log |sort |uniq -c|sort -nr -k 1|head -n 10
#另一种awk 'BEGIN{FS="|"};{a[$1]++}END{for (v in a)print v,a[v]}' /usr/local/nginx/logs/access.log

echo "-----访问最多的页面前十-----"
awk 'BEGIN{FS="|"};{print $5}' /usr/local/nginx/logs/access.log |awk '{print $1"\t"$2}'|sort -k1|uniq -c|sort -nr|head -n 10

echo "-----访问最多状态码前十-----"
awk 'BEGIN{FS="|"};{print $6}' /usr/local/nginx/logs/access.log |sort |uniq -c |sort -nr|head -n 10
#另一种awk 'BEGIN{FS="|"};{a[$6]++;}END{for (v in a)print v,a[v]}' /usr/local/nginx/logs/access.log|sort -nr -k2

###一定期间的统计###
$BEGIN_TIME='17-Feb-2022:15:00:00'
$END_TIME='17-Feb-2022:17:00:00'
awk 'BEGIN{FS="|"};{print $1"\t"$3}' /usr/local/nginx/logs/access.log |sed 's/\//-/g'|awk '$2>="$BEGIN_TIME" && $2<="$END_TIME"{print $1}'|sort|uniq -c
#时间一定要放入awk中，不能使用变量
#最终版
BEGIN_TIME='17022022170000'
END_TIME='17022022180000'
awk 'BEGIN{FS="|"};{print $1"\t"$3}' /usr/local/nginx/logs/access.log |sed 's/\//-/g'|sed 's#:#-#g'|sed 's#Feb#02#g'|awk '{print $1"\t"$2}'|sed 's/-//g'|awk -v BEGIN_TIME=$BEGIN_TIME 'BEGIN_TIME<=$2{print $0}'|awk -v END_TIME=$END_TIME 'END_TIME>$2{print $1}'|sort |uniq -c|sort -nr
```

### nginx 日志切割

```shell
#!/bin/bash
#定义日志的基本目录
LOG_DIR=/usr/local/nginx/logs
#定义文件的基本名字
LOG_FILE_BASENAME=access.log
#按月份定义目录
LOG_MONTH_DIR=$LOG_DIR/$(date -d "yesterday" +"%Y-%m")
#定义昨天
YESTERDAY_TIME=$(date -d "yesterday" +%F)
for LOG_FILE in LOG_FILE_BASENAME;do
    [ ! -d $LOG_MONTH_DIR ] && mkdir -p $LOG_MONTH_DIR
    mv $LOG_DIR/$LOG_FILE_BASENAME $LOG_MONTH_DIR/${LOG_FILE_BASENAME}_${YESTERDAY_TIME}
done
kill -USR1 $(cat /usr/local/nginx/logs/nginx.pid)
```

### 发送公钥(root用户)

```shell
#!/bin/bash
[ -f /root/.ssh/id_rsa ] || ssh-keygen -P "" -f /root/.ssh/id_rsa
# 从文件中获取hostIP port user password
cat SSHList.txt|while read SERVER_IP SSHD_PORT LOGIN_NAME SSH_PASSWD
do
    ping -c1 $SERVER_IP
    if [ $? -eq 0 ];then
        touch /root/ssh_up.txt
        /usr/bin/expect <<-END
        spawn ssh-copy-id -p $SSHD_PORT $LOGIN_NAME@$SERVER_IP
        expect { 
            "yes/no" { send "yes\r";exp_continue }
            "password:" { send "$SSH_PASSWD\r" }
        }
        expect eof
        END
        echo "$(date +%F) 完成向 $SERVER_IP 发送公钥" >> /root/ssh_up.txt
    else
        touch /root/ssh_down.txt
        echo "$(date +%F) $SERVER_IP 无法连接" >> /root/ssh_down.txt
    fi
done
cat /root/ssh_up.txt /root/ssh_down.txt
```

## 十五、遇到的问题

### 1. apt 一直waiting for headers

因为是虚拟机，有另外的数据包再分装，所以MTU不能设置太大

解决办法

```shell
sudo ip link set mtu 1480 eth0
```

## 十六、性能优化

### 1./etc/security/limits.conf

PAM针对会话的的资源限制

`/etc/security/limits.d/`下的相同用户配置会覆盖`/etc/security/limits.conf`里的内容

```shell
<domain>      <type>  <item>         <value>
domain # 可以是用户user_name、用户组@group_name、*所有
type # soft警告，hard最大值
item # 限制的具体项目{
    core # 内核文件大小
    data # 最大数据大小
    fsize # 最大文件大小
    memlock # 最大锁定内存地址空间
    nofile # 最大文件打开数
    rss # 最大持久设置大小
    stack # 最大栈大小
    cpu # 最多cpu占用时间
    nproc # 进程最大数目
    as # 地址空间限制
    maxlogins # 此用户允许的最大登录数量
    priority # 运行用户进程的优先级
    locks # 用户持有的文件锁的最大数量
    sigpending # pending信号最大数量
    msgqueue # 消息队列最大可使用内存bytes
    nice # 允许的最高优先级
    rtprio # 实时优先级
}
value # 值{
    最好只有nproc才可以设置unlimited
}
```

`/etc/sysctl.conf`

```shell
net.ipv4.tcp_syn_retries = 1 # 一个新建连接，要发送多少个SYN请求才放弃
net.ipv4.tcp_synack_retries = 1 # 三次握手的第二步，要发送多少次SYN+ACK才放弃
net.ipv4.tcp_keepalive_time = 600 # 发送keepalive包前等待的时间，用于确认TCP连接是否有效，防止建立连接但不发送数据
net.ipv4.tcp_keepalive_probes = 3 # 发送keepalive次数，用于确认TCP连接是否有效
net.ipv4.tcp_keepalive_intvl =15 # keepalive包每次的发送的间隔
# net.ipv4.tcp_retries1 = 3 # 放弃回应一个TCP连接请求前﹐需要进行多少次重试，规定最低为3
net.ipv4.tcp_retries2 = 5 # 在丢弃激活(已建立通讯状况)的TCP连接之前﹐需要进行多少次重试
net.ipv4.tcp_orphan_retries = 3 # 在近端丢弃TCP连接之前﹐要进行多少次重试。
net.ipv4.tcp_fin_timeout = 2 # 对于本端断开的socket连接，TCP保持在FIN-WAIT-2状态的时间。
net.ipv4.tcp_max_tw_buckets = 36000 # 系统在同时所处理的最大 timewait sockets 数目 如果超过此数的话﹐time-wait socket 会被立即砍除并且显示警告信息
net.ipv4.tcp_tw_recycle = 1 # 打开快速 TIME-WAIT sockets 回收。除非得到技术专家的建议或要求﹐请不要随意修改这个值。(做NAT的时候，建议打开它)
net.ipv4.tcp_tw_reuse = 1 # 表示是否允许重新应用处于TIME-WAIT状态的socket用于新的TCP连接
# net.ipv4.tcp_max_orphans = 32768 # 系统所能处理不属于任何进程的TCP sockets最大数量。
# net.ipv4.tcp_abort_on_overflow = 0 # 当守护进程太忙而不能接受新的连接，就象对方发送reset消息，默认值是false。
net.ipv4.tcp_syncookies = 1 # 内核编译时选择了CONFIG_SYNCOOKIES时才会发生作用。当出现syn等候队列出现溢出时象对方发送syncookies。目的是为了防止syn flood攻击。
net.ipv4.tcp_max_syn_backlog = 16384 # 对于那些依然还未获得客户端确认的连接请求﹐需要保存在队列中最大数目。
net.ipv4.tcp_wmem = 8192 131072 16777216 # 发送缓冲的内存最小值|默认值|最大值
net.ipv4.tcp_rmem = 32768 131072 16777216 # 接受缓存
net.ipv4.tcp_mem = 786432 1048576 1572864 # 释放内存三个界值
net.ipv4.ip_local_port_range = 1024 65000 # 表示用于向外连接的端口范围
net.ipv4.ip_conntrack_max = 65536 # 系统支持的最大ipv4连接数，默认65536（事实上这也是理论最大值）
net.ipv4.netfilter.ip_conntrack_max=65536 # 防火墙的最大ipv4连接数
net.ipv4.netfilter.ip_conntrack_tcp_timeout_established=180 # 已建立的tcp连接的超时时间，默认432000，也就是5天
net.core.somaxconn = 16384 # 用来限制监听(LISTEN)队列最大数据包的数量，超过这个数量就会导致链接超时或者触发重传机制。
net.core.netdev_max_backlog = 16384 # 每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目，对重负载服务器而言，该值需要调高一点
vm.swappiness=10 # 使用SWAP内存前可用内存剩余百分比，0不使用swap
```

## 十七、服务自启动

1.复制启动脚本到`/etc/init.d`或`/etc/rc.d/init.d`

2.使用`chkconfig`设置开机启动

```shell
chkconfig --add service_name # 加入自启动
chkconfig --del service_name # 删除自启动
chkconfig --list service_name # 查看运行级别
chkconfig --levels 245 service_name off # 设置245下服务不自动启动
```
