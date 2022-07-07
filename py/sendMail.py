import smtplib
user_mail = "qqmail@qq.com" # 发送的
to_user_mail = "qqmail@qq.com" # 接受的
authorization_code = 
subject = "主题"
text = "文本内容"
body = "\n".join([
    "From: {}".format(user_mail),
    "To: {}".format(to_user_mail),
    "Subject: {}".format(subject),
    "",
    text
])
smtp_server = smtplib.SMTP(host='smtp.qq.com', port=587) # 各个邮箱的端口可能不一样，qq是587
smtp_server.connect(host='smtp.qq.com', port=587)
smtp_server.starttls() # 加密传输
smtp_server.login(user=user_mail, password=authorization_code) # 不是密码是授权码
smtp_server.sendmail(from_addr=user_mail, to_addrs=to_user_mail, msg=body)
smtp_server.quit()
