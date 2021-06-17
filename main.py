# -*- coding: utf-8 -*-
import sys
import time
from MinerStorageClass import MinerStorage
from LotusDredgeClass import LotusDredge
from CurrentMethod import sleep_time

if __name__ == '__main__':
    # 钉钉token
    access_token = "9d754a4330103e27967449453f95a2609dc87eb67aa7a960e69db356a1161972"
    # 记录钉钉发送日志
    log_file = "/opt/hbtMonitor/send.log"
    second = sleep_time(0, 0, 30)

    arg = sys.argv[1]
    if arg == "ld":
        lotus_cmd = "cd /root/hlm-miner/script/lotus/lotus-user && export PATH=/root/hlm-miner/bin/:bin:$PATH"  \
              "export lotusrepo=/data/sdb/lotus-user-1/.lotus && " \
              "export filrepo=/data/sdb/lotus-user-1/.lotusstorage && " \
              "export PRJ_ROOT=/root/hlm-miner && "  \
              "./lotus.sh mpool pending --local"

        ld = LotusDredge(lotus_cmd, log_file, access_token)
        while True:
            # 执行第一次lotus_cmd，获取nonce列表
            nonce_list = ld.get_nonce()
            time.sleep(second)
            # 执行第二次lotus_cmd，判断这次nonce是否在第一次nonce列表内
            ld.dredge(nonce_list)

    if arg == "ms":
        # 执行的shell命令
        shell = "mount -l |grep mnt |awk -F'[ ]' '{print $1,$3}'"
        # 初始化写入文件
        mount_file = "/opt/hbtMonitor/init_storage.txt"
        ms = MinerStorage(shell, mount_file, log_file, access_token)
        while True:
            time.sleep(second)
            mount_list = ms.read_mount()
            ms.check_mount(mount_list)
