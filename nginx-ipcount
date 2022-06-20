import xlsxwriter
import datetime
import os
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
# 文件及工作簿
yesterday = datetime.date.today()+datetime.timedelta(days=-1)
if not os.path.exists(f"/html/{yesterday.year}"):
    os.makedirs(f"/html/{yesterday.year}")
if not os.path.exists(f"/html/{yesterday.year}/{yesterday.month}"):
    os.makedirs(f"/html/{yesterday.year}/{yesterday.month}")
workbook = xlsxwriter.Workbook(f"/html/{yesterday.year}/{yesterday.month}/{yesterday}_IPS.xlsx")
worksheet = workbook.add_worksheet("ip")
worksheet1 = workbook.add_worksheet("url")
# 表
line_chart = workbook.add_chart({'type': 'line'})
column_chart = workbook.add_chart({'type': 'column'})
# format
ip_format = workbook.add_format({"bold": True})
worksheet.set_column("A1:A1", 25, ip_format)
worksheet.set_column("B1:B1", 35)
worksheet1.set_column("A1:A1", 50, ip_format)
worksheet1.set_column("B1:B1", 30)
line_chart.set_size({"width": 860, "height": 576})
column_chart.set_size({"width": 860, "height": 576})
# 生成数据
ips = {}
urls = {}
with open("/var/log/nginx/access.log.1", "r", encoding='utf8') as access_logs:
    for fileLine in access_logs.readlines():
        ip = eval(fileLine)["remote_addr"]
        ips[ip] = ips.get(ip, 0) + 1
        try:
            url = eval(fileLine)["request_uri"]
            urls[url] = urls.get(url, 0) + 1
        except KeyError:
            pass
ips_sorted = dict(sorted(ips.items(), key=lambda x: x[1], reverse=True))
urls_sorted = dict(sorted(urls.items(), key=lambda x: x[1], reverse=True))
# 写入数据
worksheet.write_string(0, 1, "ip访问次数最多的前十名")
worksheet.write_column(1, 0, ips_sorted.keys())
worksheet.write_column(1, 1, ips_sorted.values())
worksheet1.write_string(0, 1, "路径访问次数最多的前十五名")
worksheet1.write_column(1, 0, urls_sorted.keys())
worksheet1.write_column(1, 1, urls_sorted.values())
# 图形数据引用
ip_category_data = ["ip", 1, 0, 10, 0]
ip_value_data = ["ip", 1, 1, 10, 1]
ip_col_name = ["ip", 0, 1, 0, 1]
line_chart.add_series({
    "categories": ip_category_data,
    "values": ip_value_data,
    "name": ip_col_name
})
url_category_data = ["url", 1, 0, 15, 0]
url_value_data = ["url", 1, 1, 15, 1]
url_col_name = ["url", 0, 1, 0, 1]
column_chart.add_series({
    "categories": url_category_data,
    "values": url_value_data,
    "name": url_col_name
})
#插入表
worksheet.insert_chart("D1", line_chart)
worksheet1.insert_chart("D1", column_chart)
workbook.close()
