import requests

headers = {
    'Origin': 'https://y.qq.com',
    'Referer': 'https://y.qq.com/portal/singer_list.html',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

singer_all = []
for i in range(300):
    print('页码：',i+1)
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data={"comm":{"ct":24,"cv":0},"singerList":{"module":"Music.SingerListServer","method":"get_singer_list","param":{"area":-100,"sex":-100,"genre":-100,"index":-100,"sin":%s,"cur_page":%d}}}'%(i*80,i+1)

    response = requests.get(url,headers=headers).json()
    singer_list = response['singerList']['data']['singerlist']
    for singer in singer_list:
        singer_name = singer['singer_name']
        singer_all.append(singer_name)

print(len(singer_all))