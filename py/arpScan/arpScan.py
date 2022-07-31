from scapy.all import *
import psutil
import IPy
import re
import xlsxwriter
# 导入OUI信息
with open("./oui_s.txt", "r", encoding='utf8') as f:
    oui_list = f.readlines()
net_devices = {} # 字典存储网卡信息
scan_range = {} # 记录网段信息
scan_list = [] # 设备列表
results = {} # 结果
# 遍历出IPV4地址，存到net_devices
for if_name in psutil.net_if_addrs():
    for i in range(len(psutil.net_if_addrs()[if_name])):
        if psutil.net_if_addrs()[if_name][i].family == 2:
            net_devices[if_name] = {
                "address": psutil.net_if_addrs()[if_name][i].address,
                "netmask": psutil.net_if_addrs()[if_name][i].netmask
            }
# 通过IP地址和掩码计算出所处网段
for net_device in net_devices:
    ipAddress = IPy.IP(net_devices[net_device]["address"])
    net_mask = net_devices[net_device]["netmask"]
    ips = IPy.IP(ipAddress).make_net(net_mask)
    scan_range[net_device] = ips
# 打印整理好的网络信息
print(f"共有{len(scan_range)}张网卡:")
for index, scan_device in enumerate(scan_range):
    scan_list.append(scan_device)
    print("\t", index+1, scan_device)
# 通过异常保证统一输入的key的是网卡名称
scan_nic = input(f"\n输入需要查询的网卡名称或序号: ")
try:
    scan_device_name = scan_list[int(scan_nic)-1]
except ValueError:
    scan_device_name = scan_nic
except IndexError:
    scan_device_name = scan_nic
try:
    scan_ip_range = str(scan_range[scan_device_name])
except KeyError:
    print("请输入正确的网卡名称 ")
    exit()
print("\n正在扫描网段: ", scan_range[scan_device_name])
# arp ping
ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=scan_ip_range), timeout=2)
print("\n扫描完成, 等待分析结果………………")
for ans in ans.res:
    # 将mac的符号替换为能匹配到的格式
    macAddr = str(ans.answer.src)[:8:].replace(":", "-", )
    # 用mac匹配oui
    for oui in oui_list:
        if re.search(macAddr.upper(), oui):
            mac_oui = oui.split('\t', -1)[2].rstrip()
            print(f"\t{ans.answer.psrc}\t{ans.answer.src}\t{mac_oui}")
            # 存入字典
            results[ans.answer.psrc] = [ans.answer.src, mac_oui]
# 写入EXCEL文件
workbook = xlsxwriter.Workbook("./LAN-mac-oui.xlsx")
worksheet = workbook.add_worksheet("data")
row = 0
col = 0
# EXCEL格式定制
worksheet.set_column(col, col, width=20)
worksheet.set_column(col+1, col+1, width=25)
worksheet.set_column(col+2, col+2, width=50)
BOLD = workbook.add_format({"bold": True})
# 写入数据
worksheet.write_string(0, 0, "ip地址", BOLD)
worksheet.write_string(0, 1, "MAC地址", BOLD)
worksheet.write_string(0, 2, "网卡产商", BOLD)
for key, value in results.items():
    result_data = [key, value[0], value[1]]
    worksheet.write_row(row+1, col, result_data)
    row = row + 1
workbook.close()
print("已写入当前文件夹的LAN-mac-oui.xlsx文件")
flag = input("输入任意键退出: ")
