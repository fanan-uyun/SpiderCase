import re
import io
import csv
import time
import json
import base64
import random
import pymysql
import datetime
import requests
from lxml import etree
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent


class Down_Mysql():
    def __init__(self):
        self.connect = pymysql.connect(
            host='localhost',
            db='anjuke',
            user='root',
            password='q1q1q1',
            charset = 'utf8'
        )
        self.cursor = self.connect.cursor()  # 创建游标

    # 保存到数据库
    def save_mysql(self,image,title,bedroom_num,living_room_num,area,floor,floors,agent,neighborhood,city_area,bussiness_area,address,rent_way,face_direction,subline,price,save_time):
        sql = "insert into fangyuan(image,title,bedroom_num,living_room_num,area,floor,floors,agent,neighborhood,city_area,bussiness_area,address,rent_way,face_direction,subline,price,save_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            self.cursor.execute(sql, (image,title,bedroom_num,living_room_num,area,floor,floors,agent,neighborhood,city_area,bussiness_area,address,rent_way,face_direction,subline,price,save_time))
            self.connect.commit()
            print('数据插入成功')
        except Exception as e:
            print(e)
            print("插入数据失败")

class Anjuke():
    # 判断是否为空
    def is_empty(self, data):
        if len(data) > 0:
            return data[0]
        else:
            return ''

    # 写入csv文件
    def write_csv(self,dict_info, filename):
       '''
       将所有数据写入到csv文档中
       '''
       list_info = ['image','title','bedroom_num','living_room_num','area','floor','floors','agent','neighborhood',
    'city_area','bussiness_area','address','rent_way','face_direction','subline','price','save_time']

       with open(filename, 'a+', encoding='utf-8', newline="") as csv_info:
           # 创建csv写对象
           csv_w = csv.writer(csv_info)
           info = [str(dict_info.get(item)) for item in list_info]
           print(info)
           with open(filename, "r", encoding='utf-8', newline="") as csv_info:
               # 创建csv读对象
               reader = csv.reader(csv_info)
               if not [row for row in reader]:
                   csv_w.writerow(list_info)
                   csv_w.writerow(info)
               else:
                   csv_w.writerow(info)

    # 字体解密
    def fonts_parse(self,response):
        # 定义一个空字典 {'0x9476': 8,....}
        newmap = dict()
        try:
            # 获取加密字符串
            key_str = re.search(r"base64,(.*?)'\)",response).group(1)
            # base64解码
            b = base64.b64decode(key_str)
            # 生成二进制字节
            font = TTFont(io.BytesIO(b))
            # #十进制ascii码到字形名的对应{38006:'glyph00002',...}
            bestcmap = font['cmap'].getBestCmap()
            # 定义一个空字典 {'0x9476': 8,....}
            # newmap = dict()
            for key in bestcmap.keys():
                value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1 # 对应数字0-9
                key = hex(key) # 十进制转换为十六进制
                newmap[key] = value # 保存到字典
            # print(newmap)
        except:
            pass

        # 把页面上自定义字体替换成正常字体
        response_ = response
        for key,value in newmap.items():
            # 拼接成抓到到的网页中的字体内容 ，&#x9f92;&#x9fa5;
            key_ = key.replace('0x','&#x') + ';'
            if key_ in response_:
                response_ = response_.replace(key_,str(value))


        return response_

    # 请求url,返回html页面
    def get_url(self,url):
        # ua池
        # ua = UserAgent()
        # headers = {
        #     'User-Agent': ua.random
        # }
        headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            }
        proxies_list = [
            {
                'http':'http://218.66.253.144:8800',
                'https':'https://111.231.92.21:8888'
            },
            {
                'http': 'http://183.146.29.224:8888',
            },
            {
                'http': 'http://118.31.61.70:3128',
            },
            {
                'http': 'http://113.121.40.249:808',
            },
            {
                'http': 'http://113.121.38.178:61234',
            },
            {
                'http': 'http://39.137.69.10:80',
            },
            {
                'http': 'http://122.114.222.93:8888',
            },
            {
                'http': 'http://112.12.91.30:8888',
            },
            {
                'http': 'http://140.143.156.166:1080',
            },
            {
                'http': 'http://47.107.175.190:8000',
            },
            {
                'http': 'http://183.146.29.43:8888',
            },

        ]
        proxies = random.choice(proxies_list)
        print(proxies)
        response = requests.get(url,headers=headers,proxies=proxies).text
        # tree = etree.HTML(response)
        return response

    # 获取安居客N-S首字母开头的城市链接
    def request_city_list(self):
        print('''
            1.官网获取城市链接
            2.本地文件获取城市链接
        ''')
        num = input("请选择获取城市链接的方式“：")
        while True:
            global response
            if num == '1':
                url = 'https://www.anjuke.com/sy-city.html'
                response = self.get_url(url)
                break
            elif num == '2':
                with open("city_list.html",'r',encoding='utf-8')as fp:
                    response = fp.read()
                    break
        # print(response)
        # 再进行结构转换
        tree = etree.HTML(response)
        # 获取N(13)-S(17)的城市url
        city_list_ul = tree.xpath('//div[@class="letter_city"]//li[position()<18][position()>12]')
        city_dict = {}
        for city_list in city_list_ul:
            # name = city_list.xpath('./label/text()')
            city_name_list = city_list.xpath('.//a/text()')
            city_name_url_list = city_list.xpath('.//a/@href')
            for city,city_url in zip(city_name_list,city_name_url_list):
                # print(city,city_url)
                city_dict[city] = city_url
        # print(city_dict)
        return city_dict


    # 根据获取到的城市url获取判断该城市有无租房信息，返回城市租房链接（字典）
    def get_zufang_url(self):
        city_zufang_dict = {}
        # 使用函数 返回N-S城市url，字典
        city_dict = self.request_city_list()
        for city in city_dict.keys():
            # 城市url
            city_url = city_dict[city]
            # 使用函数，请求返回文本页面
            response = self.get_url(city_url)
            tree = etree.HTML(response)
            # 获取该城市的租房url
            zufang_url = None
            house_list = tree.xpath('//li[@class="li_single li_itemsnew li_unselected"][a="租 房"]/a/@href')
            if house_list:
                zufang_url = "".join(house_list)
                city_zufang_dict[city] = zufang_url
                print("已抓取到[%s]的租房链接"%city)

            else:
                zufang_url = "[%s]无租房信息"%city
            print(zufang_url)
            time.sleep(1)
        # with open('zufang_url_list.json', 'w',encoding='utf-8') as fp:
        #     json.dump(city_zufang_dict,fp,ensure_ascii=False)

        print(len(city_zufang_dict)) # 71

        return city_zufang_dict


    # 获取房源信息
    def get_fangyuan(self,tree,city):
        # 房源块信息
        div_list = tree.xpath('//div[@class="zu-itemmod"]')
        # print(len(div_list))
        div_page = tree.xpath('//div[@class="page-content"]//i[@class="iNxt"]/text()')
        # print(div_page)
        for div in div_list:
            data_info = {}
            # 1.租房图片链接
            image_url = div.xpath('.//img[@class="thumbnail"]/@lazy_src')[0]
            # print(image_url)
            # 2.标题
            title = div.xpath('./div[@class="zu-info"]//b/text()')[0]
            print(title)
            # 3.室
            bedroom_num = div.xpath('.//p[@class="details-item tag"]/b[1]/text()')[0]
            # bedroom_num = int(bedroom_num)
            print(bedroom_num)
            # 4.厅
            living_room_num_list = div.xpath('.//p[@class="details-item tag"]/b[2]/text()')
            if living_room_num_list:
                living_room_num = living_room_num_list[0]
                # living_room_num = int(living_room_num)
            else:
                living_room_num = None
            # print(living_room_num)
            # 5.面积
            area = div.xpath('.//p[@class="details-item tag"]/b[last()]/text()')[0]
            area = area + "m²"
            # print(area)
            # 6.楼层
            floor = div.xpath('.//p[@class="details-item tag"]/text()')[4].strip()
            floor1 = floor.split('(',)
            if len(floor1) > 1:
                floor1 = floor1[0]
            else:
                floor1 = None
            # print(floor1)
            # 7.总楼层
            floors = re.findall(r'\d+',floor)[0]
            # print(floors)
            # 8.经纪人
            try:
                agent = div.xpath('.//p[@class="details-item tag"]/text()')
                agent = agent[len(agent)-1].strip()
            except:
                agent = ""
            print(agent)
            # print(agent)
            # 9.小区名
            neighborhood = div.xpath('.//address/a/text()')
            neigh = "".join(neighborhood)
            # print(neigh)
            # 10.城区
            try:
                city_area_list = div.xpath('.//address/text()')[1].strip().split(' ')
                city_area_lst = city_area_list[0].split('-')
                city_area = city_area_lst[0]
                # print(city_area)
            except:
                city_area = ""
            # 11.商圈
            try:
                bussiness_area = city_area_lst[1]
                # print(bussiness_area)
            except:
                bussiness_area = ""
            # 12.地址
            try:
                address = city_area_list[1]
            except:
                address = ""
            # print(address)
            # 13.租房方式
            rent_way = div.xpath('.//p[@class="details-item bot-tag"]/span[1]/text()')
            rent_way = self.is_empty(rent_way)
            # print(rent_way)
            # 14.朝向
            face_direction = div.xpath('.//p[@class="details-item bot-tag"]/span[2]/text()')
            face_direction = self.is_empty(face_direction)
            # print(face_direction)
            # 15.地铁线
            subline = div.xpath('.//p[@class="details-item bot-tag"]//span[contains(text(),"线")]/text()')
            subline = "".join(subline)
            # print(subline)
            # 16.价格
            price = div.xpath('./div[@class="zu-side"]//b/text()')
            price = self.is_empty(price) + "元/月"
            # print(price)
            # 17.数据存储时间
            save_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 以csv文件方式存储
            # data_info['image'] = image_url
            # data_info['title'] = title
            # data_info['bedroom_num'] = bedroom_num
            # data_info['living_room_num'] = living_room_num
            # data_info['area'] = area
            # data_info['floor'] = floor1
            # data_info['floors'] = floors
            # data_info['agent'] = agent
            # data_info['neighborhood'] = neigh
            # data_info['city_area'] = city_area
            # data_info['bussiness_area'] = bussiness_area
            # data_info['address'] = address
            # data_info['rent_way'] = rent_way
            # data_info['face_direction'] = face_direction
            # data_info['subline'] = subline
            # data_info['price'] = price
            # data_info['save_time'] = save_time
            # self.write_csv(data_info,"%s_fangyuan.csv"%city)

            # mysql存储，实例化数据库
            db = Down_Mysql()
            db.save_mysql(image_url,title,bedroom_num,living_room_num,area,floor1,floors,agent,neigh,city_area,bussiness_area,address,rent_way,face_direction,subline,price,save_time)


        return div_page

    # 拼接完整的页面租房链接,进行房源信息的爬取
    def split_page_url(self):
        page_url = {}
        print('''
            1.官网获取城市租房链接
            2.本地文件获取城市租房链接
        ''')
        num = input("请选择获取城市租房链接的方式：")
        while True:
            global zufang_url_dict
            if num == '1':
                # ①页面获取
                zufang_url_dict = self.get_zufang_url()
                break
            elif num == '2':
                # ②本地获取
                with open('zufang_url_list.json','r',encoding='utf-8')as fp:
                    zufang_url_dict = json.load(fp)
                    break
                    # print(zufang_url_dict)
        for city in zufang_url_dict.keys():
            # 城市租房链接
            city_zufang_url = zufang_url_dict[city]
            print(city_zufang_url)
            # 拼接完整的租房url地址
            for page in range(1,51):
                city_zufang_page_url = city_zufang_url + 'fangyuan/p{}/'.format(page)
                print(f"========================正在爬取{city}第{page}页数据==================================")
                # page_url[city] = city_zufang_page_url
                page_response = self.get_url(city_zufang_page_url)
                # 字体解密
                parse_response = self.fonts_parse(page_response)
                parse_tree = etree.HTML(parse_response)
                # 获取房源信息
                next = self.get_fangyuan(parse_tree,city)
                if next:
                    break

                print(f"========================成功爬取{city}第{page}页数据==================================")

                time.sleep(1)


if __name__ == '__main__':
    anjuke = Anjuke()
    anjuke.split_page_url()



