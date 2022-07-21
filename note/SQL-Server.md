# SQL Server

## 一、数据库对象

### 1. 表

一行一条记录

一列一个字段

### 2. 视图

虚拟的表

从实际存在的表中提取数据，而不需要得知真实的表，提高了安全性

### 3. 索引

目录，提高查询速度

分为聚集索引(主键索引)和非聚集索引

### 4. 存储过程

把数据库操作的过程存储到一个对象中，可以提高数据库安全性

### 5. 触发器

达成某一条件后，执行的操作

## 二、安装

### Windows安装

#### 1.准备

设置hostname

创建Windows用户, 在该用户下运行安装程序 (会成为SQL Server的管理用户)

#### 2.运行安装程序

```powershell
C:\SQL2019\Developer_CHS\SETUP.EXE
```

✔️ 数据库引擎服务

✔️ SQL Server 复制

✔️ 混合模式+密码

一路下一步即可

#### 3.配置TCP/IP连接

打开配置管理器

```powershell
C:\Windows\SysWOW64\mmc.exe
```

SQL Server 网络配置 > MSSQLSERVER 的协议 > TCP/IP 启用

SQL Server 网络配置 > MSSQLSERVER 的协议 > TCP/IP 属性 > IP地址 > IPALL 端口 1433 > 确定

#### 4.重启SQL Server

打开配置管理器

```powershell
C:\Windows\SysWOW64\mmc.exe
```

SQL Server 服务 > SQL Server (MSSQLSERVER) > 重启

#### 5.安装SSMS(Microsoft SQL Server Management Studio)

开启TCP/IP后，可以不在同一台计算机登陆数据库实例

登录格式↓

```powershell
192.168.51.23,1433\MSSQLSERVER
```

### docker安装

```shell
docker pull mcr.microsoft.com/mssql/server:2019-latest
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=passwd" \
   --restart=always \
   -p 1433:1433 --name sqlserver -h sqlserver.lxw.com \
   -v sqlserver:/var/opt/mssql \
   -d mcr.microsoft.com/mssql/server:2019-latest
```

`SA_PASSWORD`需要复杂密码

持久化需要挂载逻辑卷，而不能是hostpath

## 三、性能查询

查询SQL SERVER 的运行情况

```sql
SELECT * 
FROM master.dbo.spt_monitor
```

## 四、数据库

数据存储页的大小默认8K，实际上会因为扇区大小的缘故，再次拆分问512字节的分割页

### 恢复模式

| 恢复模式  | 功能                                                                                        |
| ----- | ----------------------------------------------------------------------------------------- |
| 完整    | 数据文件丢失或损坏不会导致丢失工作。恢复到特定时间点上，或特定的事务                                                        |
| 大容量日志 | 是完整恢复模式的附加模式，允许执行高性能的大容量复制操作。通过使用最小方式记录大多数大容量操作，减少日志空间使用量。(不完整的记录日志，可能造成数据丢失)             |
| 简单    | 无日志备份(自动截断日志)。自动回收日志空间以减少空间需求，实际上不再需要管理事务日志空间。 最新备份之后的更改不受保护。在发生灾难时，这些更改必须重做。 只能恢复到备份的结尾。 |

一般用完整模式

### 数据页验证算法

| 页验证                 | 功能                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------- |
| CHECKSUM            | 写入数据时，会计算CHECKSUM(数据校验和)，写入页头部，读取数据时通过页头部的CHECKSUM，和数据的CHECKSUM对比，即可得知数据是否完整，只校验逻辑上的页 |
| TORN_PAGE_DETECTION | 分割页检验，每一个分割页都会校验，每当操作系统写一个SQLServer的8K数据页到磁盘时，都必须把数据分成多个512字节的页面。开启会有性能损失，但是更安全       |
| NONE                | 不校验                                                                                   |

### NULL值比较

```sql
SET ANSI_NULLS ON;
```

使`NULL`不可被比较，只可以用`is NULL`或`is not NULL`来查询

### 限制访问

| 限制访问模式          | 功能     |
| --------------- | ------ |
| MULTI_USER      | 多用户    |
| SINGLE_USER     | 单用户    |
| RESTRICTED_USER | 限制用户访问 |

### 使用权限

| 权限  | 功能                        |
| --- | ------------------------- |
| 用户  | 可以访问数据库的对象                |
| 角色  | 分配权限，属于这个角色的用户都可以使用该角色的权限 |

## 五、约束

### 1.主键约束(primary key)

保证非空、不重复、唯一

### 2.外键约束(参照约束、foreign key)

表和另一张表之间的数据进行关联

### 3.唯一约束

保证非空、不重复、可多个

### 4.检查约束

检查是否满足条件,满足才可以插入数据

### 5.非空约束

不为`NULL`

## 六、事务(Transaction)

保持数据一致性

### 属性

原子性、一致性、隔离性、持久性。

这四个属性通常称为ACID特性。

#### 原子性(atomicity)

一个事务是一个不可分割的工作单位,事务中包括的操作要么都做，要么都不做。

#### 一致性(consistency)

事务必须是使数据库从一个一致性状态变到另一个一致性状态。一致性与原子性是密切相关的。

#### 隔离性(isolation)

一个事务的执行不能被其他事务干扰。即一个事务内部的操作及使用的数据对并发的其他事务是隔离的，并发执行的各个事务之间不能互相干扰。

#### 持久性(durability)

持久性也称永久性(permanence)，指一个事务一旦提交，它对数据库中数据的改变就应该是永久性的。接下来的其他操作或故障不应该对其有任何影响。

### 开启隐式事务

```sql
SET IMPLLICT_TRANSCATION ON;
```

### 事务隔离级别

| 事务隔离级别             | 解释                                           | 优点                   | 缺点                    |
| ------------------ | -------------------------------------------- | -------------------- | --------------------- |
| `read uncommitted` | 事务中的修改，即使没有提交，其他事务也可以看得到                     | 性能好                  | 会导致“脏读”、“幻读”和“不可重复读取” |
| `read committed`   | 大多数主流数据库的默认事务等级，保证了一个事务不会读到另一个并行事务已修改但未提交的数据 | 避免了“脏读取”，该级别适用于大多数系统 | 不能避免“幻读”和“不可重复读取”。    |
| `repeatable read`  | 保证了一个事务不会修改已经由另一个事务读取但未提交（回滚）的数据             | 避免了“脏读取”和“不可重复读取”的情况 | 但不能避免“幻读”，带来了更多的性能损失  |
| `serializable`     | 保证事务之间完全的隔离                                  | 最高隔离级别               | 性能损失最大，影响使用           |

基于数据库的锁来实现

避免“脏读”、“幻读”和“不可重复读取”的发生

| 数据不一致的情况 | 解释                                              |
| -------- | ----------------------------------------------- |
| 脏读       | 事务中的修改，即使没有提交，其他事务也可以看得到，如果事务回滚，则这是一条错误数据       |
| 幻读       | 事务1读取不到记录，此时，事务2`INSERT`此条记录，导致事务1无法`INSERT`此纪录 |
| 不可重复读取   | 同一事务，2次读取到的记录不一致                                |

为了解决这些情况，可以调整事务的隔离级别

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
```

### 查询当前活跃事务

```sql
DBCC OPENTRAN(db_name);
```

## 七、锁

对共享资源进行并发访问

提供数据的完整性和一致性

### 事务的阻塞

如果一个事物在数据操作中锁住了某个数据库资源，而此时，另一个事务想要访问该资源，则必须等待该资源解锁，这样就会发生阻塞

### 死锁

多用户或多进程资源争夺，所有阻塞的事务都在等待其他事务提交来释放锁

#### 确定持有锁的查询

```sql
-- Perform cleanup.   
IF EXISTS(SELECT * FROM sys.server_event_sessions WHERE name='FindBlockers')  
    DROP EVENT SESSION FindBlockers ON SERVER  
GO  
-- Use dynamic SQL to create the event session and allow creating a -- predicate on the AdventureWorks database id.  
--  
DECLARE @dbid int  

SELECT @dbid = db_id('AdventureWorks')  

IF @dbid IS NULL  
BEGIN  
    RAISERROR('AdventureWorks is not installed. Install AdventureWorks before proceeding', 17, 1)  
    RETURN  
END  

DECLARE @sql nvarchar(1024)  
SET @sql = '  
CREATE EVENT SESSION FindBlockers ON SERVER  
ADD EVENT sqlserver.lock_acquired   
    (action   
        ( sqlserver.sql_text, sqlserver.database_id, sqlserver.tsql_stack,  
         sqlserver.plan_handle, sqlserver.session_id)  
    WHERE ( database_id=' + cast(@dbid as nvarchar) + ' AND resource_0!=0)   
    ),  
ADD EVENT sqlserver.lock_released   
    (WHERE ( database_id=' + cast(@dbid as nvarchar) + ' AND resource_0!=0 ))  
ADD TARGET package0.pair_matching   
    ( SET begin_event=''sqlserver.lock_acquired'',   
            begin_matching_columns=''database_id, resource_0, resource_1, resource_2, transaction_id, mode'',   
            end_event=''sqlserver.lock_released'',   
            end_matching_columns=''database_id, resource_0, resource_1, resource_2, transaction_id, mode'',  
    respond_to_memory_pressure=1)  
WITH (max_dispatch_latency = 1 seconds)'  

EXEC (@sql)  
--   
-- Create the metadata for the event session  
-- Start the event session  
--  
ALTER EVENT SESSION FindBlockers ON SERVER
STATE = START
--  
-- The pair matching targets report current unpaired events using   
-- the sys.dm_xe_session_targets dynamic management view (DMV)  
-- in XML format.  
-- The following query retrieves the data from the DMV and stores  
-- key data in a temporary table to speed subsequent access and  
-- retrieval.  
--  
SELECT   
objlocks.value('(action[@name="session_id"]/value)[1]', 'int')  
        AS session_id,  
    objlocks.value('(data[@name="database_id"]/value)[1]', 'int')   
        AS database_id,  
    objlocks.value('(data[@name="resource_type"]/text)[1]', 'nvarchar(50)' )   
        AS resource_type,  
    objlocks.value('(data[@name="resource_0"]/value)[1]', 'bigint')   
        AS resource_0,  
    objlocks.value('(data[@name="resource_1"]/value)[1]', 'bigint')   
        AS resource_1,  
    objlocks.value('(data[@name="resource_2"]/value)[1]', 'bigint')   
        AS resource_2,  
    objlocks.value('(data[@name="mode"]/text)[1]', 'nvarchar(50)')   
        AS mode,  
    objlocks.value('(action[@name="sql_text"]/value)[1]', 'varchar(MAX)')   
        AS sql_text,  
    CAST(objlocks.value('(action[@name="plan_handle"]/value)[1]', 'varchar(MAX)') AS xml)   
        AS plan_handle,      
    CAST(objlocks.value('(action[@name="tsql_stack"]/value)[1]', 'varchar(MAX)') AS xml)   
        AS tsql_stack  
INTO #unmatched_locks  
FROM (  
    SELECT CAST(xest.target_data as xml)   
        lockinfo  
    FROM sys.dm_xe_session_targets xest  
    JOIN sys.dm_xe_sessions xes ON xes.address = xest.event_session_address  
    WHERE xest.target_name = 'pair_matching' AND xes.name = 'FindBlockers'  
) heldlocks  
CROSS APPLY lockinfo.nodes('//event[@name="lock_acquired"]') AS T(objlocks)  

--  
-- Join the data acquired from the pairing target with other   
-- DMVs to return provide additional information about blockers  
--  
SELECT ul.*  
    FROM #unmatched_locks ul  
    INNER JOIN sys.dm_tran_locks tl ON ul.database_id = tl.resource_database_id AND ul.resource_type = tl.resource_type  
    WHERE resource_0 IS NOT NULL  
    AND session_id IN   
        (SELECT blocking_session_id FROM sys.dm_exec_requests WHERE blocking_session_id != 0)  
    AND tl.request_status='wait'  
    AND REPLACE(ul.mode, 'LCK_M_', '' ) = tl.request_mode
DROP TABLE #unmatched_locks  
DROP EVENT SESSION FindBlockers ON SERVER
```

确定问题后，执行

```sql
DROP TABLE #unmatched_locks  
DROP EVENT SESSION FindBlockers ON SERVER
```

#### 查找具有最多锁定的对象

```sql
-- Find objects in a particular database that have the most
-- lock acquired. This sample uses AdventureWorksDW2012.
-- Create the session and add an event and target.

IF EXISTS(SELECT * FROM sys.server_event_sessions WHERE name='LockCounts')
    DROP EVENT session LockCounts ON SERVER;
GO
DECLARE @dbid int;

SELECT @dbid = db_id('AdventureWorksDW2012');

DECLARE @sql nvarchar(1024);
SET @sql = '
    CREATE event session LockCounts ON SERVER
        ADD EVENT sqlserver.lock_acquired (WHERE database_id ='
            + CAST(@dbid AS nvarchar) +')
        ADD TARGET package0.histogram(
            SET filtering_event_name=''sqlserver.lock_acquired'',
                source_type=0, source=''resource_0'')';

EXEC (@sql);
GO
ALTER EVENT session LockCounts ON SERVER
    STATE=start;
GO
-- Create a simple workload that takes locks.

USE AdventureWorksDW2012;
GO
SELECT TOP 1 * FROM dbo.vAssocSeqLineItems;
GO
-- The histogram target output is available from the
-- sys.dm_xe_session_targets dynamic management view in
-- XML format.
-- The following query joins the bucketizing target output with
-- sys.objects to obtain the object names.

SELECT name, object_id, lock_count
    FROM
    (
    SELECT objstats.value('.','bigint') AS lobject_id,
        objstats.value('@count', 'bigint') AS lock_count
        FROM (
            SELECT CAST(xest.target_data AS XML)
                LockData
            FROM     sys.dm_xe_session_targets xest
                JOIN sys.dm_xe_sessions        xes  ON xes.address = xest.event_session_address
                JOIN sys.server_event_sessions ses  ON xes.name    = ses.name
            WHERE xest.target_name = 'histogram' AND xes.name = 'LockCounts'
             ) Locks
        CROSS APPLY LockData.nodes('//HistogramTarget/Slot') AS T(objstats)
    ) LockedObjects
    INNER JOIN sys.objects o  ON LockedObjects.lobject_id = o.object_id
    WHERE o.type != 'S' AND o.type = 'U'
    ORDER BY lock_count desc;
GO

-- Stop the event session.

ALTER EVENT SESSION LockCounts ON SERVER
    state=stop;
GO
```

## 八、索引

加快数据的查询速度

### 按存储方式分类

#### 聚集索引

聚簇索引的顺序，就是数据在硬盘上的物理顺序

唯一

#### 非聚集索引

其实可以看作是一个含有聚集索引的表，只记录索引列和主键

可多个

### 按表列属性分类

#### 主键索引

#### 唯一索引

#### 普通索引

#### 多列索引

#### 全文索引

### 查看某一张表中的索引信息

```sql
sp_helpindex table_name
```

## 九、权限

### 登录名

登录名是登录数据库服务器的用户

登录名可以映射多个数据库用户

#### 创建登录用户

```sql
CREATE LOGIN "login_name" FROM windows;
-- SQLServer创建windows身份验证的用户
CREATE LOGIN "LXW" WITH password="passwd";
-- SQLServer创建SQLServer身份验证的用户
```

### 数据库用户

数据库用户是登录数据库的用户

数据库用户只能对应一个登录名 

#### 创建数据库用户

```sql
CREATE USER LXW FOR LOGIN LXW WITH DEFAULT_SCHEMA=dbo
```

### 角色

一个用户可以对应多个角色

#### 服务器级别角色

不可变更

#### 数据库级别角色

自己定义权限`SELECT`之类的
