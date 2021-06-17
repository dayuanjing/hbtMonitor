# -*- coding: utf-8 -*-
from CurrentMethod import *


class MinerStorage:
    # 记录第一个被创建对象的引用
    instance = None
    # 记录是否执行过初始化动作
    init_flag = False

    def __new__(cls, *args, **kwargs):
        # 1.判断类属性是否为空对象，若为空说明第一个对象还没被创建
        if cls.instance is None:
            # 2.对第一个对象没有被创建，我们应该调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        # 3.把类属性中保存的对象引用返回给python的解释器
        return cls.instance

    def __init__(self, shell, mount_file, log_file, access_token):
        # 1.判断是否执行过初始化动作,若执行过，直接return
        self.shell = shell
        self.mount_file = mount_file
        self.log_file = log_file
        self.access_token = access_token

        if self.init_flag:
            return
        # 2.若没执行过，再执行初始化,
        # 执行shell命令，将mount信息写入文件
        msg = os.popen(self.shell).readlines()
        if not os.path.isfile(self.mount_file):
            self.mount = open(self.mount_file, 'w')
        # 这里open文件，需要通过类调用mount属性(MountCheck.mount)，不能使用self.mount,第一次执行的时候会报错
        with open(self.mount_file, 'w+') as m:
            for line in msg:
                cmd = "ls " + line.split()[1]
                exec_status = exec_command(cmd)
                if exec_status == "1":
                    title = "新故障: " + line.split()[0]
                    msg = message(title, get_ip(), exec_status, line.split()[0])
                    contents = sending_dingding(self.access_token, msg)
                    write_log(self.log_file, contents)
                newline = ";".join(line.split()) + ";" + exec_status + "\n"
                m.write(newline)
        # 修改类属性的标记
        self.init_flag = True

    # 读取 initMount.txt文件，返回数组
    def read_mount(self):
        new_list = []
        # 这里open文件，需要通过类调用mount属性(MountCheck.mount)，不能使用self.mount，第一次执行的时候会报错
        with open(self.mount_file, 'r') as file_obj:
            file_list = file_obj.readlines()
            # 去除字符出的\n字符
            for i in range(0, len(file_list)):
                file_list[i] = file_list[i].rstrip('\n')
            # 字符串按;分割成列表加入数组中
            for i in range(0, len(file_list)):
                new_list.append(file_list[i].split(";"))
        return new_list

    # 传入数组，检查文件系统，并更新状态
    def check_mount(self, *mount_array):
        for ma in mount_array:
            for m in range(0, len(ma)):
                cmd = "ls " + ma[m][1]
                # 原始状态
                status = ma[m][2]
                # ls 命令执行后的状态
                exec_status = exec_command(cmd)
                if status == "1" and exec_status == "1":
                    title = "已发送故障: " + ma[m][0]
                    write_log(self.log_file, "已发送告警，无需重复发送\t故障信息头:" + title)
                if status == "0" and exec_status == "1":
                    title = "新故障: " + ma[m][0]
                    msg = message(title, get_ip(), exec_status, ma[m][0])
                    contents = sending_dingding(self.access_token, msg)
                    write_log(self.log_file, contents)
                if status == "1" and exec_status == "0":
                    title = "故障恢复: " + ma[m][0]
                    msg = message(title, get_ip(), exec_status, ma[m][0])
                    contents = sending_dingding(self.access_token, msg)
                    write_log(self.log_file, contents)

                # 更新状态
                with open(self.mount_file, 'r') as f:
                    lines = f.readlines()
                with open(self.mount_file, 'w') as f_w:
                    for line in lines:
                        # 判断需要变更的字符串是否在打开文件的这一行中
                        if ma[m][0] in line:
                            line = line.replace(line.split(';')[2], exec_status + "\n")
                        f_w.write(line)
