from scapy.all import *
import psutil
import IPy
import re
with open("/home/lxw/oui.txt", "r", encoding='utf8') as f:
    oui_list = f.readlines()
net_devices = {}
scan_range = {}
for if_name in psutil.net_if_addrs():
    for i in range(len(psutil.net_if_addrs()[if_name])):
        if psutil.net_if_addrs()[if_name][i].family == 2:
            net_devices[if_name] = {
				"address": psutil.net_if_addrs()[if_name][i].address,
				"netmask": psutil.net_if_addrs()[if_name][i].netmask
			}
for net_device in net_devices:
    ipAddress = IPy.IP(net_devices[net_device]["address"])
    net_mask = net_devices[net_device]["netmask"]
    ips = IPy.IP(ipAddress).make_net(net_mask)
    scan_range[net_device] = ips
print(f"共有{len(scan_range)}张网卡:")
for index, scan_device in enumerate(scan_range):
    print("\t", index+1, scan_device)
scan_device_name = input(f"输入需要查询的网卡名称: ")
scan_ip_range = str(scan_range[scan_device_name])
ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=scan_ip_range), timeout=2)
print("正在扫描网段: ", scan_range[scan_device_name])
for ans in ans.res:
    macAddr = str(ans.answer.src)[:8:].replace(":", "-", )
    for oui in oui_list:
        if re.search(macAddr.upper(), oui):
            mac_oui = oui.split('\t', -1)[2].rstrip()
            print(f"\t{ans.answer.psrc}\t{ans.answer.src}\t{mac_oui}")
