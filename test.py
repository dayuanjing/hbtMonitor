import json
import time


class TestLotusDredge:
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
        "Data": "qB1bMZUxVKGrLj+crTbMvYIx0rQxaHEsa/TGB9R6IPU7+8MrurIw4DhlC9AmnqNpGAUAQaZ+1R3N0Ijz9pDEINWERSNC5eAdfv6m4yCTxLWu8GTXMpxiqyWhcEYJFFvK"
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
        "Params": "gg9YwISuVf9Q4aZPwOfgXCHhq+QVfesmtfAGQe5pFuvEnHyP4fplj2ZO3hQGDBl/OKogAKhGEbIizQVtvvuJsIArSYrq5gp0v4zbatgdJV96+VIQyUDVNdYUNLVCFrEyFptcWRkNepqvkYVBvRrbLIGYvJQzZl+dOrnyKyLuRxhm88NCKe5WjyzpGjH9RRmIU/oGQaKFj8PJVhoBNNuB655W78Q/E2/k0oPTjN0lAeuv/HICZxYhmKDCNeORBRDW9qkFXQ=="
      },
      "Signature": {
        "Type": 2,
        "Data": "t3Wr3IZ+CV7k+JE+sC6jN3lP6N5BccJTDwqlb8uWoB7in9Aa0Jl7uc8OeVxPtJOwACjTkMG6LF1Pe3NYysFvumPN5toLz2ykkukELnfKnP+mU205PgJhgYnhv889T0Xo"
      }
    }
    {
      "Message": {
        "Version": 0,
        "To": "t06135",
        "From": "t3qn5nrwpj7tz4djphqsvmwpv7l2jfcdw6ty37qktshkpshsugom6fwb2azxzhvanxqvzrtma4j5fsregcer5q",
        "Nonce": 51,
        "Value": "2464915703310213",
        "GasPrice": "1",
        "GasLimit": 206024970,
        "Method": 7,
        "Params": "ghBYwIY/dGCd4hLOLvmOvj4L5e6Vx8HtvxjpYWvIpPsnhjgDVyVUetPVVqtlN6I/kpDE+aVODFY5BcNbjNMrPXc2BxlN7zuC0cpfLsZY4OtQBtZ/SORVQtOnrs2srvtMc7ZZIQSSdemtsClM+odLSClsghTLkZxcv8oQ363IxUx5STlBCSWzb/cVbdDHNxsRuhG9Z6p0/HLq+I5/xqO/NKq7unJuyGOhVN/n17m7fVWUsAcdVWdd31ZmU3H4wA4CvwPsag=="
      },
      "Signature": {
        "Type": 2,
        "Data": "riciMJum+dDbqWFH3gzsq15yC/apfPgmNHaKSaUtUlXZGc5zGhAzQGKUJZm3Y9+fDgGDULaYHUpbVJrGudj6d8cbF79jWgtMT+JFTuNCuBS9BZVUfQhLP9AIVrZIhxI0"
      }
    }
    '''

    # 间隔时间
    def sleep_time(hour, minute, sec):
        return hour * 3600 + minute * 60 + sec

    def get_nonce():
        nonce_list = []
        string = TestLotusDredge.json_str.replace("\n", "").replace(" ", "").replace("}{", "};{")
        for item in string.split(';'):
            data = json.loads(item)
            nonce = data['Message']['Nonce']
            nonce_list.append(nonce)
        return nonce_list

    def test_dredge(*nonce_list):
        string = TestLotusDredge.json_str.replace("\n", "").replace(" ", "").replace("}{", "};{")
        for item in string.split(';'):
            data = json.loads(item)
            gas_limit = data['Message']['GasLimit']
            dredge_from = data['Message']['From']
            nonce = data['Message']['Nonce']
            if nonce in nonce_list[0]:
                dredge_cmd = "cd /root/hlm-miner/script/lotus/lotus-user && " \
                             "export PATH=/root/hlm-miner/bin/:bin:$PATH && " \
                             "export lotusrepo=/data/sdb/lotus-user-1/.lotus && " \
                             "export filrepo=/data/sdb/lotus-user-1/.lotusstorage && " \
                             "export PRJ_ROOT=/root/hlm-miner && " \
                             "./lotus.sh mpool replace --really-do-it --gas-feecap 12000000000 --gas-limit " \
                             + str(gas_limit) + " --gas-premium 130000 " + dredge_from + ' ' + str(nonce)

                print(dredge_cmd)


if __name__ == '__main__':
    second = TestLotusDredge.sleep_time(0, 0, 5)
    while True:
        nonce_list = TestLotusDredge.get_nonce()
        time.sleep(second)
        TestLotusDredge.test_dredge(nonce_list)
