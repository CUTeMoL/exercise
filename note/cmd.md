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
