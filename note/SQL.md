# SQL

数据来自`sqlzoo`的`world`和`nobel`表

sqlzoo:  https://sqlzoo.net

## 一、DQL(数据查询语句)

### 语法顺序

```sql
SELECT sum(col) FROM t WHERE col=v GROUP BY col HAVING col ORDER BY col desc limit begin_num count_num;
```

| 关键词       | 作用                                                   |
| ------------ | ------------------------------------------------------ |
| `SELECT`     | 定义查询字段                                           |
| `FROM`       | 来自哪张表                                             |
| `WHERE`      | 筛选条件                                               |
| `GROUP BY`   | 分组,去重                                              |
| `HAVING`     | 过滤                                                   |
| `ORDER BY`   | 排序 `asc`升序 `desc`降序                              |
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
SELECT yr, subject, count(subject)
FROM nobel
WHERE yr in (2013, 2014, 2015)
GROUP BY yr, subject
ORDER BY yr desc, count(subject) desc;
```



#### `ORDER BY`

筛选1984年`subject`中的`Medicine`和`Physics`要排在最前，然后其他根据`subject`排序，最后根据`winner`排序

```sql
SELECT yr, winner, subject
FROM nobel
WHERE yr=1984
ORDER BY subject in ('Medicine', 'Physics') desc, subject, winner;
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

| 分类       | 符号\|关键词        | 作用                                                         |
| ---------- | ------------------- | ------------------------------------------------------------ |
| 通配符     | `*`                 | 字段通配符(代表所有)                                         |
|            | `_`                 | 字符通配符代表1个字符                                        |
|            | `%`                 | 字符通配符代表0个或多个字符                                  |
|            |                     |                                                              |
|            |                     |                                                              |
|            |                     |                                                              |
| 逻辑运算符 | `/`                 | 除法（分数符号）                                             |
|            | `*`                 | 乘法（在公式中）                                             |
|            | `+`                 | 加法（在公式中）                                             |
|            | `-`                 | 减法（在公式中）                                             |
|            | `=`                 | 等于                                                         |
|            | `>`                 | 大于, `>=`大于等于                                           |
|            | `<`                 | 小于, `<=`小于等于                                           |
|            | `<>`或`!=`          | 不等于                                                       |
|            | `between v1 and v2` | 在v1和v2之间的数，包括v1和v2                                 |
|            | `in`                | 条件范围筛选(列表)                                           |
|            | `not in`            | 不在该条件范围筛选                                           |
|            | `is null`           | 为空值                                                       |
|            | `is not null`       | 不为空值                                                     |
|            | `and`               | 与                                                           |
|            | `or`                | 或                                                           |
|            | `not`               | 非                                                           |
|            | `like`              | 模糊查询                                                     |
| 其他       | `as`                | 对表或字段起别名                                             |
|            | `distinct`          | 去除重复（放在`SELECT`后面）                                 |
|            | `()`                | 括号可以是列表`(v1, v2, v3)`，提供给in使用，也可以是调整运算的优先级`(col1+col2)` |

## 八、函数

| 函数    | 作用                 |
| ------- | -------------------- |
| sum()   | 总和，忽略`null`     |
| avg()   | 平均，忽略`null`     |
| max()   | 最大，忽略`null`     |
| min()   | 最小，忽略`null`     |
| count() | 统计次数，忽略`null` |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |
|         |                      |

