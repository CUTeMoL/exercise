import pymongo
import datetime
import geoip2.database
'''
NGINX-accesslog格式
        log_format json '{"@timestamp": "$time_iso8601", '
                         '"remote_addr": "$remote_addr", '
                         '"remote_user": "$remote_user", '
                         '"body_bytes_sent": "$body_bytes_sent", '
                         '"status": "$status", '
                         '"request_time": "$request_time", '
                         '"request": "$request", '
                         '"request_uri": "$request_uri", '
                         '"request_method": "$request_method", '
                         '"http_referer": "$http_referer", '
                         '"http_x_forwarded_for": "$http_x_forwarded_for", '
                         '"upstream_status": "$upstream_status", '
                         '"upstream_response_time": "$upstream_response_time", '
                         '"http_user_agent": "$http_user_agent"}';

        access_log /var/log/nginx/access.log json;
'''
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
            data["remote_address"] = "PRIVATE NETWORK"
        x = mongodbcol.insert_one(data)
        # print(x.inserted_id)
# 删库
# x = mongodbcol.delete_many({})
# 全库查询
# for x in mongodbcol.find():
#     print(x)
