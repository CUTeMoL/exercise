import pymongo
import datetime
import geoip2.database
# 连接数据库
mongodbclient = pymongo.MongoClient("mongodb://localhost:27017/")
mongodb = mongodbclient["nginxAccessLog"]
dblist = mongodbclient.list_database_names()
yesterday = datetime.date.today() + datetime.timedelta(days=-1)
col_name = "nginxLogs{}{}".format(str(yesterday)[0:4], str(yesterday)[5:7])
mongodbcol = mongodb[col_name]
# 读取GEO数据库
dbreader = geoip2.database.Reader('/home/lxw/GeoLite2-City.mmdb') # 读取GeoLite2-City.mmdb
# 读取日志文件存储到MongoDB
with open("/var/log/nginx/access.log.1", "r", encoding='utf8') as access_logs:
    for line in access_logs.readlines():
        data = eval(line)
        try:
            geo_data = dbreader.city(data["remote_addr"])
            data["remote_addr_Country"] = geo_data.country.name
            data["remote_addr_Province"] = geo_data.subdivisions.most_specific.name
            data["remote_addr_City"] = geo_data.city.name
        except geoip2.errors.AddressNotFoundError:
            data["remote_address"] = None
        x = mongodbcol.insert_one(data)
        # print(x.inserted_id)
# 删库
# x = mongodbcol.delete_many({})
# 全库查询
# for x in mongodbcol.find():
#     print(x)
