import re
import os
import json
import datetime
import requests
from prettytable import PrettyTable  # dos窗口输出美观化，pycharm没作用
from colorama import init,Fore,Back,Style


sess = requests.session()


# headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
# }


init(autoreset=False)
class Colored():
    """
    后面加RESET避免后面的字符串受到前面颜色渲染的影响，置为默认
    """
    #  字体：淡红色
    def red(self, c):
        return Fore.LIGHTRED_EX + c + Fore.RESET
    #  字体：淡绿色
    def green(self, c):
        return Fore.LIGHTGREEN_EX + c + Fore.RESET
    #  字体：淡黄色
    def yellow(self, c):
        return Fore.LIGHTYELLOW_EX + c + Fore.RESET
    #  字体：淡白色
    def white(self,c):
        return Fore.LIGHTWHITE_EX + c + Fore.RESET
    #  字体：淡蓝色
    def blue(self,c):
        return Fore.LIGHTBLUE_EX + c + Fore.RESET
    #  字体：品红
    def magenta(self,c):
        return Fore.MAGENTA + c + Fore.RESET
    #  字体：绿色
    def green1(self,c):
        return Fore.GREEN + c + Fore.RESET
    #  字体：淡青色
    def cyan(self,c):
        return Fore.LIGHTCYAN_EX + c + Fore.RESET

class TicketCrawl():
    def __init__(self):
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        # 车站：车站代码
        self.station = None
        # 车站代码：车站
        self.station_names = None

    # 获取车站名称及对应代码
    def get_station_code(self):
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9110'

        response = sess.get(url,headers=self.headers).text
        # print(response)
        # pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
        # result = re.findall(pattern, response)
        result = re.findall(r'([\u4e00-\u9fff]+)\|([A-Z]+)',response)
        # 将车站与车站代码转为字典类型
        self.station = dict(result)
        # 将车站和车站代码位置调换，用于后面的转化 BJP:北京西
        self.station_names = dict(zip(self.station.values(), self.station.keys()))
        # print(station)
        return self.station,self.station_names


    # 获取车票信息
    def get_ticket_info(self,station):
        # 调用系统本地时间（出发时间）
        # date = time.strftime("%Y-%m-%d", time.localtime())
        time_original = input('请输入出发日期：\n')
        time_format = datetime.datetime.strptime(time_original, '%Y%m%d')
        tomorrow_date = time_format.strftime('%Y-%m-%d')
        # now_date = datetime.date.today()
        # tomorrow_date = now_date + datetime.timedelta(days=input('请输入'))
        print(tomorrow_date)
        # 起始站
        from_station = station[input('请输入出发车站：\n')]
        # 目的站
        to_station = station[input('请输入到达车站：\n')]
        sess.cookies.update(
            {
                'RAIL_EXPIRATION': '1569132689668',
                'RAIL_DEVICEID': 'Ry6Q7Tkau6lvtQFj-1-qD3Mrde9MOKac4kGC5MCLRvgQ5ADb2vySV_SptrTnvjckvQxVWcocw7621ci-T2TmMlg4pChroHuQoXvciR1XyZ52i4ZSiS_dClAx8x_Ck3tg_4or7LxX15-nWH7ilOFn53WcrBup-bN8',
                'route': 'c5c62a339e7744272a54643b3be5bf64'
            }
        )
        params = {
            'leftTicketDTO.train_date': tomorrow_date,
            'leftTicketDTO.from_station': from_station,
            'leftTicketDTO.to_station': to_station,
            'purpose_codes': 'ADULT'
        }
        ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?'
        ticket = sess.get(url=ticket_url,headers=self.headers,params=params).content.decode('utf-8')
        # print(ticket)
        # 转化为python字典
        ticket = json.loads(ticket)
        return ticket

    # 展示详细车票余票信息
    def show_ticket(self,ticket,station_names):
        # 实例化一个PerttyTable对象并添加表头信息字段--余票信息字段
        table = PrettyTable(
            ["\t车次","\t出发站“","到达站","\t出发时间","到达时间","历时","商务座\t",
             "一等座","二等座","高级软卧","软卧","动卧"," 硬卧","软座","硬座",
             "\t无座","其他","备注"]
        )
        # table.align = 'l'
        # 从python字典数据中取出所有车次余票信息，并遍历
        ticket_list = ticket['data']['result']
        for t in ticket_list:
            data_dic = {}
            data_list = t.split('|')
            # for i in enumerate(data_list):
            #     print(i)
            # print(data_list)
            # print(len(data_list))
            # 车次
            train_num = data_list[3]
            # 出发站
            from_station_name = data_list[6]
            # 到达站
            to_station_name = data_list[7]
            # 出发时间
            start_time = data_list[8]
            # 到达时间
            arrive_time = data_list[9]
            # 历时
            took_time = data_list[10]
            # 商务座
            business = data_list[32] or data_list[25]
            # 一等座
            first = data_list[31]
            # 二等座
            second = data_list[30]
            # 高级软卧
            high_soft_sleeper = data_list[21]
            # 软卧
            soft_sleeper = data_list[23]
            # 动卧
            act_sleeper = data_list[27]
            # 硬卧
            hard_sleeper = data_list[28]
            # 软座
            soft_seat = data_list[24]
            # 硬座
            hard_seat = data_list[29]
            # 无座
            no_seat = data_list[26]
            # 其他
            other = data_list[22]
            # 备注
            remark = data_list[1]
            # 保存到字典
            data_dic['train_num'] = train_num
            data_dic['from_station_name'] = from_station_name
            data_dic['to_station_name'] = to_station_name
            data_dic['start_time'] = start_time
            data_dic['arrive_time'] = arrive_time
            data_dic['took_time'] = took_time
            data_dic['business'] = business
            data_dic['first'] = first
            data_dic['second'] = second
            data_dic['high_soft_sleeper'] = high_soft_sleeper
            data_dic['soft_sleeper'] = soft_sleeper
            data_dic['act_sleeper'] = act_sleeper
            data_dic['hard_sleeper'] = hard_sleeper
            data_dic['soft_seat'] = soft_seat
            data_dic['hard_seat'] = hard_seat
            data_dic['no_seat'] = no_seat
            data_dic['other'] = other
            data_dic['remark'] = remark
            color = Colored()  # 创建Colored对象
            data_dic["remark"] = color.blue(data_list[1])
            # 替换空白字符为--
            for data in data_dic:
                if data_dic[data] == '':
                    data_dic[data] = '--'
            # print(data_dic)



            # 用于存储字段颜色渲染之后的每一个车次的余票信息，PrettyTable行数据添加
            ticket_info = []
            # 开始指定数据的颜色渲染
            for name in data_dic:
                # 找到出发站，渲染为淡绿色
                if name == "from_station_name":
                    c = color.green(station_names[data_dic['from_station_name']])
                    ticket_info.append(c)
                # 找到到达站，渲染为淡红色
                elif name == "to_station_name":
                    c = color.red(station_names[data_dic["to_station_name"]])
                    ticket_info.append(c)
                # 找到出发时间，渲染为淡绿色
                elif name == "start_time":
                    c = color.green(data_dic['start_time'])
                    ticket_info.append(c)
                # 找到到达时间，渲染为淡红色
                elif name == "arrive_time":
                    c = color.red(data_dic["arrive_time"])
                    ticket_info.append(c)
                # 找到车次，渲染为淡黄色
                elif name == "train_num":
                    c = color.yellow(data_dic['train_num'])
                    ticket_info.append(c)
                # 一等座，淡青色
                elif name == "first":
                    c = color.cyan(data_dic['first'])
                    ticket_info.append(c)
                # 硬卧，品红
                elif name == "hard_sleeper":
                    c = color.magenta(data_dic['hard_sleeper'])
                    ticket_info.append(c)
                # 硬座，绿色
                elif name == "hard_seat":
                    c = color.green1(data_dic['hard_seat'])
                    ticket_info.append(c)
                # 其他信息，保持默认颜色
                else:
                    ticket_info.append(data_dic[name])


            # 按行添加数据，进行prettytable表格展示，参数为列表：列表为一条记录
            table.add_row(ticket_info)
        # 展示表格输出效果
        print(table)



if __name__ == '__main__':

    # station,station_names = get_station_code()
    # ticket = get_ticket_info(station)
    # show_ticket(ticket,station_names)
    # 实例化车票抓取类
    ticket_crawl = TicketCrawl()
    # 返回车站与车站代码互相对应的字典
    station,station_names = ticket_crawl.get_station_code()
    # 请求车票信息接口，转化为python字典类型并返回
    ticket = ticket_crawl.get_ticket_info(station)
    # 开始解析爬取车票信息，格式化输出
    ticket_crawl.show_ticket(ticket,station_names)

    os.system('pause')