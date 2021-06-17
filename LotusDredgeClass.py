# -*- coding: utf-8 -*-
import json
import re
from CurrentMethod import exec_cmd_result, get_ip, message, sending_dingding, write_log


class LotusDredge:
    json_str = '''
        {
          "Message": {
            "Version": 0,
            "To": "t05503",
            "From": "t3qcafrncru6kxwcg25eiowrwmfjmuej7ldtkdt3knzwdrkjvmu72iyzh2zykss3hpgoolbyucndblpyeuyz4a",
            "Nonce": 1,
            "Value": "1614458653484361323",
            "GasPrice": "1",
            "GasLimit": 21680398,
            "Method": 6,
            "Params": "igMYRdgqWCkAAYLiA4HoAiB1P55l0Sbwur5RdLmMEg4FewUFo9VHc0cyyNn9W9zLbDkBT4AaABe0rfQAAAA="
          },
          "Signature": {
            "Type": 2,
            "Data": "qB1bMZUxVKGrLj+crTbMvYIx0rQxaHEsa/TGB9R6IPU7+8MrurIw4DhlC9AmnqNpGAUAQaZ+1R3N0Ijz9pDEINWK"
          }
        }
        {
          "Message": {
            "Version": 0,
            "To": "t06135",
            "From": "t3qn5nrwpj7tz4djphqsvmwpv7l2jfcdw6ty37qktshkpshsugom6fwb2azxzhvanxqvzrtma4j5fsregcer5q",
            "Nonce": 50,
            "Value": "2464915703310213",
            "GasPrice": "1",
            "GasLimit": 206024970,
            "Method": 7,
            "Params": "gg9YwISuVf9Q4aZPwOfgXCHhq+QVfesmtfAGQe5pFuvEnHyP4fplj2ZO3hQGDBl/OKogAKhGEbIiz"
          },
          "Signature": {
            "Type": 2,
            "Data": "t3Wr3IZ+CV7k+JE+sC6jN3lP6N5BccJTDwqlb8uWoB7in9Aa0Jl7uc8OeVxPtJOwACjTkMG6LF1Pe3NYysFvumP"
          }
        }
    '''

    def __init__(self, lotus_cmd, log_file, access_token):
        self.lotus_cmd = lotus_cmd
        self.log_file = log_file
        self.access_token = access_token

    def get_nonce(self):
        nonce_list = []
        result_json = exec_cmd_result(self.lotus_cmd, shell=True)
        gaslimit = re.findall('GasLimit', result_json[0])
        if result_json[1] is None and gaslimit:
            new_str = result_json[0].replace("\n", "").replace(" ", "").replace("}{", "};{")
            for item in new_str.split(';'):
                data = json.loads(item)
                nonce = data['Message']['Nonce']
                nonce_list.append(nonce)
        return nonce_list

    # lotus疏通
    def dredge(self, *nonce_list):
        title = "新故障: Lotus堵塞"
        # 获取服务器IP
        ip = get_ip()

        result_json = exec_cmd_result(self.lotus_cmd, shell=True)
        gaslimit = re.findall('GasLimit', result_json[0])
        # gaslimit = re.findall('GasLimit', LotusDredge.json_str)

        if result_json[1] is None and gaslimit:
            # 在多个json字符串之间增加分隔符; 方便切割和序列化每条json字符串
            # new_str = LotusDredge.json_str.replace("\n", "").replace(" ", "").replace("}{", "};{")
            new_str = result_json[0].replace("\n", "").replace(" ", "").replace("}{", "};{")
            for item in new_str.split(';'):
                data = json.loads(item)
                gas_limit = data['Message']['GasLimit']
                dredge_from = data['Message']['From']
                nonce = data['Message']['Nonce']
                # 判断这次nonce是否在第一次nonce列表内
                if nonce in nonce_list[0]:
                    dredge_cmd = "cd /root/hlm-miner/script/lotus/lotus-user && " \
                                 "export PATH=/root/hlm-miner/bin/:bin:$PATH && "\
                                 "export lotusrepo=/data/sdb/lotus-user-1/.lotus && " \
                                 "export filrepo=/data/sdb/lotus-user-1/.lotusstorage && " \
                                 "export PRJ_ROOT=/root/hlm-miner && " \
                                 "./lotus.sh mpool replace --really-do-it --gas-feecap 12000000000 --gas-limit " \
                                 + str(gas_limit) + " --gas-premium 130000 " + dredge_from + ' ' + str(nonce)
                    out = exec_cmd_result(dredge_cmd, shell=True)
                    msg = message(title, ip, "已执行疏通脚本，脚本返回信息：\nstdout：" + out[0], "GasLimit：" + str(gas_limit)
                                  + "\nNonce：" + str(nonce))
                    contents = sending_dingding(self.access_token, msg)
                    write_log(self.log_file, contents)
                    write_log("/opt/hbtMonitor/dredge.log", str(data))
        else:
            write_log(self.log_file, "hlm-miner执行失败：" + result_json[0])






