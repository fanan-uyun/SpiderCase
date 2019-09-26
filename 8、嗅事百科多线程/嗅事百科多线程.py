import json
import time
import requests
import threading
from lxml import etree
from queue import Queue


class ThreadCrawl(threading.Thread):
    def __init__(self, threadName, pageQueue):
        #threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(ThreadCrawl, self).__init__()
        # 线程名
        self.threadName = threadName
        # 页码队列
        self.pageQueue = pageQueue
        # 请求报头
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

    def run(self):
        print("启动 " + self.threadName)
        while True:
            # 由于采集队列中数据是死的，这里只用判断采集队列中为空，即可结束循环
            if pageQueue.empty():
                break
            try:
                # 取出一个数字，先进先出
                # 可选参数block，默认值为True
                #1. 如果对列为空，block为True的话，不会结束，会进入阻塞状态，直到队列有新的数据
                #2. 如果队列为空，block为False的话，就弹出一个Queue.empty()异常，
                page = self.pageQueue.get(block=False)
                url = "http://www.qiushibaike.com/8hr/page/" + str(page) +"/"
                #print url
                content = requests.get(url, headers = self.headers).text
                time.sleep(1)
                dataQueue.put(content)
                #print len(content)
            except:
                pass
        print("结束 " + self.threadName)

class ThreadParse(threading.Thread):
    def __init__(self, threadName):
        super(ThreadParse, self).__init__()
        # 线程名
        self.threadName = threadName

    def run(self):
        print("启动" + self.threadName)
        while True: # 循环往队列中取任务
            # 只有数据response队列中为空，并且采集任务线程全部死掉才结束循环
            if dataQueue.empty() and PARSE_flag:
                break
            try:
                html = dataQueue.get(block=False)
                self.parse(html)
            except:
                pass
        print("退出" + self.threadName)

    def parse(self, html):
        # 解析为HTML DOM
        html = etree.HTML(html)

        node_list = html.xpath('//li[contains(@id, "qiushi_tag")]')
        # print("nostlist:%s"%node_list)

        for node in node_list:
            # xpath返回的列表，这个列表就这一个参数，用索引方式取出来，用户名
            username = node.xpath('.//a[@class="recmd-user"]/span/text()')[0]
            # 头像链接
            image = node.xpath('.//a[@class="recmd-user"]/img/@src')[0]
            # 取出标签下的内容,段子内容
            content = node.xpath('.//a[@class="recmd-content"]/text()')[0]
            # 取出标签里包含的内容，点赞
            zan = node.xpath('.//div[@class="recmd-num"]/span[1]/text()')[0]
            # 评论
            comments = node.xpath('.//div[@class="recmd-num"]/span[last()-1]/text()')[0]

            items = {
                "username" : username,
                "image" : image,
                "content" : content,
                "zan" : zan,
                "comments" : comments
            }

            # with 后面有两个必须执行的操作：__enter__ 和 _exit__
            # 不管里面的操作结果如何，都会执行打开、关闭
            # 打开锁、处理内容、释放锁
            with lock:
                # 写入存储的解析后的数据
                # self.filename.write(json.dumps(items, ensure_ascii = False).encode("utf-8") + "\n")
                with open('duanzi.json','a',encoding='utf-8')as fp:
                    json.dump(items,fp,ensure_ascii=False)
                    fp.write('\n')


# 解析线程标志，用于判断生产者（请求页面）线程是否全部死掉
PARSE_flag = False

# 采集结果(每页的HTML源码response)的数据队列，参数为空表示不限制
dataQueue = Queue()

# 创建锁，文件写入
lock = threading.Lock()

if __name__ == "__main__":
    start_time = time.time()
    # 页码的队列
    pageQueue = Queue()
    # 放入20个数字，先进先出
    for i in range(1, 21):
        pageQueue.put(i)

    # 三个采集线程的名字
    crawlList = ["采集线程1号", "采集线程2号", "采集线程3号"]
    # 存储三个采集线程的列表集合
    threadcrawl = []
    for threadName in crawlList:
        thread = ThreadCrawl(threadName, pageQueue)
        thread.start()
        threadcrawl.append(thread)


    # 三个解析线程的名字
    parseList = ["解析线程1号","解析线程2号","解析线程3号"]
    # 存储三个解析线程
    threadparse = []
    for threadName in parseList:
        thread = ThreadParse(threadName)
        thread.start()
        threadparse.append(thread)

    # 使用采集线程阻塞主线程
    for thread in threadcrawl:
        thread.join()

    # join容器中的线程全部死掉，标志生产者线程全部死掉，置为True
    PARSE_flag = True

    # 使用解析线程阻塞主线程
    for thread in threadparse:
        thread.join()


    end_time = time.time()
    print(f'耗时：{end_time-start_time}')