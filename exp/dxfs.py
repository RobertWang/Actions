import threading
import queue
import random
import base64
import bz2
import json
import time
import sys
import os
import requests
import warnings
from requests.packages import urllib3
# 关闭警告
urllib3.disable_warnings()
warnings.filterwarnings('ignore')


# 定义线程数量
WORKER_THREADS_NUM = int(os.getenv('THREADS_NUM', 0) or 8)
print(f"工作线程数量设置为 {WORKER_THREADS_NUM}")


# 定义用户列表
USER_TABLE = os.environ.get("SMS_LIST")
decom_data = base64.b64decode(USER_TABLE)
decom_data = bz2.decompress(decom_data).decode('utf-8')
x = json.loads(decom_data)
USER_TOTAL = len(x)

# 随机打乱
random.shuffle(x)


# 创建一个队列来存储任务
TASK_QUEUE = queue.Queue()


# 定义一个工作线程，用来执行任务
def worker():
    while True:
        # 从队列中获取任务
        task = TASK_QUEUE.get()

        # 正式执行时，调用发送短信函数
        send_sms_code(task['mobile'])
        # 标记任务完成
        TASK_QUEUE.task_done()


# 发送短信函数
def send_sms_code(mobile):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Dnt': '1',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = 'NWQ0OTU3ODgxOGUwMjFiMzFmOWNjNzMyZDM5NjYyNWI='
    md5 = base64.b64decode(data).decode('utf-8')
    data = '44CQ6YO95LiN6LWWMjRo6Ieq5Yqp5rSX6L2m44CR5bCK5pWs55qE55So5oi377yM5oKo55qE6aqM6K+B56CB5pivMDAwMDAwIO+8jOivt+S6jjXliIbpkp/lhoXmraPnoa7ovpPlhaXjgILlpoLpnZ7mnKzkurrmk43kvZzvvIzor7flv73nlaXmraTnn63kv6HjgII='
    content = base64.b64decode(data).decode('utf-8')
    data = 'aHR0cHM6Ly9hcGkuc21zYmFvLmNvbS9zbXM/dT1kYmxxY2Z3'
    api = base64.b64decode(data).decode('utf-8')
    api = f"{api}&p={md5}&m={mobile}&c={content}"

    res = requests.get(api, headers=headers, verify=False)
    if res.status_code == 200:
        print('√', end='')
    else:
        print('x', end='')

    return True


# 检查当前 ip 地址和归属地
def check_my_ip():
    url = 'https://ipinfo.io'
    res = requests.get(url, verify=False)
    print(f"请求地址: {url}, 耗时: {res.elapsed.microseconds} 状态码: {res.status_code} 字符编码: {res.apparent_encoding} 响应内容: {res.json()}")

    if res.status_code == 200:
        info = res.json()
        print(f"当前 IP 地址: {info['ip']} @ {info['city']}, {info['country']}")
        return True
    print(f"网络请求失败！中断退出执行...请检查网络或代理是否正常")
    sys.exit()


''' 程序入口 '''
if __name__ == '__main__':
    # 验证当前 ip 地址和归属地，确认是否继续执行
    confirm = check_my_ip()
    print(f'程序开始 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    cost = time.time()
    # 创建并启动多个工作线程
    for i in range(WORKER_THREADS_NUM):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    # 添加任务到队列
    for inx in range(USER_TOTAL):
        mobile = x[inx]
        inx += 1
        # 添加任务到队列
        TASK_QUEUE.put({'inx': inx, 'mobile': mobile})

    # 等待队列中的任务全部完成
    TASK_QUEUE.join()
    cost = time.time() - cost
    print(f"所有任务共 {USER_TOTAL} 条短信发送完成! 总共耗时 {cost:.2f} 秒")
