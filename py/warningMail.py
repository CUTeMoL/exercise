import smtplib
import psutil
from email.mime.text import MIMEText
from email.header import Header

def sendWarningMail(mailserver, mailport, sender, receivers, sender_passwd, message):
    subject = 'Machine warning !!'
    message['From'] = Header(sender, 'utf-8')
    message['To'] =  Header(receivers, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    smtp_server = smtplib.SMTP(host=mailserver, port=mailport)
    smtp_server.connect(host=mailserver, port=mailport)
    smtp_server.starttls()
    smtp_server.login(user=sender, password=sender_passwd)
    smtp_server.sendmail(from_addr=sender, to_addrs=receivers, msg=message.as_string())


mailserver = 
mailport = 
sender = 
sender_passwd = 
receivers = 

# 内存警告
if psutil.virtual_memory().percent >= 30:
    message = MIMEText('内存使用率超过30%，达到了{}%'.format(psutil.virtual_memory().percent), 'plain', 'utf-8')
    sendWarningMail(mailserver, mailport, sender, receivers, sender_passwd, message)
# 分区空间警告
for partition in psutil.disk_partitions():
    if psutil.disk_usage(partition.mountpoint).percent >= 50:
        message =  MIMEText('{}分区使用率使用率超过50%，达到了{}%'.format(partition.device, 
        psutil.disk_usage(partition.mountpoint).percent), 'plain', 'utf-8')
        sendWarningMail(mailserver, mailport, sender, receivers, sender_passwd, message)
