import sys
import pycurl

def test_url(URL):
    website = pycurl.Curl()
    website.setopt(pycurl.URL, URL)
    website.setopt(pycurl.CONNECTTIMEOUT, 5)
    website.setopt(pycurl.TIMEOUT, 5)
    website.setopt(pycurl.NOPROGRESS, 1)
    website.setopt(pycurl.FORBID_REUSE, 1)
    website_file = open("./url_result.html", mode="wb")
    website.setopt(pycurl.WRITEHEADER, website_file)
    website.setopt(pycurl.WRITEDATA, website_file)
    try:
        website.perform()
    except Exception as err:
        print(f"connection fail: {err}")
        website_file.close()
        website.close()
        sys.exit()
    print("{}的状态码: {}".format(URL, website.getinfo(pycurl.HTTP_CODE)))
    print("{}的总用时: {}".format(URL, website.getinfo(pycurl.TOTAL_TIME)))
    print("{}的DNS解析用时: {}".format(URL, website.getinfo(pycurl.NAMELOOKUP_TIME)))
    print("{}的建立连接用时: {}".format(URL, website.getinfo(pycurl.CONNECT_TIME)))
    print("{}的建立连接-准备传输用时: {}".format(URL, website.getinfo(pycurl.PRETRANSFER_TIME)))
    print("{}的建立连接-传输开始用时: {}".format(URL, website.getinfo(pycurl.STARTTRANSFER_TIME)))
    print("{}的重定向所消耗的时间: {}".format(URL, website.getinfo(pycurl.REDIRECT_TIME)))
    print("{}的上传数据包大小: {}".format(URL, website.getinfo(pycurl.SIZE_UPLOAD)))
    print("{}的下载数据包大小: {}".format(URL, website.getinfo(pycurl.SIZE_DOWNLOAD)))
    print("{}的平均上传速度: {}".format(URL, website.getinfo(pycurl.SPEED_UPLOAD)))
    print("{}的平均下载速度: {}".format(URL, website.getinfo(pycurl.SPEED_DOWNLOAD)))
    print("{}的HTTP头部大小: {}".format(URL, website.getinfo(pycurl.HEADER_SIZE)))
    website_file.close()
    website.close()

website_url = input("输入URL地址,如http://www.baidu.com :")
test_url(website_url)
flag = input("按任意键退出：")