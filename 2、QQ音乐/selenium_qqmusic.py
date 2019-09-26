import requests
from selenium import webdriver
# 实例化浏览器
driver = webdriver.Chrome()
# req = requests.utils.quote('https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&w=%E5%91%A8%E6%9D%B0%E4%BC%A6',encoding='utf-8')

# 请求
driver.get('https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&w=%E5%91%A8%E6%9D%B0%E4%BC%A6')
driver.implicitly_wait(10)
url = driver.find_element_by_xpath('//div[@class="songlist__item"]//a').get_attribute('href')
print(url)