# SQL

数据来自`sqlzoo`

sqlzoo:  https://sqlzoo.net

## 一、DQL(数据查询语句)

### 语法顺序

```sql
SELECT sum(col) 
FROM t 
WHERE col=v 
GROUP BY col 
HAVING col 
ORDER BY col desc 
LIMIT begin_num count_num;
```

### 运行顺序

```sql
FROM > WHERE > GROUP BY > HAVING > SELECT创建的新字段 > ORDER BY > LIMIT > SELECT
```

| 关键词             | 作用                                    |
| --------------- | ------------------------------------- |
| `SELECT`        | 定义查询字段                                |
| `FROM`          | 来自哪张表(如果来自子查询则要添加临时表名)                |
| `INNER JOIN ON` | 表连接(笛卡尔积`X`),一定会显示所有结果,未匹配到的会填充`null` |
| `LEFT JOIN ON`  | 左连接，`INNER JOIN`的基础上丢弃右表未匹配到的`ROW`    |
| `RIGHT JOIN ON` | 右连接，`INNER JOIN`的基础上丢弃左表未匹配到的`ROW`    |
| `WHERE`         | 筛选条件                                  |
| `GROUP BY`      | 分组,去重                                 |
| `HAVING`        | 过滤                                    |
| `ORDER BY`      | 排序 `asc`升序 `desc`降序                   |
| `LIMIT x, n`    | x位置偏移量(从0开始，类似数值下标，第一行就是0), n行数       |

### 示例

#### `INNER JOIN`

```sql
SELECT * 
FROM T1
INNER JOIN T2
ON T1.col=T2.col;
```

#### `LEFT JOIN`和`RIGHT JOIN`

查询`game.team1`的教练是`Fernando Santos`的`eteam.teamname`、`game.mdate`和`game.id`

```sql
SELECT game.mdate, eteam.teamname, game.id
FROM game
LEFT JOIN eteam
ON game.team1=eteam.id
WHERE eteam.coach='Fernando Santos';
```

查询作为主角超过30次的演员，根据次数从大到小排序

```sql
SELECT actor.name, over30.times
FROM (SELECT actorid, count(*) times
FROM casting
WHERE casting.ord=1
GROUP BY actorid
HAVING count(ord)>30) over30
LEFT JOIN actor
ON over30.actorid=actor.id
ORDER BY over30.times DESC;
```

查询每场比赛的`game.id`和`game.mdate`，每个球队的进球情况

```sql
SELECT goal.matchid, game.mdate,
    game.team1, sum(case when game.team1=goal.teamid then 1 else 0 end) score1,
    game.team2, sum(case when game.team2=goal.teamid then 1 else 0 end) score2
FROM goal
LEFT JOIN game
ON game.id=goal.matchid
GROUP BY goal.matchid, game.mdate, game.team1, game.team2
```

#### `WHERE`

正则匹配以`H`或`C`开头的国家名

```sql
SELECT * 
FROM world
WHERE name REGEXP '^[H|O].*'
```

国家名包含`aeiou`这5个字符, 但是不能出现空格

```sql
SELECT name
FROM world
WHERE name like '%a%'
and name like '%e%'
and name like '%i%'
and name like '%o%'
and name like '%u%'
and name not like '% %';
```

查询首都和名称，其中首都需是国家名称的拓展(首都包含国家名)，但首都名不等于国家名

```sql
SELECT capital, name
FROM world
WHERE capital like concat('%', name, '%')
and name!=capital;
```

#### `GROUP BY`

统计`Medicine`的`winner`人数

```sql
SELECT subject, count(winner)
FROM nobel
WHERE subject='Medicine'
GROUP BY subject;
```

统计2013到2015年每年每个科目的获奖人数，按年数从大到小，按人数从大到小

```sql
SELECT yr, subject, count(winner)
FROM nobel
WHERE yr in (2013, 2014, 2015)
GROUP BY yr, subject
ORDER BY yr desc, count(winner) desc;
```

#### `HAVING`

查询人口数为3亿以上的大洲和其平均gdp，其中只有gdp高于200亿且人口数大于6000万或者gdp低于80亿且首都中含有三个a的国家计入计算，最后按国家数从大到小排序，只显示第一行

```sql
SELECT continent, avg(gdp), sum(population)
FROM world
WHERE (gdp>20000000000 and population>60000000)
    or (gdp<8000000000 and capital like '%a%a%a%')
GROUP BY continent
HAVING sum(population)>300000000
ORDER BY count(continent) desc
LIMIT 1;
```

#### `ORDER BY`

筛选1984年`subject`中的`Medicine`和`Physics`要排在最前，然后其他根据`subject`排序，最后根据`winner`排序

```sql
SELECT yr, winner, subject
FROM nobel
WHERE yr=1984
ORDER BY subject in ('Medicine', 'Physics') desc, subject, winner;
```

选区`S14000021`根据年份分区后，再对投票数进行从大到小排序，命名为`posn`，然后根据`party`进行排序，列出`yr`,`lastName`,`party`,`votes`,`posn`

```sql
SELECT yr, lastName, party, votes,
    RANK() OVER (PARTITION BY yr ORDER BY votes DESC) as posn
FROM ge
WHERE constituency = 'S14000021' 
ORDER BY party DESC;
```

从`covid`表中提取`France`和`Germany`的每年1月的每确诊人数和每日新增人数，按照日期排序

```sql
SELECT name, date_format(whn, '%Y-%m-%d') date, confirmed,
    lag(confirmed, 1)over(partition by name order by whn) yesterday,
    confirmed-lag(confirmed, 1)over(partition by name order by whn) new
FROM covid
WHERE name in ('France', 'Germany') and month(whn)=1
ORDER BY whn;
```

从`covid`表中提取`Italy`的每周新增人数

```sql
SELECT name, date_format(whn, '%Y-%m-%d') date, confirmed,
    lag(confirmed, 1)over(partition by name order by whn) weekbefore,
    confirmed-lag(confirmed, 1)over(partition by name order by whn) new
FROM covid
WHERE name='Italy' and weekday(whn)=0
ORDER BY whn;
```

#### `LIMIT`

查询第100到120行数据

```sql
SELECT * 
FROM nobel
LIMIT 99, 21;
```

#### `子查询`

查询`gdp`大于欧洲所有国家的国家

```sql
SELECT name
FROM world
WHERE gdp > (
    SELECT max(gdp)
    FROM world
    where continent='Europe'
);
```

查询和`Argentina`或`Australia`在同一个大洲的国家名,根据名称排序

```sql
SELECT name, continent
FROM world
WHERE continent in (
    SELECT continent
    FROM world
    WHERE name in ('Argentina', 'Australia')
)
ORDER BY name;
```

查询`2017年`所有在`S14000021`到`S14000026`选区投票数最高的议员

```sql
SELECT constituency, party, votes
FROM (
    SELECT constituency, votes, party,
    rank() over(partition by constituency order by votes desc ) rank
    FROM ge
    WHERE yr=2017
    and constituency>='S14000021'
    and constituency<='S14000026') a
WHERE rank=1;
```

查询所有国家人口大于`25000000`的大洲，及其国家名和人口

```sql
SELECT name, continent, population, gdp
FROM world
WHERE continent not in (
    SELECT continent
    FROM world
    WHERE population>25000000
);
```

查询每个`continent`中`area`最大的`name`, 显示`continent`,`name`.`area`

```sql
SELECT continent, name, area
FROM world
where area in (
    SELECT max(area)
    FROM world
    GROUP BY continent
);
```

## 二、DML(数据操作语句)

`INSERT`

`UPDATE`

`DELETE`

## 三、TCL(事务控制语句)

### SQLServer

| 关键词                            | 功能          |
| ------------------------------ | ----------- |
| `BEGIN TRANSACTION`            | 开启事务,可以加事务名 |
| `BEGIN DISTRIBUTE TRANSACTION` | 开启分布式事务     |
| `COMMIT TRANSACTION`           | 提交事务        |
| `ROLLBACK TRANSACTION`         | 回滚          |
| `SAVE TRANSACTION`             | 保存检查点       |

### MySQL

| 关键词                                 | 功能      |
| ----------------------------------- | ------- |
| `BEGIN` or `START TRANSACTION`      | 开启事务    |
| `BEGIN DISTRIBUTE TRANSACTION`      | 开启分布式事务 |
| `COMMIT` or `COMMIT WORK`           | 提交事务    |
| `ROLLBACK` or `ROLLBACK WORK`       | 回滚      |
| `SAVEPOINT checkpoint_name`         | 保存检查点   |
| `ROLLBACK TO checkpoint_name`       | 回滚至检查点  |
| `RELEASE SAVEPOINT checkpoint_name` | 删除检查点   |

## 四、DCL(数据控制语句)

`GRANT`

`DENY`

`REVOKE`

## 五、DDL(数据定义语句)

| 关键词        | 作用                         |
| ---------- | -------------------------- |
| `CREATE`   | 创建                         |
| `ALTER`    | 修改                         |
| `ADD`      | `ALTER`时添加`FILE`、`COLUMN`等 |
| `DROP`     | 删除(包括表结构)                  |
| `TRUNCATE` | 删除(不包括表结构)                 |

### 示例

#### `CREATE`

创建数据库

```sql
CREATE DATABASE dbname;
```

`SQL Server`创建数据库`test1`,文件`d:/filename.mdf`,初始大小`8mb`,最大大小`16mb`,自动增长`16mb`

```sql
CREATE DATABASE test1
on (
    name='test1',
    filename='d:/filename.mdf',
    size=8mb,
    maxsize=16mb,
    filegrowth=5%
);
```

创建数据表

```sql
CREATE TABLE table_name(
    column_name1 int UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    column_name2 datetime DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP() NOT NULL
    column_name3 datatype,
    column_name4 datatype
);
-- 在SQLServer中不能用UNSIGNED和AUTO_INCREMENT
-- 在sqlserver中可以使用datetime2(7)
```

创建表时创建联合主键

```sql
CREATE TABLE table_name(
    col_name1 int NOT NULL,
    col_name2 int NOT NULL,
    CONSTRAINT pk_name PRIMARY KEY(
        col_name1, col_name2
    )
);
-- 创建单字段主键，（）要保留
```

#### `ALTER`

修改数据库名称

```sql
ALTER DATABASE dbname 
MODIFY name=new_dbname;
-- 仅SQLServer使用
```

添加数据文件

```sql
ALTER DATABASE dbname
ADD FILE(name=dbfilename,
    filename='d:\dbfilename.ndf');
```

为`SQL Server`数据库`test1`添加日志`testlog`,文件`d:/testlog`,初始容量`2mb`,最大容量`50mb`,文件增长的数量为`10%`

```sql
ALTER DATABASE test1
ADD log FILE(
    name=testlog,
    filename='d:\testlog.ldf',
    size=2mb,
    maxsize=50mb,
    filegrowth=10%
);
```

修改表名

```sql
EXECUTE sp_rename 't1','t2';
-- 仅SQLServer使用
RENAME TABLE db01.t1 TO db02.t11;
-- 可以移动表到另一个库
```

添加表的字段

```sql
ALTER TABLE t1
ADD column_name1 datatype;
```

表的字段改名

```sql
ALTER TABLE emp 
RENAME COLUMN old_col_name TO new_col_name;
-- 仅MySQL使用
EXECUTE sp_rename 'table_name.column_name','column_name';
-- 仅SQLServer使用
```

修改字段的类型

```sql
ALTER TABLE t1
ALTER COLUMN column_name1 datatype;
-- 仅SQLServer使用
ALTER TABLE emp 
MODIFY COLUMN col_tmp varchar(10);
-- 仅MySQL使用
```

为已存在的表创建联合主键

```sql
ALTER TABLE t1
ADD CONSTRAINT pk_name PRIMARY KEY(
    column_name1, column_name2
);
```

为已存在的表`test01`的字段`column1`创建参照`test01`的字段`column2_fk`外键约束

```sql
ALTER TABLE test01
ADD CONSTRAINT fk_name foreign key(column1)
REFERENCES test02(column2_fk);
```

为已存在的表创建检查约束

```sql
ALTER TABLE test01
ADD CONSTRAINT ck_name CHECK(column>=1);
```

为已存在的表创建索引

```sql
CREATE UNIQUE INDEX index_name 
ON table_name(column_name);
-- UNIQUE代表唯一索引，没有的话就是普通索引
```

#### `DROP`

删除数据库

```sql
DROP DATABASE dbname;
```

删除表

```sql
DROP TABLE t1;
```

删除字段

```sql
ALTER TABLE t1 
DROP COLUMN column_name;
```

#### `TRUNCATE`

删除表数据，但保留表结构

```sql
TRUNCATE TABLE t1;
```

## 六、CCL(指针控制语句)

## 七、其他符号关键词用法

| 分类    | 符号\|关键词             | 作用                                                      |
| ----- | ------------------- | ------------------------------------------------------- |
| 通配符   | `*`                 | 字段通配符(代表所有)                                             |
|       | `_`                 | 字符通配符代表1个字符                                             |
|       | `%`                 | 字符通配符代表0个或多个字符                                          |
|       |                     |                                                         |
|       |                     |                                                         |
|       |                     |                                                         |
| 逻辑运算符 | `/`                 | 除法（分数符号）                                                |
|       | `*`                 | 乘法（在公式中）                                                |
|       | `+`                 | 加法（在公式中）                                                |
|       | `-`                 | 减法（在公式中）                                                |
|       | `=`                 | 等于                                                      |
|       | `>`                 | 大于, `>=`大于等于                                            |
|       | `<`                 | 小于, `<=`小于等于                                            |
|       | `<>`或`!=`           | 不等于                                                     |
|       | `between v1 and v2` | 在v1和v2之间的数，包括v1和v2                                      |
|       | `in`                | 条件范围筛选(列表)                                              |
|       | `not in`            | 不在该条件范围筛选                                               |
|       | `is null`           | 为空值                                                     |
|       | `is not null`       | 不为空值                                                    |
|       | `and`               | 与                                                       |
|       | `or`                | 或                                                       |
|       | `not`               | 非                                                       |
|       | `like`              | 模糊查询                                                    |
|       | `REGEXP`            | 正则匹配，忽视大小写                                              |
| 其他    | `as`                | 对表或字段起别名                                                |
|       | `distinct`          | 去除重复（放在`SELECT`后面）                                      |
|       | `()`                | 括号可以是列表`(v1, v2, v3)`，提供给in使用，也可以是调整运算的优先级`(col1+col2)` |

## 八、函数

| 类型          | 函数                                                          | 作用                                                                                           |
| ----------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 计算          | `sum()`                                                     | 总和，忽略`null`                                                                                  |
|             | `avg()`                                                     | 平均，忽略`null`                                                                                  |
|             | `max()`                                                     | 最大，忽略`null`                                                                                  |
|             | `min()`                                                     | 最小，忽略`null`                                                                                  |
|             | `count()`                                                   | 统计次数，忽略`null`                                                                                |
|             | `round(x, y)`                                               | 对`x`四舍五入, 保留小数点`y`位（y可以是负数）                                                                  |
|             | `floor(x)`                                                  | 对`x`进行向下取整,如`-1.9`取整为`-2`                                                                    |
|             |                                                             |                                                                                              |
| 字符串         | `concat('str1', 'str2')`                                    | 连接字符串                                                                                        |
|             | `replace('str', 'old', 'new')`                              | 替换                                                                                           |
|             | `left('str', n)`                                            | 截取左边的`n`个字符                                                                                  |
|             | `right('str', n)`                                           | 截取右边的`n`个字符                                                                                  |
|             | `substring('str', n, len)`                                  | 从左边的`n`个字符开始，截取`len`个字符                                                                      |
|             |                                                             |                                                                                              |
| 数据类型转换      | `cast(x as type)`                                           | 将`x`转换成新类型`type`                                                                             |
| 日期时间函数      | `year(date)`                                                | 获取年份                                                                                         |
|             | `month(date)`                                               | 获取月份                                                                                         |
|             | `day(date)`                                                 | 获取日                                                                                          |
|             | `date_add(date, INTERVAL expr type)`                        | 时间加操作, `expr`是间隔`n`, `type`值`SECOND`,`MINUTE`,`HOUR`,`DAY`,`WEEK`,`MONTH`,`QUARTER`,`YEAR`   |
|             | `date_sub(date, INTERVAL expr type)`                        | 时间减操作, `expr`是间隔`n`, `type`值`SECOND`,`MINUTE`,`HOUR`,`DAY`,`WEEK`,`MONTH`,`QUARTER`,`YEAR`   |
|             | `datediff(date1, date2)`                                    | 对比两个日期之间的间隔天数                                                                                |
|             | `date_format(date,format)`                                  | 将日期和时间格式化`format`可以是`%Y/%M/%d %H:%i:S`                                                       |
| 条件判断函数      | `if(expr, 'v1', 'v2')`                                      | 如果表达式`expr`结果为`True`返回`v1`,`False`返回`v2`                                                     |
|             | `case expr when v1 then r1 [when v2 then r2] [else rn] end` | 如果表达式`expr`结果为`v1`返回`r1`,`v2`返回`r2`其它返回`rn`                                                  |
|             | `case when expr then r1 [when expr then r2] [else rn] end`  | 如果表达式`expr`成立，返回`r1`，匹配一条后，就不继续匹配了                                                           |
| 窗口函数        | `rank() over(PARTITION BY col1 ORDER BY col2 DESC)`         | 在`ORDER BY`之前生效,根据`PARTITION BY`分区(不去重，可选则不分区，则对整张表排序)，排序时`ORDER BY`会赋值序号，窗口函数只能在`SELECT`中使用 |
| 窗口函数赋值序号的方式 | `rank()`                                                    | 跳跃排序, 如`1,1,3,4`                                                                             |
|             | `dense_rank()`                                              | 并列连续, 如`1,1,2,3`                                                                             |
|             | `row_number()`                                              | 连续累加, 如`1,2,3,4`                                                                             |
| 窗口函数偏移分析函数  | `lag(col1, n) over(partition by col2 order by col3)`        | `lag()`根据字段`col1`，向上偏移`n`位                                                                   |
|             | `lead(col1, n)`                                             | 向下偏移                                                                                         |

## 九、数据类型

### INT(整型)

| 数据库        | Type        | range                    | unsigned_Max   |
| ---------- | ----------- | ------------------------ | -------------- |
| SQL SERVER | `bit`       | `0`,`1`,`NULL`           | `0`,`1`,`NULL` |
| SQL SERVER | `tinyint`   | `0~255`                  | `255`          |
|            | `tinyint`   | `-128~127`               | `255`          |
|            | `smallint`  | `-32768~32767`           | `65535`        |
|            | `mediumint` | `-8388608~8388607`       | `16777215`     |
|            | `int`       | `-2147483648~2147483647` | `4294967295`   |
|            | `bigint`    | `-2^63~2^63-1`           | `2^64-1`       |

| unsigned | signed | zerofill           | auto_increment       |
| -------- | ------ | ------------------ | -------------------- |
| 无符号      | 有符号    | 显示真实属性/值不做任何修改/填充0 | 自增/每张表只能一个/必须是索引的一部分 |

### 浮点数

| 数据库        | type      | 占用空间 | 精度  | 精确度 |
| ---------- | --------- | ---- | --- | --- |
| MySQL      | `FLOAT`   | 4    | 单精度 | 低   |
| MySQL      | `DOUBLE`  | 8    | 双精度 | 中   |
| SQL SERVER | `NUMERIC` | 变长   | 高精度 | 高   |
|            | `DECIMAL` | 变长   | 高精度 | 高   |

FLOAT(M,D)/DOUBLE(M,D)/DECIMAL(M,D)/NUMERIC(M,D)    表示显示M位整数D位小数

NUMERIC(M,D) 在功能上完全等同于 DECIMAL(M,D)

### MONEY类型

| 数据库        | type         | 占用空间 |
| ---------- | ------------ | ---- |
| SQL SERVER | `MONEY`      | 8    |
| SQL SERVER | `SMALLMONEY` | 4    |

### 字符串类型

| type           | 说明             | N的含义 | 是否有字符集 | 最大长度  |
| -------------- | -------------- | ---- | ------ | ----- |
| `CHAR(N)`      | 定长字符，不足的部分空格补齐 | 字符   | 是      | 255   |
| `VARCHAR(N)`   | 变长字符           | 字符   | 是      | 16384 |
| `BINARY(N)`    | 定长二进制字节        | 字节   | 否      | 255   |
| `VARBINARY(N)` | 变长二进制字节        | 字节   | 否      | 16384 |
| `TINYBLOB`     | 二进制大对象         | 字节   | 否      | 256   |
| `BLOB`         | 二进制大对象         | 字节   | 否      | 16K   |
| `MEDIUMBLOB`   | 二进制大对象         | 字节   | 否      | 16M   |
| `LONGBLOB`     | 二进制大对象         | 字节   | 否      | 4G    |
| `TINYTEXT`     | 大对象            | 字节   | 是      | 256   |
| `TEXT`         | 大对象            | 字节   | 是      | 16K   |
| `MEDIUMTEXT`   | 大对象            | 字节   | 是      | 16M   |
| `LONGTEXT`     | 大对象            | 字节   | 是      | 4G    |

`BINARY`/`BLOB`主要用于存2进制数据

`VARCHAR`会检查字符是否存在，但`BINARY`不会，`BINARY`存放的是2进制字节，碰到不同的字符集显示不同的字符

`TEXT`相当于`VARCHAR`但是长度计算方式不同

`nchar`,`nvarchar`,`ntext`unicode类型

### `ENUM`枚举类型（多选一）

最多允许65536个值

### `SET`集合类型（多选多）

最多允许64个值

### `JSON`类型

由一系列的`key:value`组成的数据字符串（类似Mongodb，不需要定义列）

`BLOB`可以不符合`key:value`，不能做约束性检查，`JSON`数据类型会约束一定符合`key:value`者一格式

`JSON`查询性能高：查询不需要遍历所有字符串才能找到数据

支持部分属性索引：通过虚拟列的功能可以对`JSON`中的部分数据进行索引

另外`json_extract`、`json_unquote`

`JSON`插入示例：

```sql
create table table_name (
    col_name1 int,
    col_name2 json
);

insert into table_name (
    value1,
    '{"colname_json1":"value_json1","colname_json2":"value_json2"}'
);
```

### 日期类型

MySQL

| type        | 占用字节 | 表示范围                                              |
| ----------- | ---- | ------------------------------------------------- |
| `DATETIME`  | 8    | `1000-01-01 00:00:00~9999-12-31 23:59:59`         |
| `DATE`      | 3    | `1000-01-01~9999-12-31`                           |
| `TIMESTAMP` | 4    | `1970-01-01 00:00:00 UTC~2038-01-19 03:14:17 UTC` |
| `YEAR`      | 1    | `YEAR(2):1970~2070     YEAR(4):1901~2155`         |
| `TIME`      | 3    | `-838:59:59~838:59:59`                            |

*有时区的话推荐`TIMESTAMP`

SQL Server

| type             | 占用空间 | 格式                                          | 范围                                                                      | 时区偏移量 |
| ---------------- | ---- | ------------------------------------------- | ----------------------------------------------------------------------- | ----- |
| `DATETIME`       | 8    | `YYYY-MM-DD hh:mm:ss[.nnn]`                 | `1753-01-01 ~ 9999-12-31`                                               | ❌     |
| `DATETIME2`      | 6-8  | `YYYY-MM-DD hh:mm:ss[.nnnnnnn]`             | `0001-01-01 00:00:00.0000000 ~ 9999-12-31 23:59:59.9999999`             | ❌     |
| `DATE`           | 3    | `YYYY-MM-DD`                                | `0001-01-01 ~ 31.12.99`                                                 | ❌     |
| `SMALLDATETIME`  | 4    | `YYYY-MM-DD hh:mm:ss`                       | `1900-01-01 ~ 2079-06-06`                                               | ❌     |
| `TIME`           | 3-5  | `hh:mm:ss[.nnnnnnn]`                        | `00:00:00.0000000 ~ 23:59:59.9999999`                                   | ❌     |
| `DATETIMEOFFSET` | 8-10 | `YYYY-MM-DD hh:mm:ss[.nnnnnnn] [+\|-]hh:mm` | `0001-01-01 00:00:00.0000000 到 9999-12-31 23:59:59.9999999（以 UTC 时间表示）` | ✔     |

### `geometry`

地理空间类型，可存经纬度

## 附录

### world表

| name | continent | area | population | gdp | capital |
| ---- | --------- | ---- | ---------- | --- | ------- |
| 国家名  | 大洲        | 面积   | 人口         | GDP | 首都      |

### nobel表

| yr  | subject | winner |
| --- | ------- | ------ |
| 年   | 学科      | 获奖者    |

### ge表

| yr  | firstName | lastName | constituency | party | votes |
| --- | --------- | -------- | ------------ | ----- | ----- |
| 年   | 姓         | 名        | 选区           | 政党    | 票数    |

### covid表

| name | whn | confirmed | deaths | recovered |
| ---- | --- | --------- | ------ | --------- |
| 名    | 日期  | 确诊        | 死亡     | 治愈        |

### game表

| id   | mdate | stadium | team1 | team2 |
| ---- | ----- | ------- | ----- | ----- |
| 比赛id | 日期    | 场地      | 队伍1id | 队伍2id |

### goal表

| matchid | teamid | player | gtime     |
| ------- | ------ | ------ | --------- |
| 比赛id    | 队伍id   | 运动员    | 球员每次进球的分数 |

### eteam表

| id   | teamname | coach |
| ---- | -------- | ----- |
| 队伍id | 队名       | 教练    |

### movie表

| id   | title | yr  | director | budget | gross |
| ---- | ----- | --- | -------- | ------ | ----- |
| 电影id | 标题    | 年份  | 导演名      | 预算     | 收入    |

### actor表

| id   | name |
| ---- | ---- |
| 演员id | 演员名  |

### casting表

| movieid | actorid | ord  |
| ------- | ------- | ---- |
| 电影id    | 演员id    | 主角顺位 |
