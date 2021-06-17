# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import shlex
import subprocess
import time
import requests


def write_log(log_path, log_info):
    """
    写日志
    :param log_path: 日志文件路径
    :param log_info: 写入内容
    :return:
    """
    tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if not os.path.isfile(log_path):
        f = open(log_path, 'a+')
    with open(log_path, 'a+') as fp:
        fp.write(tm + "\t" + log_info + "\n")


def get_ip():
    """
    获取IP地址
    :return: 返回ip地址
    """
    # 使用os.popen()函数执行ifconfig命令，结果为file对象，将其传入cmd_file保存
    cmd_file = os.popen('ifconfig')
    # 使用file对象的read()方法获取cmd_file的内容
    cmd_result = cmd_file.read()
    # 构造用于匹配IP的匹配模式,获取的IP是以10段开头的
    pattern = re.compile(r'(inet.*?)(10.\d{1,3}.\d{1,3}.\d{1,3})')
    # 使用re模块的findall函数匹配
    ip_list = re.findall(pattern, cmd_result)
    return ip_list[0][1]


def exec_command(cmd, timeout=5):
    """
    判断命令执行是否超时
    :param cmd: 要执行的命令
    :param timeout: 最长等待时间，单位：秒
    poll() is not None表示进程不在运行，如果在运行再去判断是否执行超时
    terminate() 终止进程发送SIGTERM信号
    :return: status 状态 超时返回字符串1，正常返回0
    """
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    status = ""
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            status = "1"
            p.terminate()
        else:
            status = "0"
        time.sleep(0.1)
    return status


def exec_cmd_result(cmd, cwd=None, timeout=None, shell=False):
    """
    执行命令，返回执行结果，communicate()返回一个元组：(stdoutdata, stderrdata)
    :param cmd: 主要执行的命令
    :param cwd: 运行命令时，更改路径
    :param timeout: 超时时间
    :param shell: 是否通过shell运行
    :return: return_code
    """
    if shell:
        cmd_string_list = cmd
    else:
        cmd_string_list = shlex.split(cmd)

    end_time = 0
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    sub = subprocess.Popen(cmd_string_list, cwd=cwd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=shell)
    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception('Timeout: {}'.format(cmd))
    return sub.communicate()


def sending_dingding(access_token, msg):
    """
    # 发送钉钉告警,返回成功失败字符串
    :param access_token: 钉钉token
    :param msg: 发送消息
    :return: return_msg  钉钉返回信息
    """
    return_msg = ""
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=" + access_token
    headers = {"Content-Type": "application/json ;charset=utf-8"}
    request_data = {
        "msgtype": "markdown",
        "markdown": {
            "title": '黑犇监控',
            "text": msg
        },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    }
    # 把json转变为字符串格式数据
    send_msg = json.dumps(request_data)
    # 发送post请求，请求钉钉接口
    response = requests.post(url=webhook, headers=headers, data=send_msg)
    # 返回写入日志的字符串数据
    contents = json.loads(response.content.decode())
    if contents["errcode"] == 0:
        return_msg = "钉钉消息发送成功\t返回信息:" + str(contents) + "\t" + msg
    else:
        return_msg = "钉钉消息发送失败\t返回信息:" + str(contents) + "\t" + msg
    return return_msg


def message(title, ip, status, question):
    """
    # 钉钉告警信息
    :param title: 标题
    :param ip:  服务器IP
    :param status: 状态
    :param question: 详情
    :return: msg
    """
    event_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg = "### <font color=#FF000 size=4 face=\"微软雅黑\">" + title + \
          "</font>\n\n> **主机IP:** " + ip + \
          "\n\n> **报警时间:** " + event_time + \
          "\n\n> **当前状态:** " + status + \
          "\n\n> **问题详情:** " + question + "\n\n"
    return msg


# 间隔时间
def sleep_time(hour, minute, sec):
    return hour * 3600 + minute * 60 + sec
