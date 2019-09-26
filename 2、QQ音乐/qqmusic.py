import os
import json
import requests


headers = {
    'Origin': 'https://y.qq.com',
    'Referer': 'https://y.qq.com/portal/search.html',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

def get_music_info():
    music_info_list = []
    name = input('请输入歌手或歌曲：')
    page = input('请输入页码：')
    num = input('请输入当前页码需要返回的数据条数：')
    url = f'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p={page}&n={num}&w={name}'
    response = requests.get(url,headers=headers).text
    # 将其切分为json字符串形式
    music_json = response[9:-1]
    # json转字典
    music_data = json.loads(music_json)
    # print(music_data)
    music_list = music_data['data']['song']['list']
    for music in music_list:
        music_name = music['songname']
        singer_name = music['singer'][0]['name']
        songmid = music['songmid']
        media_mid = music['media_mid']
        music_info_list.append((music_name,singer_name,songmid,media_mid))
        # print(music_name,singer_name,songmid,media_mid)
    return music_info_list

def get_purl(music_info_list):
    music_data = []
    # 提取songid
    for music in music_info_list:
        music_name = music[0]
        singer_name = music[1]
        songmid = music[2]
        # media_mid = music[3]
        # 这里uid 可以不传
        url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data={"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"703417739","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"703417739","songmid":["%s"],"songtype":[0],"uin":"1094013271","loginflag":1,"platform":"20"}},"comm":{"uin":"1094013271","format":"json","ct":24,"cv":0}}'%songmid
        response = requests.get(url,headers=headers).json()
        purl = response['req_0']['data']['midurlinfo'][0]['purl']
        full_media_url = 'http://dl.stream.qqmusic.qq.com/' + purl
        # print(music_name,singer_name,full_media_url)
        music_data.append(
            {
                'music_name': music_name,
                'singer_name': singer_name,
                'full_media_url': full_media_url
            }
        )
    return music_data

def save_music_mp3(music_data):
    if not os.path.exists('歌曲下载'):
        os.mkdir('歌曲下载')
    for music in music_data:
        music_name = music['music_name']
        singer_name = music['singer_name']
        full_url = music['full_media_url']
        music_response = requests.get(full_url,headers=headers).content
        with open('歌曲下载/%s-%s.mp3'%(music_name,singer_name),'wb')as fp:
            fp.write(music_response)
            print('[%s]保存成功！'%music_name)



if __name__ == '__main__':
    music_info_list = get_music_info()
    music_data = get_purl(music_info_list)
    save_music_mp3(music_data)