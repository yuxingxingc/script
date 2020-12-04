# -*- coding:utf-8 -*-
import sys
import lzma
import os
import zipfile
import shutil
import paramiko
import ipaddress
import time


class Analyse:
    def __init__(self):
        self.arg = sys.argv[:]
        self.interface = []
        self.module = []
        if len(sys.argv) > 1:
            self.host = sys.argv[1]
            self.verify_ip()
            self.username='ute'
            password = input('请输入你的ute密码：')
            self.passwd = password

    def check_arg(self):
        del self.arg[0]
        for i in self.arg:
            if i in CONTAINER:
                print('您输入并且想要查询的是：{}模块'.format(i))
                self.module.append(i)
            elif i in INTERFACE:
                print('您输入并且想要查询的是：{}接口'.format(i))
                self.interface.append(i)
            else:
                return False
        print('Module is {}, interface is {}'.format(self.module, self.interface))
        return self.interface, self.module

    def get_snapshot(self):
        current_dir = os.getcwd()
        dir_file = os.listdir()
        for line in dir_file:
            if line.endswith('.zip'):
                print('The current zip file is {}'.format(current_dir + os.sep + line))
                return current_dir + os.sep + line

    def find_cp_log(self, file):
        check_dir = '.\\test'
        # 创建初始存放的文件夹
        if not os.path.exists(check_dir):
            os.makedirs('.\\test')
        log_dir = os.getcwd() + '\\test'
        # 解压snapshot
        snapshot = zipfile.ZipFile(file)
        snapshot.extractall(path=log_dir)
        snapshot.close()
        # 创建最终存放log的文件夹
        final_log = '.\\test\\logs'
        if not os.path.exists(final_log):
            os.makedirs(final_log)
        second_dir = os.listdir('.\\test')
        for line in second_dir:
            if line.endswith('.zip'):
                print(line)
                sub_zip = '.\\test' + os.sep + line
                each_zip = zipfile.ZipFile(sub_zip)
                each_zip.extractall('.\\test\\logs')
                each_zip.close()
        file_container = os.listdir(final_log)
        result_log = '.\\result'
        if not os.path.exists(result_log):
            os.makedirs(result_log)
        for line in file_container:
            if line.endswith('runtime.zip'):
                print(line)
                result_zip = '.\\test\\logs' + os.sep + line
                shutil.move(result_zip, result_log)
        shutil.rmtree(check_dir)
        log_file = os.listdir(result_log)
        for line in log_file:
            log_zip = '.\\result' + os.sep + line
            zipfile.ZipFile(log_zip).extractall('.\\result')
            os.remove(log_zip)
        log_file = os.listdir(result_log)
        for line in log_file:
            if '_cp_' not in line:
                dele_file = result_log + os.sep + line
                os.remove(dele_file)
        log_file = os.listdir(result_log)
        for line in log_file:
            xz_file = result_log + os.sep + line
            log_name = os.path.splitext(xz_file)[0]
            with lzma.open(xz_file) as f, open(log_name,'wb') as fout:
                print('正在解压 {}'.format(xz_file))
                file_content = f.read()
                fout.write(file_content)
                fout.close()
                f.close()
            print('正在删除 {}'.format(xz_file))
            os.remove(xz_file)
        log_file = os.listdir(result_log)
        for i in log_file:
            print('查询到 {}'.format(i))
        print('完成CP log寻找工作！log存放在.\\test路径下，请查看！')

    def upload_file2remote(self, local_path='', remote_path=''):
        t = paramiko.Transport((self.host,22))
        t.connect(username=self.username, password='noki@123')
        sftp = paramiko.SFTPClient().from_transport(t)
        sftp.put(localpath=local_path, remotepath=remote_path)
        t.close()

    def remove_result(self):
        last_result = os.path.exists('.\\result')
        if last_result:
            print('存在上一次解压的snapshot，正在删除上一次的log！！！')
            shutil.rmtree('.\\result')
        else:
            print('工作目录是干净的，无需其他操作！！')

    def download_file2local(self, remote_path='/tmp/logs.tgz', local_path='.\\logs.tgz'):
        t = paramiko.Transport(sock=(self.host,22))
        t.connect(username=self.username, password='noki@123')
        sftp = paramiko.SFTPClient().from_transport(t, sock=22)
        sftp.get(remotepath=remote_path, localpath=local_path)
        t.close()

    def ute_scp_gnb(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(hostname=self.host, username=self.username, password=self.passwd)
        channel = ssh.invoke_shell()
        channel.settimeout(15)
        channel.send('scp' + '-r' + '/ffs/run/logs' + self.host + '@' + ':' + '/tmp/' + '\n')
        buff = ''
        resp = ''
        while not buff.endswith('$ '):
            resp = channel.recv(9999)
            if not resp.find('\'s password: '):
                print('Error info: Authentication failed')
                channel.close()
                ssh.close()
                sys.exit()
            buff += resp
        print(buff)
        channel.close()
        ssh.close()

    def exec_remote_command(self, cmd):
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        s.connect(hostname=self.host, username=self.username, password=self.passwd)
        stdin, stdout, stderr = s.exec_command(cmd)
        result = stdout.read().decode('utf-8')
        print(result)
        s.close()
        return result

    def verify_ip(self):
#        print(f'主机ip是 {self.host}, 用户名是 {self.username}, 密码是 {self.passwd}')
        try:
            ipaddress.ip_address(self.host)
            print(f'{self.host}是合法IP')
        except Exception as e:
            print('-' * 40, '请检查IP地址格式是否合法', '-' * 40)
            sys.exit()

    def get_gnb_internal_ip(self):
        output = test.exec_remote_command("ssh 192.168.255.1 'cat /etc/hosts'")
        for line in output.split(sep='\n'):
            if 'fct0s1icom' in line:
                asik_slave = line.split(sep=' ')[0].split(sep='\t')[0]
                print(f'* asik slave的ip是{asik_slave}')
            elif 'fsp1s0icom' in line:
                abil_master = line.split(sep=' ')[0]
                print(f'* abil master的ip是{abil_master}')
            elif 'fsp1s1icom' in line:
                abil_slave = line.split(sep=' ')[0]
                print(f'* abil slave的ip是{abil_slave}')
        return [asik_slave, abil_master, abil_slave]

    def asik_scp_logs(self):
        host_list = self.get_gnb_internal_ip()
        log_dir = time.strftime('%Y-%m-%d-%H-%M-log',time.localtime(time.time()))
        self.exec_remote_command(f"ssh 192.168.255.1 'mkdir -p /tmp/{log_dir}/'")
        self.exec_remote_command(f"ssh 192.168.255.1 'scp toor4nsn@{host_list[0]}:/tmp/node_CPNRT00/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(f"ssh 192.168.255.1 'scp toor4nsn@{host_list[0]}:/tmp/node_CPRT00/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(f"ssh 192.168.255.1 'cp /tmp/node_CPCL00/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(f"ssh 192.168.255.1 'cp /tmp/node_CPNB00/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(f"ssh 192.168.255.1 'cp /tmp/node_CPIF00/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(f"ssh 192.168.255.1 'scp toor4nsn@{host_list[1]}:/tmp/node_CPUE20/tmp/*_cp_* /tmp/{log_dir}'")
        self.exec_remote_command(
            f"ssh 192.168.255.1 '[ -d ~ ] && tar czvf /tmp/{log_dir}.tgz /tmp/{log_dir} || echo not_found'")
        self.exec_remote_command(
            f"ssh 192.168.255.1 '[ -d /tmp/{log_dir}.tgz ] && scp /tmp/{log_dir}.tgz ute@{self.host}:~ || echo not_found'")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        start_time = time.time()
        test = Analyse()
    #    test.check_arg()
        test.remove_result()
        file = test.get_snapshot()
        test.find_cp_log(file=file)
        end_time = time.time()
        print(f'CP log 搜索完毕，总共耗时{end_time - start_time}')
    else:
        test = Analyse()
        # test.ute_scp_gnb()
        test.verify_ip()
        test.asik_scp_logs()
        current_dir = os.getcwd() + os.sep + 'log.tgz'
        test.download_file2local(remote_path='/tmp/{log_dir}.tgz', local_path='current_dir')
