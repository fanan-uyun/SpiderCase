import re
import json
import requests
from pyquery import PyQuery as pq


url = 'https://hotels.ctrip.com/hotel/chengdu28/p1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}
res = requests.get(url,headers=headers).content.decode('utf-8')
# with open('xiecheng.html','w',encoding='utf-8')as fp:
#     fp.write(res)
# print(res)
# 使用pyquery加载HTML页面
html = pq(res)
# 抓取动态加载的价格数据
hllist = re.findall(r"htllist: '(.*?)',",res)[0]
# 将json格式字符串转为python类型 [{},{},...]
hllist = json.loads(hllist)
# 重新构建字典{’39341191‘：’299‘}
hotel_price = {}
for i in hllist:
    hotel_id = i['hotelid']
    amount = i['amount']
    hotel_price[hotel_id] = amount
print(hotel_price)

# 总页数
page_total = html('#txtpage').attr('data-pagecount')
print('总页数：',page_total)

# 取出酒店块列表，itmes方法返回的是一个生成器对象
items = html('#hotel_list > div > ul').items()
print(items)
i = 1
for ul in items:
    # 酒店id，用去拿取动态渲染的数据，
    hotel_id = ul.find('.hotel_pic a').attr('data-hotel')
    print(hotel_id)

    # 标题
    print(i)
    title = ul.find('.hotel_name > a').attr('title')
    print(title)

    # 地址
    address = ul.find('.hotel_item_htladdress').text()
    address = re.findall(r'(.*?)。 地图',address)[0]
    print(address)

    # 文字评分
    score_text = ul.find('.hotel_level').text()
    # 评分
    score = ul.find('.hotel_value').text()
    print(score_text,score)

    # 用户推荐率
    user_recommend = ul.find('.total_judgement_score').text().replace('用户推荐','')
    print(user_recommend)

    # 用户点评数
    user_comment_num = ul.find('.hotel_judgement').text().replace('源自','').replace('位住客点评','')
    print(user_comment_num)

    # 用户推荐点评语
    recommend = ul.find('.recommend').text().replace('\n',' ')
    print(recommend)

    # 价格
    price = '￥' + hotel_price[hotel_id] + '起'
    print(price)
    i += 1
    print('=============================================================')



if __name__ == '__main__':
    pass