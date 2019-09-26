import requests
import random
from pprint import pprint

session = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}



# 生成验证码图片
def make_verification_code():
    # 获取验证码图片
    code_pic_name = 'code1.png'
    code_pic_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image'
    code_res = session.get(url=code_pic_url, headers=headers).content
    with open(code_pic_name, 'wb')as fp:
        fp.write(code_res)
        print('生成验证码成功！')

    return code_pic_name

# 验证码图片坐标
def code_position():
    # 利用随机模块生成8张图片的坐标
    position_dic = {
        '1': f'{random.randint(5,67)},{random.randint(5,67)}',
        '2': f'{random.randint(67+5,67*2+5)},{random.randint(5,67)}',
        '3': f'{random.randint(67*2+5+5,67*3+5+5)},{random.randint(5,67)}',
        '4': f'{random.randint(67*3+5+5+5,67*4+5+5+5)},{random.randint(5,67)}',
        '5': f'{random.randint(5,67)},{random.randint(67+5,67*2+5)}',
        '6': f'{random.randint(67+5,67*2+5)},{random.randint(67+5,67*2+5)}',
        '7': f'{random.randint(67*2+5+5,67*3+5+5)},{random.randint(67+5,67*2+5)}',
        '8': f'{random.randint(67*3+5+5+5,67*4+5+5+5)},{random.randint(67+5,67*2+5)}'
    }
    pprint(position_dic)
    return position_dic

# 验证码校验
def code_valid(position_dic):
    coorList = []
    pos = input('请输入图片位置(1-8)：')
    pos_list = pos.split(',')
    for p in pos_list:
        coorList.append(position_dic[p])
    position = ','.join(coorList)
    print('验证码坐标：',position)

    url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
    params = {
        'answer': position,
        'rand': 'sjrand',
        'login_site': 'E'
    }
    response = session.get(url=url,headers=headers,params=params)
    print(response.text)
    return position

def login(position):
    url = 'https://kyfw.12306.cn/passport/web/login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'https://kyfw.12306.cn/otn/resources/login.html'
    }
    session.cookies.update(
        {
            'RAIL_EXPIRATION':'1569132689668',
            'RAIL_DEVICEID':'Ry6Q7Tkau6lvtQFj-1-qD3Mrde9MOKac4kGC5MCLRvgQ5ADb2vySV_SptrTnvjckvQxVWcocw7621ci-T2TmMlg4pChroHuQoXvciR1XyZ52i4ZSiS_dClAx8x_Ck3tg_4or7LxX15-nWH7ilOFn53WcrBup-bN8',
            'route':'c5c62a339e7744272a54643b3be5bf64'
        }
    )
    data = {
        'username': '账户',
        'password': '密码',
        'appid': 'otn',
        'answer': position
    }
    response = session.post(url=url,headers=headers,data=data).content.decode('utf-8')
    print('是否登录成功',response)


if __name__ == '__main__':
    # 生成验证码图片
    code_pic_name = make_verification_code()
    # 生成验证码图片坐标
    position_dic = code_position()
    # 验证码校验
    position = code_valid(position_dic)
    # 登录
    login(position)
