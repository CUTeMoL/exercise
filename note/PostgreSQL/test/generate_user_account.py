import random
import string
import datetime
import os

def generate_random_string(length=10):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_email():
    """生成随机邮箱"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com']
    username = generate_random_string(random.randint(5, 10))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_random_date(start_year=2010, end_year=2024):
    """生成随机日期"""
    start_date = datetime.datetime(start_year, 1, 1)
    end_date = datetime.datetime(end_year, 12, 31)
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + datetime.timedelta(days=random_days)

def generate_batch_sql(batch_size, batch_num, total_batches):
    """生成一批SQL数据"""
    sql_lines = []
    
    # 计算这批数据的起始ID
    start_id = batch_num * batch_size + 1
    end_id = start_id + batch_size - 1
    
    print(f"正在生成批次 {batch_num + 1}/{total_batches} (ID: {start_id} - {end_id})")
    
    for i in range(batch_size):
        user_id = start_id + i
        
        # 生成各字段数据
        username = generate_random_string(8)
        email = generate_random_email()
        age = random.randint(18, 80)
        salary = round(random.uniform(3000.00, 20000.00), 2)
        is_active = random.choice([True, False])
        created_at = generate_random_date().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = generate_random_date().strftime('%Y-%m-%d %H:%M:%S')
        phone = f"+1{random.randint(1000000000, 9999999999)}"
        
        # 生成JSON数据
        address_json = f'{{"street": "{generate_random_string(10)}", "city": "{generate_random_string(8)}", "zipcode": "{random.randint(10000, 99999)}"}}'
        
        # 生成数组数据
        tags = ["'" + tag + "'" for tag in random.sample(
            ["vip", "regular", "premium", "new", "active", "inactive", "verified"], 
            random.randint(1, 3)
        )]
        tags_array = f"ARRAY[{','.join(tags)}]"
        
        # 生成枚举值
        user_type = random.choice(["'admin'", "'user'", "'moderator'", "'guest'"])
        status = random.choice(["'active'", "'inactive'", "'pending'", "'suspended'"])
        
        # 构造SQL插入语句
        sql = f"({user_id}, '{username}', '{email}', {age}, {salary}, {str(is_active).lower()}, '{created_at}', '{updated_at}', '{phone}', '{address_json}'::jsonb, {tags_array}, {user_type}, {status})"
        sql_lines.append(sql)
    sql_lines.append('-- %s-%s 批次完成'%(start_id,end_id))
    return sql_lines

def create_table_sql():
    """创建表的SQL语句 - 表名改为user_account"""
    return """
-- 创建枚举类型
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'user', 'moderator', 'guest');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_status') THEN
        CREATE TYPE account_status AS ENUM ('active', 'inactive', 'pending', 'suspended');
    END IF;
END $$;

-- 创建用户账户表（避免使用user关键字）
CREATE TABLE IF NOT EXISTS user_account (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 120),
    salary DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address JSONB NOT NULL,
    tags TEXT[] NOT NULL,
    user_type user_role NOT NULL,
    status account_status NOT NULL,
    
    -- 添加唯一约束
    UNIQUE(username),
    UNIQUE(email)
);
"""

def create_indexes_sql():
    """创建索引的SQL语句 - 表名改为user_account"""
    return """
-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_account_status ON user_account (status);
CREATE INDEX IF NOT EXISTS idx_user_account_created_at ON user_account (created_at);
CREATE INDEX IF NOT EXISTS idx_user_account_age ON user_account (age);
CREATE INDEX IF NOT EXISTS idx_user_account_salary ON user_account (salary);
CREATE INDEX IF NOT EXISTS idx_user_account_is_active ON user_account (is_active);
CREATE INDEX IF NOT EXISTS idx_user_account_user_type ON user_account (user_type);

-- 创建JSONB字段的GIN索引
CREATE INDEX IF NOT EXISTS idx_user_account_address ON user_account USING gin (address);

-- 创建数组字段的GIN索引
CREATE INDEX IF NOT EXISTS idx_user_account_tags ON user_account USING gin (tags);

-- 创建复合索引
CREATE INDEX IF NOT EXISTS idx_user_account_status_active ON user_account (status, is_active);
CREATE INDEX IF NOT EXISTS idx_user_account_type_created ON user_account (user_type, created_at);
CREATE INDEX IF NOT EXISTS idx_user_account_email_username ON user_account (email, username);

-- 创建函数索引（用于按城市查询）
CREATE INDEX IF NOT EXISTS idx_user_account_city ON user_account USING btree ((address->>'city'));

-- 创建部分索引（只索引活跃用户）
CREATE INDEX IF NOT EXISTS idx_user_account_active_users ON user_account (id) WHERE is_active = true;
"""

def main():
    # 配置参数
    total_rows = 10000000 # 1000万行
    batch_size = 100       # 每批生成的数据量
    num_batches = total_rows // batch_size # 第N批次
    
    # 输出文件
    output_file = "generate_user_account.sql"
    
    print(f"开始生成 {total_rows:,} 行数据...")
    print(f"批量大小: {batch_size:,}")
    print(f"总批次数: {num_batches:,}")
    
    # 写入文件开头
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- PostgreSQL 用户账户数据生成脚本\n")
        f.write("-- 表名: user_account (避免使用user关键字)\n")
        f.write("-- 生成时间: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        f.write("-- 总数据量: %s 行\n\n"%(total_rows))
        
        # 写入创建表的SQL
        f.write(create_table_sql())
        f.write("\n\n")
        
        
        # 禁用触发器以提高导入性能（可选）
        f.write("-- 禁用触发器和索引以提高导入性能\n")
        f.write("ALTER TABLE user_account DISABLE TRIGGER ALL;\n\n")
        # 批量生成数据
        for batch_num in range(num_batches):
            # 每100批提交一次，避免事务过大
            # if batch_num % batch_size == 0 and batch_num > 0:
            #     f.write("COMMIT;\n\nBEGIN;\n\n")
            #     print(f"已提交 {batch_num} 批数据")
            
            # 生成一批数据
            batch_data = generate_batch_sql(batch_size, batch_num, num_batches)
            
            # 写入文件
            f.write("-- 第%s次插入用户账户数据\n"%(batch_num))
            f.write("BEGIN;\n")
            f.write("INSERT INTO user_account (id, username, email, age, salary, is_active, created_at, updated_at, phone, address, tags, user_type, status) VALUES\n")
            
            # 写入数据行
            for i, row in enumerate(batch_data):
                f.write(row)
                if i == batch_size - 1:
                    f.write(";\n")  # 最后一行
                else:
                    f.write(",\n")
            
            # 每批数据后刷新缓冲区
            f.write("COMMIT;\n\n")
        
        # 重新启用触发器
        f.write("-- 重新启用触发器\n")
        f.write("ALTER TABLE user_account ENABLE TRIGGER ALL;\n\n")
        
        
        # 创建索引（在数据插入后创建，提高性能）
        f.write("-- 创建索引（在数据插入后创建以提高性能）\n")
        f.write(create_indexes_sql())
        f.write("\n")
        
        # 更新统计信息
        f.write("-- 更新统计信息以便优化器做出更好的执行计划\n")
        f.write("ANALYZE user_account;\n\n")
        
        # 添加验证查询
        f.write("-- 验证数据\n")
        f.write("SELECT '总用户账户数: ' || COUNT(*)::TEXT FROM user_account;\n")
        f.write("SELECT status, COUNT(*) as count FROM user_account GROUP BY status ORDER BY count DESC;\n")
        f.write("SELECT user_type, COUNT(*) as count FROM user_account GROUP BY user_type ORDER BY count DESC;\n")
        f.write("SELECT is_active, COUNT(*) as count FROM user_account GROUP BY is_active;\n")
        f.write("SELECT AVG(age) as avg_age, MIN(age) as min_age, MAX(age) as max_age FROM user_account;\n")
        f.write("SELECT AVG(salary) as avg_salary, MIN(salary) as min_salary, MAX(salary) as max_salary FROM user_account;\n")
        f.write("SELECT (address->>'city') as city, COUNT(*) as user_count FROM user_account GROUP BY address->>'city' ORDER BY user_count DESC LIMIT 10;\n")
    
    print(f"\nSQL文件已生成: {output_file}")
    print(f"文件大小: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    # 生成执行说明
    with open("README_USER_ACCOUNT.txt", 'w', encoding='utf-8') as f:
        f.write("PostgreSQL 用户账户数据生成脚本说明\n")
        f.write("=" * 50 + "\n\n")
        f.write("重要提示：\n")
        f.write("1. 表名已从 'user' 改为 'user_account'，避免使用PostgreSQL关键字\n")
        f.write("2. 索引是在数据插入后单独创建的，以提高性能\n")
        f.write("3. 导入过程中禁用了触发器\n\n")
        
        f.write("执行步骤：\n")
        f.write("1. 创建数据库:\n")
        f.write("   CREATE DATABASE test;\n\n")
        f.write("2. 连接到数据库:\n")
        f.write("   \\c test\n\n")
        f.write("3. 执行SQL脚本（可能需要较长时间，建议在服务器上执行）:\n")
        f.write("   \\i generate_user_account.sql\n\n")
        f.write("4. 或者使用psql命令行:\n")
        f.write("   psql -d test -f generate_user_account.sql\n\n")
        
        f.write("性能优化建议（在psql中执行）：\n")
        f.write("1. 调整维护工作内存:\n")
        f.write("   SET maintenance_work_mem = '2GB';\n")
        f.write("2. 导入期间关闭同步提交:\n")
        f.write("   SET synchronous_commit = off;\n")
        f.write("3. 增加检查点间隔:\n")
        f.write("   SET checkpoint_timeout = '30min';\n")
        f.write("4. 查看执行时间:\n")
        f.write("   \\timing\n\n")
        
        f.write("一次性优化执行命令：\n")
        f.write("psql -d test -c \"SET maintenance_work_mem = '2GB'; SET synchronous_commit = off;\" -f generate_user_account.sql\n\n")
        
        f.write("表结构说明:\n")
        f.write("- id: BIGSERIAL - 主键，自增长\n")
        f.write("- username: VARCHAR(50) - 用户名，唯一\n")
        f.write("- email: VARCHAR(100) - 邮箱，唯一\n")
        f.write("- age: INTEGER - 年龄，18-120岁\n")
        f.write("- salary: DECIMAL(10,2) - 薪水\n")
        f.write("- is_active: BOOLEAN - 是否激活\n")
        f.write("- created_at: TIMESTAMP - 创建时间\n")
        f.write("- updated_at: TIMESTAMP - 更新时间\n")
        f.write("- phone: VARCHAR(20) - 电话号码\n")
        f.write("- address: JSONB - JSON格式地址\n")
        f.write("- tags: TEXT[] - 标签数组\n")
        f.write("- user_type: user_role - 用户类型枚举\n")
        f.write("- status: account_status - 状态枚举\n\n")
        
        f.write("创建的索引:\n")
        f.write("1. 基础字段索引: status, created_at, age, salary, is_active, user_type\n")
        f.write("2. JSONB字段GIN索引: address\n")
        f.write("3. 数组字段GIN索引: tags\n")
        f.write("4. 复合索引: (status, is_active), (user_type, created_at), (email, username)\n")
        f.write("5. 函数索引: 按城市查询\n")
        f.write("6. 部分索引: 只索引活跃用户\n")
    
    print("已生成 README_USER_ACCOUNT.txt 文件，包含详细使用说明")

if __name__ == "__main__":
    main()