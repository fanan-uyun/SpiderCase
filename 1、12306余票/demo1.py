import requests
import numpy as np
from selenium import webdriver
import time
# from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
from base64 import b64decode

#点击 验证码刷新按钮
#0 succ
#-1 failed
def click_refresh(b):
    try:
        b.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[3]/div/div[3]").click()
        return 0
    except:
        print("click_refresh:exception!!!!")
        return -1

    return -1

#查找 立即登录按钮
#0 found
#-1 not found
def find_login_now(b):
    try:
        b.find_element_by_xpath('''//*[@id="J-login"]''')
        return 0
    except:
        #print("find_login_now:exception!!!!")
        return -1

    return -1


#click 立即登录 button
#0 正常
#-1 出错
def click_login_now(b):
    try:
        b.find_element_by_xpath('''//*[@id="J-login"]''').click()
        return 0
    except:
        print("click_login:exception!!!!")
        return -1

    return -1



#click account login
#0 正常
#-1 出错
def click_accountlogin(b):
    try:
        b.find_element_by_xpath("/html/body/div[2]/div[2]/ul/li[2]/a").click()
        return 0
    except:
        print("click_accountlogin:exception!!!!")
        return -1

    return -1


#初始化浏览器
def init_browser(b):
    b.maximize_window()

#进入登录页，必须是未登录状态
def visit_login_page(b):
    url = 'https://kyfw.12306.cn/otn/resources/login.html'
    b.get(url)
    time.sleep(5)
    click_accountlogin(b)
    time.sleep(5)#访问login page后休息5秒，等待验证码图片加载完成 


#分析js，获取验证码图片，保存为verify_code.jpg
def get_a_verify_pic(b):
    pic_name = 'verify_code.jpg'
    img_str = b.find_element_by_xpath('''//*[@id="J-loginImg"]''').get_attribute('src') # 定位图片位置，获取 src 的属性值
    img_str = img_str.split(",")[-1] # 删除前面的 “data:image/jpeg;base64,”
    img_str = img_str.replace("%0A", '\n') # 将"%0A"替换为换行符
    img_data = b64decode(img_str) # b64decode 解码
    with open(pic_name, 'wb') as fout:
        fout.write(img_data)
    time.sleep(1)

    return pic_name


# 破解图片验证码（返回图片位置）
def ana_pic(b,pic_name):
    body_list = []
    url = 'http://littlebigluo.qicp.net:47720/'
    files = {'pic_xxfile': (pic_name, open(pic_name, 'rb'), 'image/png')}
    res = requests.post(url, files=files)  # post pic
    # print(res)
    """
    ------WebKitFormBoundaryyQCryxrFdroFLJ4Y
    Content-Disposition: form-data; name="pic_xxfile"; filename="code1.png"
    Content-Type: image/png
    ------WebKitFormBoundaryyQCryxrFdroFLJ4Y--
    """

    if res.status_code == 200:  # return ok
        try:
            # print(res.text)
            if u"图片貌似选" in res.text:  # 识别验证码成功        
                body_str_1 = res.text.split(u'''<B>''')
                body_str = body_str_1[1].split(u'<')[0].split()
                for index in body_str:
                    body_list.append(int(index))
                return 0, np.array(body_list)

            else: # 没识别出来
                print('not recogonized!!!')
                return -1, None

        except Exception as e:
            print(e)
            print("ana pic failed!!!!")
            return -1, None

    print('server return is NOK!!!')
    return -1, None  # 验证码解析失败



#按输入的下标，点击一张验证码图片
def click_one_pic(b,i):
    try:
        imgelement=b.find_element_by_xpath('''//*[@id="J-loginImg"]''')
        if i<=4:
            ActionChains(b).move_to_element_with_offset(imgelement,40+72*(i-1),73).click().perform()
        else:
            i -= 4
            ActionChains(b).move_to_element_with_offset(imgelement,40+72*(i-1),145).click().perform()
    except:
        print("Wa -- click one pic except!!!")



#按bodylist 指示，点击指定验证图片
def click_pic(b,body_list):
    for i in range(len(body_list)):
        click_one_pic(b,body_list[i])
        time.sleep(1)


#输入用户名密码，并点击验证码登陆
#0:登录成功
#1:验证失败
#-1 错误异常
def login(b):
    pic_name=None
    try:

        pic_name=get_a_verify_pic(b)      #截取12306验证码图片
        ret_val,body_list=ana_pic(b,pic_name) #破解12306验证码

        username=b.find_element_by_id('J-userName')
        username.clear()
        username.send_keys('yunfancom@sina.com')
        password=b.find_element_by_id('J-password')
        password.clear()
        password.send_keys('996623077zh')
        time.sleep(2)

        if ret_val != 0:
            #print("login : what??? predict return error!!")
            print("没有验证码图片!!! !!")
            os.remove(pic_name)       #exception occured
            click_refresh(b)
            return -1

        if len(body_list) == 0:       #no pic recognized
            click_refresh(b)
            print("验证码列表为空!!!")
            os.remove(pic_name)       #exception occured
            return 1            #verified failed

        click_pic(b,body_list)
        time.sleep(1)            #休息1秒再点击登陆按钮
        if click_login_now(b) != 0:
            print("登录异常!!!")
            return -1          #Error happened!!
    except Exception as e:
        print(e)
        if None != pic_name:
            os.remove(pic_name)#exception occured
        print("登录错误!!")
        return -1

    time.sleep(5)#查看验证码是否正确??
    ret_val=find_login_now(b)
    if ret_val == 0: #验证码错误
        print("验证码错误!!!")
        return 1

    os.remove(pic_name)
    print("登录成功!!!")
    return 0


#循环login
#返回
#0：登陆成功-正常返回
#-1：登陆失败或异常返回
#1 ：验证码未识别出来
def try_login(b):
    for k in range(0,2):          #连续尝试2次
        rt_val=login(b)
        if rt_val < 0:           #error happened
            print("验证码获取异常!!")
            time.sleep(10)
            continue
        elif rt_val == 1:          #verified code error
            print("验证码，错误!!")
            time.sleep(5)
            continue            #login again
        else:                #login successfully
            print("尝试登录，成功登录!!!")
            return 0

    return -1          #login failed





# res = ana_pic('code.png')
# print(res)



if __name__ == "__main__":

    b = webdriver.Chrome()
    init_browser(b)
    visit_login_page(b)

    time.sleep(2)

    ret_val = try_login(b) #尝试登录
    if ret_val<0:
        print("登录失败!!")
    else:
        print("登录成功!!!")


