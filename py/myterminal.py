import paramiko

mymachine_ip = []
mymachine_port = 22
print("---sftp传输文件---")
trans=paramiko.Transport((mymachine_ip,mymachine_port))
trans.connect(username="lxw",password="passwd")
sftp=paramiko.SFTPClient.from_transport(trans)
sftp.get("/home/lxw/access.log.1","e:/tmp/accesslog.txt") # 把对方机器的/etc/fstab下载到本地为/tmp/fstab(注意不能只写/tmp,必须要命名)
sftp.put("e:/tmp/tmp.txt","/home/lxw/tmp.txt") # 本地的上传,也一样要命令
trans.close()
print("---sftp传输文件完成---")

# 远程执行命令
print("---远程传命令---")
ssh = paramiko.SSHClient()
private_key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
# ssh.connect(hostname=mymachine_ip, port=22, username="lxw", pkey=private_key)
ssh.connect(hostname=mymachine_ip, port=mymachine_port, username="lxw", password="passwd")
stdin, stdout, stderr = ssh.exec_command("touch /home/lxw/123")
# 获取返回的结果
cor_res = stdout.read()
err_res = stderr.read()
if cor_res:
    result = cor_res
else:
    result = err_res
print(result.decode())
ssh.close()
print("---远程传命令完成---")
