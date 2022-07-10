import smtplib
import psutil
from email.mime.text import MIMEText
from email.header import Header

def warning_mail(mail_server, mail_port, from_mailbox, sender_name, to_mailbox, receiver_list, sender_password, messages):
    subject = 'Machine warning !!'
    messages['From'] = Header(sender_name, 'utf-8')
    messages['To'] =  Header(receiver_list, 'utf-8')
    messages['Subject'] = Header(subject, 'utf-8')
    smtp_server = smtplib.SMTP(host=mail_server, port=mail_port)
    smtp_server.connect(host=mail_server, port=mail_port)
    smtp_server.starttls()
    smtp_server.login(user=from_mailbox, password=sender_password)
    smtp_server.sendmail(from_addr=from_mailbox, to_addrs=to_mailbox, msg=messages.as_string())


mailServerName =
mailServerPort =
fromMail =
sender =
senderPasswd =
toMail =
receivers =

# 内存警告
if psutil.virtual_memory().percent >= 30:
    message = MIMEText('内存使用率超过30%，达到了{}%'.format(psutil.virtual_memory().percent), 'plain', 'utf-8')
    warning_mail(mailServerName, mailServerPort, fromMail, sender, toMail, receivers, senderPasswd, message)
# 分区空间警告
for partition in psutil.disk_partitions():
    if psutil.disk_usage(partition.mountpoint).percent >= 50:
        message =  MIMEText('{}分区使用率使用率超过50%，达到了{}%'.format(partition.device,
        psutil.disk_usage(partition.mountpoint).percent), 'plain', 'utf-8')
        warning_mail(mailServerName, mailServerPort, fromMail, sender, toMail, receivers, senderPasswd, message)
