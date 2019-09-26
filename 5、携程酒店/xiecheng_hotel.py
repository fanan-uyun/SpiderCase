import re
import time
import json
import pymongo
import requests
import threading
from queue import Queue
from pyquery import PyQuery as pq
from fake_useragent import UserAgent
import urllib3
urllib3.disable_warnings()

sess = requests.session()

headers = {'user-agent':UserAgent().random}

class MyMongoDB():
    def __init__(self,database,sets):
        # 1.创建客户端
        self.client = pymongo.MongoClient('localhost')
        # 2.创建数据库
        self.db = self.client[database]
        # 3.创建集合
        self.collection = self.db[sets]

    def insert_one(self,dic):
        """
        一次插入一条数据
        :param dic: 字典数据
        :return:
        """
        try:
            self.collection.insert(dic)
            print('数据保存成功！')
        except:
            print('数据保存失败！')

    def insert_many(self,lst):
        """
        一次性插入多条数据
        :param lst: 列表套字典
        :return:
        """
        try:
            self.collection.insert_many(lst)
            print('数据保存成功！')
        except:
            print('数据保存失败！')

    def find(self):
        """
        查询所有数据
        :return:
        """
        data = self.collection.find()
        print('数据查询如下：')
        # users = self.collection.find({'age': {'$gt': 19}})
        for i in data:
            print(i)


class SpiderCrawl(threading.Thread):
    def __init__(self,t_name,url_queue):
        super(SpiderCrawl, self).__init__()
        # 线程名
        self.t_name = t_name
        # url队列
        self.url_queue = url_queue

    def run(self):
        while True:
            # 判断队列是否为空，为空则跳出循环，结束任务
            if self.url_queue.empty():
                break
            url = self.url_queue.get()
            print(f'\033[0;36m{self.t_name}线程开始抓取{url}\033[0m')
            self.html_request(url)
            # 睡眠2s,要不然服务器检测阻断链接
            time.sleep(2)
            print()
            print('\033[0;31m++++++++++++++++++++++++++++++++++++++++++++\033[0m')

    # 页面请求
    def html_request(self,url):
        """
        页面请求
        :param url: 目标链接
        :return: 响应的网页内容
        """
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            # 'origin': 'https://hotels.ctrip.com',
            # 'referer': 'https://hotels.ctrip.com/hotel/chengdu28/'
        }
        response = sess.get(url, headers=headers,verify=False).content.decode('utf-8')

        # print(sess.cookies)
        hotel_price = self.reset_price_data(response)

        self.html_parse(response,hotel_price)

    # 重构酒店价格数据(酒店价格为动态渲染)
    def reset_price_data(self,response):
        """
        重构酒店价格数据
        :param response: 响应的页面内容
        :return: 酒店id:价格 对应的字典数据
        """
        hotel_price = {}
        # 正则匹配js动态加载的价格数据json字符串
        try:
            hllist = re.findall(r"htllist: '(.*?)',", response)[0]
            # 将json格式字符串转为python类型 [{},{},...]
            hllist = json.loads(hllist)
            # 重新构建字典{’39341191‘：’299‘}
            # hotel_price = {}
            for i in hllist:
                # 取出酒店id
                hotel_id = i['hotelid']
                # 取出酒店价格
                amount = i['amount']
                # id:价格 键值对
                hotel_price[hotel_id] = amount
        except:
            print('没有抓取到酒店价格信息')
        return hotel_price



    # pyquery页面解析
    def html_parse(self,response,hotel_price):
        """
        页面解析
        :param response: requests请求的响应内容
        :param hotel_price: 重构的价格数据
        :return: 总页码
        """

        # 使用pyquery加载HTML页面
        html = pq(response)
        # 总页数
        # page_total = html('#txtpage').attr('data-pagecount')
        # print('总页数：', page_total)


        # 取出酒店块列表元素，itmes方法返回的是一个生成器对象
        items = html('#hotel_list > div > ul').items()

        for ul in items:
            data = {}
            # 酒店id，用去拿取动态渲染的数据，
            hotel_id = ul.find('.hotel_pic a').attr('data-hotel')
            # print(hotel_id)

            # 标题
            title = ul.find('.hotel_name > a').attr('title')
            # print(title)

            # 地址
            address = ul.find('.hotel_item_htladdress').text()
            try:
                address = re.findall(r'(.*?)。 地图', address)[0]
            except:
                address = ''
            # print(address)

            # 文字评分
            score_text = ul.find('.hotel_level').text()
            # 评分
            score = ul.find('.hotel_value').text()
            # print(score_text, score)

            # 用户推荐率
            user_recommend = ul.find('.total_judgement_score').text().replace('用户推荐', '')
            # print(user_recommend)

            # 用户点评数
            user_comment_num = ul.find('.hotel_judgement').text().replace('源自', '').replace('位住客点评', '')
            # print(user_comment_num)

            # 用户推荐点评语
            recommend = ul.find('.recommend').text().replace('\n', ' ')
            # print(recommend)

            # 价格
            if hotel_price:
                price = '￥' + hotel_price[hotel_id]
            else:
                price = ''
            # print(price)


            data['hotel_id'] = hotel_id
            data['title'] = title
            data['price'] = price
            data['score_text'] = score_text
            data['score'] = score
            data['user_recommend'] = user_recommend
            data['user_comment_num'] = user_comment_num
            data['recommend'] = recommend
            data['address'] = address

            # 实例化MongoDB
            mongo = MyMongoDB('xiecheng','hotel')
            mongo.insert_one(data)

            print(data)

            print('=============================================================')



# 创建队列
url_queue = Queue()

flag = True
if __name__ == "__main__":
    start_time = time.time()
    base_url = 'https://hotels.ctrip.com/hotel/chengdu28'
    base_res = sess.get(url=base_url,headers=headers).content.decode('utf-8')
    try:
        page = int(re.findall(r'到<input class="c_page_num" id="txtpage" type="text" value="1"data-pagecount=(.*?) name="" />页',
                      base_res, re.S)[0])
    except:
        print('暂时获取不到总页数，指定page为100')
        page = 100
    print(page)

    for i in range(1,page+1):
        url = f'https://hotels.ctrip.com/hotel/chengdu28/p{i}'
        url_queue.put(url)

    # 起线程，完成任务，指定5个任务完成所有数据的爬取
    # 指定5个任务，存放到列表中，并没有任何实际意义
    thread_names = ['T1', 'T2', 'T3','T4','T5']
    thread_list = []
    for t_name in thread_names:
        thread = SpiderCrawl(t_name, url_queue)
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    end_time = time.time()

    print(f"整个程序耗时：{end_time - start_time}")
