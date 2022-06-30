from scapy.all import *
import time
import os
import geoip2.database
# 需要 Graphviz 和 ImageMagick
domain = input("追踪的域名: ")
dbreader = geoip2.database.Reader('/home/lxw/GeoLite2-City.mmdb') # 读取GeoLite2-City.mmdb
if len(domain) >= 1 and domain[0] != "":
    a,u = traceroute(domain)
    ip_addrs = set("") # 创造空集合存放IP地址
    for i in range(len(a)):
        ip_addr = a[i].answer.src
        ip_addrs.add(ip_addr) # ip地址加入集合可以去重
    for ip in ip_addrs:
        try:
            geo_data = dbreader.city(ip)
            # 输出想要的信息
            print(
                ip, 
                geo_data.country.name, 
                geo_data.subdivisions.most_specific.name,
                geo_data.city.name
                # geo_data.location.latitude
                # geo_data.location.longitude
            )
        except:
            print(ip, "None", "None", "None")
    a.graph(target="> test.svg") # 绘制成路由图
    time.sleep(3)
    # os.popen("/usr/bin/convert ./test.svg ./test.png") 
    # 转化为png图片(可省略)
else:
    print("域名有误")
