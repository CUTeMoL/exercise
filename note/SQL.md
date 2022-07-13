# SQL

数据来自`sqlzoo`的`world`、`ge`和`nobel`表

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
limit begin_num count_num;
```

| 关键词          | 作用                              |
| ------------ | ------------------------------- |
| `SELECT`     | 定义查询字段                          |
| `FROM`       | 来自哪张表                           |
| `WHERE`      | 筛选条件                            |
| `GROUP BY`   | 分组,去重                           |
| `HAVING`     | 过滤                              |
| `ORDER BY`   | 排序 `asc`升序 `desc`降序             |
| `LIMIT x, n` | x位置偏移量(从0开始，类似数值下标，第一行就是0), n行数 |

### 示例

#### `WHERE`

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
ORDER BY party DESC
```

#### `LIMIT`

查询第100到120行数据

```sql
SELECT * 
FROM nobel
LIMIT 99, 21;
```

## 二、DML(数据操作语句)

## 三、TCL(事务控制语句)

## 四、DCL(数据控制语句)

## 五、DDL(数据定义语句)

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
| 窗口函数偏移分析函数  |                                                             |                                                                                              |

## 九、数据类型

### INT(整型)

| Type        | range                    | unsigned_Max |
| ----------- | ------------------------ | ------------ |
| `tinyint`   | `-128~127`               | `255`        |
| `smallint`  | `-32768~32767`           | `65535`      |
| `mediumint` | `-8388608~8388607`       | `16777215`   |
| `int`       | `-2147483648~2147483647` | `4294967295` |
| `bigint`    | `-2^63~2^63-1`           | `2^64-1`     |

| unsigned | signed | zerofill           | auto_increment       |
| -------- | ------ | ------------------ | -------------------- |
| 无符号      | 有符号    | 显示真实属性/值不做任何修改/填充0 | 自增/每张表只能一个/必须是索引的一部分 |

### 浮点数

| type      | 占用空间 | 精度  | 精确度 |
| --------- | ---- | --- | --- |
| `FLOAT`   | 4    | 单精度 | 低   |
| `DOUBLE`  | 8    | 双精度 | 中   |
| `DECIMAL` | 变长   | 高精度 | 高   |

FLOAT(M,D)/DOUBLE(M,D)/DECIMAL(M,D)    表示显示M位整数D位小数

### 字符串类型

| type           | 说明      | N的含义 | 是否有字符集 | 最大长度  |
| -------------- | ------- | ---- | ------ | ----- |
| `CHAR(N)`      | 定长字符    | 字符   | 是      | 255   |
| `VARCHAR(N)`   | 变长字符    | 字符   | 是      | 16384 |
| `BINARY(N)`    | 定长二进制字节 | 字节   | 否      | 255   |
| `VARBINARY(N)` | 变长二进制字节 | 字节   | 否      | 16384 |
| `TINYBLOB`     | 二进制大对象  | 字节   | 否      | 256   |
| `BLOB`         | 二进制大对象  | 字节   | 否      | 16K   |
| `MEDIUMBLOB`   | 二进制大对象  | 字节   | 否      | 16M   |
| `LONGBLOB`     | 二进制大对象  | 字节   | 否      | 4G    |
| `TINYTEXT`     | 大对象     | 字节   | 是      | 256   |
| `TEXT`         | 大对象     | 字节   | 是      | 16K   |
| `MEDIUMTEXT`   | 大对象     | 字节   | 是      | 16M   |
| `LONGTEXT`     | 大对象     | 字节   | 是      | 4G    |

`BINARY`/`BLOB`主要用于存2进制数据

`VARCHAR`会检查字符是否存在，但`BINARY`不会，`BINARY`存放的是2进制字节，碰到不同的字符集显示不同的字符

`TEXT`相当于`VARCHAR`但是长度计算方式不同

### `ENUM`枚举类型（多选一）

最多允许65536个值

### `SET`集合类型（多选多）

最多允许64个值

### `JSON`类型

由一系列的`key:value`组成的数据字符串（类似Mongodb，不需要定义列）

`BLOB`可以不符合`key:value`，不能做约束性检查，`JSON`数据类型会约束一定符合`key:value`者一格式

`JSON`查询性能高：查询不需要遍历所有字符串才能找到数据

支持部分属性索引：通过虚拟列的功能可以对JSON中的部分数据进行索引

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
)
```

### 日期类型

| type        | 占用字节 | 表示范围                                              |
| ----------- | ---- | ------------------------------------------------- |
| `DATETIME`  | 8    | `1000-01-01 00:00:00~9999-12-31 23:59:59`         |
| `DATE`      | 3    | `1000-01-01~9999-12-31`                           |
| `TIMESTAMP` | 4    | `1970-01-01 00:00:00 UTC~2038-01-19 03:14:17 UTC` |
| `YEAR`      | 1    | `YEAR(2):1970~2070     YEAR(4):1901~2155`         |
| `TIME`      | 3    | `-838:59:59~838:59:59`                            |

*有时区的话推荐`TIMESTAMP`

### `geometry`

地理空间类型，可存经纬度

## 附录

### world表结构

| name | continent | area | population | gdp | capital |
| ---- | --------- | ---- | ---------- | --- | ------- |
| 国家名  | 大洲        | 面积   | 人口         | GDP | 首都      |

https://sqlzoo.net/wiki/SELECT_from_WORLD_Tutorial

### nobel表结构

| yr  | subject | winner |
| --- | ------- | ------ |
| 年   | 学科      | 获奖者    |

https://sqlzoo.net/wiki/SELECT_from_Nobel_Tutorial

ge表结构

| yr  | firstName | lastName | constituency | party | votes |
| --- | --------- | -------- | ------------ | ----- | ----- |
| 年   | 姓         | 名        | 选区           | 政党    | 票数    |

https://sqlzoo.net/wiki/Window_functions
