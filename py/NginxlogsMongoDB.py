import pymongo
import datetime
# 连接数据库
mongodbclient = pymongo.MongoClient("mongodb://localhost:27017/")
mongodb = mongodbclient["nginxAccessLog"]
dblist = mongodbclient.list_database_names()
yesterday = datetime.date.today() + datetime.timedelta(days=-1)
col_name = "nginxLogs{}{}".format(str(yesterday)[0:4], str(yesterday)[5:7])
mongodbcol = mongodb[col_name]
# 读取日志文件存储到MongoDB
with open("/var/log/nginx/access.log.1", "r", encoding='utf8') as access_logs:
    for line in access_logs.readlines():
        data = eval(line)
        x = mongodbcol.insert_one(data)
        print(x.inserted_id)
# x = mongodbcol.delete_many({})
for x in mongodbcol.find():
    print(x)

