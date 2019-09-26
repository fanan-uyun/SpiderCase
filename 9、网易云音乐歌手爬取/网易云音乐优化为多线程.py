import time
import requests
import threading
from lxml import etree
from queue import Queue



# 请求主url，获取歌单地区分类url，一个线程就可以
class SingerCountry(threading.Thread):
    # 初始化
    def __init__(self,url):
        super().__init__()
        self.url = url
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        # 返回歌手页面内容
        self.singer_response = requests.get(self.url, headers=self.headers).text
        # 转HTML结构
        self.tree = etree.HTML(self.singer_response)


    # 重写run方法
    def run(self):
        singer_class_list = self.tree.xpath('//div[@class="blk"]')
        # 歌手分类
        for singer_class in singer_class_list:
            # 歌手地区分类名
            singer_class_name = singer_class.xpath('.//a[@class="cat-flag"]/text()')
            # 歌手地区分类名url
            singer_class_href = singer_class.xpath('.//a[@class="cat-flag"]/@href')
            # 遍历地区歌手类型及对应的url链接
            for cls, href in zip(singer_class_name, singer_class_href):
                base_url = 'https://music.163.com'
                # 拼接完整的url
                class_url = base_url + href
                # 由于爬取的歌手地区分类名字带/，将其切分或替换
                cls_name = cls.split('/')[0]
                # print(f"==============================={cls_name}=======================================")
                # print(class_url)
                country_queue.put(class_url)

# 请求地区分类url二级页面，获取以首字母方式分类的歌手信息url
class SingerAph(threading.Thread):
    # 初始化
    def __init__(self,i):
        super().__init__()
        # 任务名称（线程）
        self.i = i
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }



    # 重写run方法
    def run(self):
        while True:
            # 如果二级队列中为空并且所有线程死掉，则提出任务队列
            if country_queue.empty() and country_flag:
                break
            try:
                # 从二级链接队列中取出url
                country_url = country_queue.get(block=False)
                # 返回歌手页面内容
                print(f"================{self.i}二级页面任务开始执行====================")
                singer_response = requests.get(country_url, headers=self.headers).text
                # 转HTML结构
                singer_tree = etree.HTML(singer_response)
                # 请求二级页面,保存歌手分类页面
                # 转换歌手分类页面结构
                # 以首字母方式获取歌手信息页面
                non_letters = singer_tree.xpath('//ul[@id="initial-selector"]/li[position()>1]/a/text()')
                non_letters_href = singer_tree.xpath('//ul[@id="initial-selector"]/li[position()>1]/a/@href')
                base_url = 'https://music.163.com'
                for letter, letter_url in zip(non_letters, non_letters_href):
                    # letter:ABC....
                    letter_dir_url = base_url + letter_url
                    letter_queue.put(letter_dir_url)
                print(f"================{self.i}二级页面任务完成====================")
            except:
                pass


# 三级页面，请求首字母分类链接，获取最终数据
class SingerParse(threading.Thread):
    # 初始化
    def __init__(self,j):
        super().__init__()
        self.j = j
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }


    # 重写run，解析页面，爬取指定数据
    def run(self):
        while True:
            # 如果三级队列中为空并且所有线程死掉，则退出任务队列
            if letter_queue.empty() and letter_flag:
                break
            try:
                # 从三级链接队列中取出url
                letter_url = letter_queue.get(block=False)
                print(f"================{self.j}三级页面任务开始执行====================")
                # 返回歌手页面内容
                singer_response = requests.get(letter_url, headers=self.headers).text
                # 转HTML结构
                letter_tree = etree.HTML(singer_response)

                # 请求三级页面
                # singer_names = []
                singer_name = letter_tree.xpath('//ul[@id="m-artist-box"]//a[@class="nm nm-icn f-thide s-fc0"]/text()')
                print(len(singer_name))
                # singer_names += singer_name
                # 保存到类变量列表中
                # print(singer_names)
                # print(len(singer_names))
                for name in singer_name:
                    with lock:
                        with open('wangyi.txt','a',encoding='utf-8')as fp:
                            fp.write(name+'\n')

                print(f"================{self.j}三级页面任务开始执行====================")
            except:
                pass

# 文件锁
lock = threading.Lock()

# 地区分类url队列
country_queue = Queue()
country_flag = False

# 歌手分类url队列
letter_queue = Queue()
letter_flag = False

if __name__ == '__main__':
    start_time = time.time()
    # 请求一级页面
    url = 'https://music.163.com/discover/artist'
    # 一级消费者线程
    singer_country = SingerCountry(url)
    singer_country.start()

    # 二级页面，创建线程任务
    singer2_name = ['S1','S2','S3','S4','S5']
    # 子线程列表
    singer2_thread_list = []
    for i in singer2_name:
        singer2 = SingerAph(i)
        singer2.start()
        singer2_thread_list.append(singer2)

    # 三级页面，创建线程任务
    singer3_name = ['T1', 'T2', 'T3', 'T4', 'T5']
    # 子线程列表
    singer3_thread_list = []
    for j in singer3_name:
        singer3 = SingerParse(j)
        singer3.start()
        singer3_thread_list.append(singer3)

    singer_country.join()
    country_flag = True

    for s2 in singer2_thread_list:
        s2.join()
    letter_flag = True

    for s3 in singer3_thread_list:
        s3.join()


    end_time = time.time()

    print(f'耗时：{end_time-start_time}秒')



