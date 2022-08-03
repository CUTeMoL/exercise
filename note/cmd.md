# cmd

## 一、命令

### 1. set

设置变量

```powershell
set key=value
set /p key=comment # 接受用户输入value
set /a # 表达式计算
```

打印变量值

```powershell
set # 打印所有设置过的变量
set key # 打印^key的变量
```

取消变量

```powershell
set key=
```

使用变量

```powershell
%variable%
```

### 2. echo

回显

```powershell
echo on # 每一行的内容都要显示出来
echo off # 只显示执行结果
echo message # 显示消息(cmd中遇空格不换行)
echo "message" # 显示消息(不加引号时powershell中遇空格换行)
```

`@`本行只显示运行结果

```powershell
@echo on # 有@本行'echo on'不显示,只执行命令，其余行会显示
```

### 3. rem

注释

```powershell
rem message # 注释信息echo on下会回显
```

`::`也可以用于注释，和`rem`的区别在于`echo on`下是否回显

### 4. pause

暂停

```powershell
pause # 暂停，然后输入任意键继续
echo 注释信息 & pause > nul # 暂停并显示注释信息
```

### 5. title

```powershell
title title_message # 窗口的标题设置
```

### 6. goto

移动到`:label`这个标签的位置,可以创建循环

```powershell
:label1
set /a var+=1
echo %var%
if %var% leq 3 goto label1
pause
```
