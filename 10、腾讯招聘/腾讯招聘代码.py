import time
import requests
import threading
from queue import Queue
from fake_useragent import UserAgent

'''
    根据“"请求"和"解析"来进行生产消费者模式
'''

# 生产者线程类
class ProductThread(threading.Thread):
    # 继承父类init
    def __init__(self,j,page_queue):
        super().__init__()
        self.j = j
        self.page_queue = page_queue

    # 重写run方法
    def run(self):
        # 线程不能只干一个任务就退出，需要不断取任务
        while True:
            # 任务停止条件：当任务队列为空的时候，线程退出
            if self.page_queue.empty():
                break
            try:
                page = self.page_queue.get(block=False)
                print(f"===========生产者{self.j}任务开始执行{page}========")
                url = f'https://careers.tencent.com/tencentcareer/api/post/Query?keyword=python&pageIndex={page}&pageSize=10'
                self.get_url(url)
                print(f"===========生产者{self.j}任务完成{page}===========")
            except:
                pass

    # 请求方法
    def get_url(self,url):
        # 实例化useragent
        ua = UserAgent()
        useragent = ua.random
        headers = {
            'User-Agent': useragent
        }
        response = requests.get(url, headers=headers).json()
        # with open('txzp.json','w',encoding='utf-8')as fp:
        #     fp.write(response)

        # return response
        response_queue.put(response)



class ConsumerThread(threading.Thread):
    # 继承父类init
    def __init__(self,k):
        super().__init__()
        self.k = k

    # 重写run方法
    def run(self):
        # 线程不能只干一个任务就退出，需要不断取任务
        while True:
            # 任务停止条件：（1）任务队列为空 （2）生产者线程全部死掉
            if response_queue.empty() and flag:
                break
            # 异常判断：跳过队列为空的报错
            try:
                # block=False主要为了解决队列为空时或两个消费者同时取剩下的一个response时程序等待的状态
                response = response_queue.get(block=False)
                print(f"***********消费者{self.k}任务开始执行*******")
                self.parse_response(response)
                print(f"***********消费者{self.j}任务完成**********")
            except:
                pass

    # 解析方法
    def parse_response(self,response):
        job_list = response['Data']['Posts']
        for job in job_list:
            # 工作岗位
            job_name = job['RecruitPostName']
            # 工作地点
            job_address = job['LocationName']
            # 岗位职责
            Responsibility = job['Responsibility'].replace('\n', '').replace('\r', '')
            # 详情url
            PostURL = job['PostURL']
            # 拼接保存信息
            info = f'工作岗位：{job_name}，工作地点：{job_address}，岗位职责：{Responsibility}，工作详情：{PostURL}'

            # 上锁，并自动释放锁
            with lock:
                with open('腾讯招聘1.txt', 'a', encoding='utf-8')as fp:
                    fp.write(info + '\n')

# 创建锁，用于文件写入
lock = threading.Lock()

# 创建消费者队列（响应解析），存放生产者生产的响应
response_queue = Queue()

# 定义一个flag，用于判断生产者线程是否全部死掉
flag = False

# 主线程
if __name__ == '__main__':
    # 主进程开始时间
    start_time = time.time()
    # 创建生产者队列（请求）
    page_queue = Queue()
    for i in range(1,88):
        # 将页码存入队列
        page_queue.put(i)

    # 起线程，完成任务，指定3个任务完成所有数据的爬取
    # 指定3个任务，存放到列表中，并没有任何实际意义（也可以使用range）
    # 生产者任务（线程）
    p_task_name = ['p1', 'p2', 'p3']
    # 消费者任务（线程）
    c_task_name = ['c1', 'c2', 'c3']
    # 存储生产者线程列表，用于阻塞主线程
    p_thread_list = []
    # 存储消费者线程列表，用于阻塞主线程
    c_thread_list = []
    # 开始生产者，页面请求线程
    for j in p_task_name:
        p_task = ProductThread(j,page_queue)
        p_task.start()
        p_thread_list.append(p_task)

    # 开始消费者，响应解析线程
    for k in c_task_name:
        c_task = ConsumerThread(k)
        c_task.start()
        c_thread_list.append(c_task)

    # 根据每个子线程去阻塞主线程，本程序重点部分(难点)
    # join是一个容器,它里面存放着线程t1和线程t2和t3,他们不死光,主线程不死
    # 他们全部死光,不管容器外面还有没有其他线程,主线程都死
    # 使用生产者阻塞主进程
    for p_task in p_thread_list:
        p_task.join()

    # 如果生产者线程全部死掉，则将flag状态置为True
    flag = True

    # 使用消费者阻塞主进程
    for c_task in c_thread_list:
        c_task.join()

    # 主进程结束时间
    end_time = time.time()

    print(f"整个程序耗时：{end_time-start_time}")



