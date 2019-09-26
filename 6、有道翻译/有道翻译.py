import requests
import json
import time
import hashlib
import random

def is_json(file):
    try:
        json.loads(file)
    except Exception as e:
        return False
    return True

def md5_encryption(value):
    md5 = hashlib.md5()
    md5.update(bytes(value,encoding='utf-8'))
    return md5.hexdigest()

def youdaofanyi(word,salt,ts,sign):
    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    proxies_list = [
                # {
                #     'http':'http://218.66.253.144:8800',
                #     'https':'https://111.231.92.21:8888'
                # },
                {
                    'http': 'http://183.146.29.224:8888',
                },
                {
                    'http': 'http://118.31.61.70:3128',
                },
                {
                    'http': 'http://113.121.40.249:808',
                },
            ]
    proxies = random.choice(proxies_list)
    # print(proxies)
    data = {
        'i':word,
        'from':'AUTO',
        'to':'AUTO',
        'smartresult':'dict',
        'client':'fanyideskweb',
        'salt':salt,
        'sign':sign,
        'ts':ts,
        'bv':'6ba427a653365049d202e4d218cbb811',
        'doctype':'json',
        'version':'2.1',
        'keyfrom':'fanyi.web',
        'action':'FY_BY_CLICKBUTTION'
    }

    headers = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        # 'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Content-Length':'233' + str(len(word)),
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie':'OUTFOX_SEARCH_USER_ID=130988169@10.168.8.61; JSESSIONID=aaaxUs9cW7z8cbRbfGlZw; OUTFOX_SEARCH_USER_ID_NCOO=1568055972.6077068; ___rl__test__cookies=1566784752546',
        'Host':'fanyi.youdao.com',
        'Origin': 'http://fanyi.youdao.com',
        'Referer': 'http://fanyi.youdao.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }

    response = requests.post(url,data=data,headers=headers,proxies=proxies).content.decode('utf-8')
    is_true = is_json(response)
    print(is_true)
    if is_true:
        pass
    else:
        print("输出的不是json格式")
        return None

    response_json = json.loads(response)
    print(response_json)

    # 对结果进行字符串拼接
    info = word + ':'
    # 取出翻译后的结果
    try:
        explain_list = response_json.get('smartResult').get('entries')

        for explain in explain_list:
            explain.strip()
            info += explain.strip() + '\n'
            print(info)
    except:
        explain = response_json.get('translateResult')[0][0].get('tgt')
        info += explain.strip() + '\n'
        print(info)

    with open('fanyi.txt','a',encoding='utf-8')as fp:
        fp.write(info)
        fp.write('\n')


# 15667907053339
# 15667982340878
# 1566790705333
# 1566798288831

if __name__ == '__main__':
    while True:
        word = input("请输入要查找的单词：")
        # 优化后时间戳
        salt = int(time.time()*10000)
        # # 优化后时间戳减一位
        ts = int(time.time()*1000)
        # 拼接生成需要转换成MD5的字符串
        value = "fanyideskweb" + word + str(salt) + "n%A-rKaT5fb[Gy?;N5@Tj"
        # 生成MD5
        sign = md5_encryption(value)
        # print(sign)
        youdaofanyi(word, salt, ts, sign)
