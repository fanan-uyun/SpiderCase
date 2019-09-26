import requests

import json

import os

import threading

#发送请求获取信息

def get_response(url):

    headers = {

        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

    }

    response = requests.get(url=url, headers=headers).content

    return response



#保存文件

def save_mp3(music_name,res,word):

    filePath = os.path.join(os.getcwd(), './mp3/' + word)

    if not os.path.exists(filePath):

        print('路径不存在')

        os.makedirs(filePath)

        print('创建成功')

        with open('./mp3/' + word + "/" + music_name + ".m4a", "wb") as file:

            file.write(res)

    else:

        with open('./mp3/' + word + "/" + music_name + ".m4a", "wb") as file:

            file.write(res)



#发送请求

def send_request():

    word = 'exodus'

    res1 = requests.get(

        'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&lossless=0&flag_qc=0&p=1&n=20&w=' + word)

    jm1 = json.loads(res1.text.strip('callback()[]'))

    list_url = []

    re = jm1['data']['song']['list']

    for j in re:

        try:

            list_url.append((j['songmid'], j['songname'].replace('/',''), j['singer'][0]['name']))

        except:

            print('wrong')

    for i in list_url:

        print("开始下载 %s" %i[1])

        res = get_response("http://ws.stream.qqmusic.qq.com/C100"+i[0]+".m4a?fromtag=0")

        #save_mp3(i[1],res,word)

        thr = threading.Thread(target=save_mp3, args=(i[1],res,word))

        # 启动线程

        thr.start()

        print("下载完成")

    print("done")

send_request()