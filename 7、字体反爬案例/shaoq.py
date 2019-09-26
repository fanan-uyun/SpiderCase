import requests
import re
import base64
from fontTools.ttLib import TTFont
from pprint import pprint
font = TTFont('131.woff')
# font.saveXML('131.xml')


# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
# }
# url = 'http://shaoq.com/font'
#
# response = requests.get(url,headers=headers).content.decode('utf-8')
# print(response)

# font = TTFont('131.woff')
# font.saveXML('131.ttx')
# font.saveXML('131.xml')
# fontMap = font.getBestCmap()
# print(font.getGlyphOrder())
# mappings = {}
# for k, v in font.getBestCmap().items():
#     print(k,v)
#     if v.startswith('uni'):
#         # :x以十六进制输出,int(数字，几进制）默认10进制
#         print(chr(int(v[3:], 16)))
#         # mappings['&#x{:x};'.format(k)] = chr(int(v[3:], 16))
#         # mappings['&#x{:x};'.format(k)] = v
#         mappings[v] = '&#x{:x};'.format(k)
#     else:
#         mappings['&#x{:x};'.format(k)] = v
# pprint(mappings)

# print(chr(int('e963',16)))
# print(font['cmap'].tables[2].ttFont.getReverseGlyphMap())
# print(font['cmap'].tables[2].ttFont.tables['cmap'].tables[1].cmap)
# newMap = {}
# for key in fontMap.keys():  # {38006:'glyph00002',...}
#     value = fontMap[key]  # value：0002 # key: 38006 fontMap[key]:glyph00002
#     key = hex(key)  # 10进制整数转换成16进制,0x9a4b
#     newMap[key] = value
# print(newMap)
# print(font.getGlyphID())
def parse_font():
    font1 = TTFont('131.woff')
    keys, values = [], []
    for k, v in font1.getBestCmap().items():
        print(k,v)
        if v.startswith('uni'):
            keys.append(eval("u'\\u{:x}".format(k) + "'"))
            values.append(chr(int(v[3:], 16)))
        else:
            keys.append("&#x{:x}".format(k))
            values.append(v)
    print(keys, values)
    return dict(zip(keys, values))
# a = parse_font()
# print(a)
# print(chr(5242))--->我
# print(ord('我'))#--->int

