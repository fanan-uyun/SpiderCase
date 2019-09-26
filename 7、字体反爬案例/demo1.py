from fontTools.ttLib import TTFont
from pprint import pprint
from 字体反爬.demo import font_dic
import requests

# '&#xf1db;': 'unif1db',
def font_parse():
    font = TTFont('131.woff')
    mappings = {}
    for k, v in font.getBestCmap().items():
        print(k,v)
        if v.startswith('uni'):
            # :x以十六进制输出,int(数字，几进制）默认10进制
            # print(chr(int(v[3:], 16)))
            # mappings['&#x{:x};'.format(k)] = chr(int(v[3:], 16))
            mappings['&#x{:x};'.format(k)] = v
    return mappings
    # pprint(mappings)

font_parse()

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
# }
# url = 'http://shaoq.com/font'
#
# response = requests.get(url,headers=headers).content.decode('utf-8')
# print(response)
# mappings = font_parse()
# for k,v in mappings.items():
#     print(k,v)
#     if k in response:
#         font_par = font_dic[v]
#         response = response.replace(k,font_par)
# print(response)
#
#
# font_url = 'http://shaoq.com/static/fonts/f7ad95972dab792cc51c548a9c958d1a.woff'
# res = requests.get(font_url,headers=headers).content
# with open('123.woff','wb')as fp:
#     fp.write(res)

