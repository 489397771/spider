from urllib.parse import urlencode
import json
import re
from hashlib import md5

import os
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
import pymongo
# 开启进程，引入进程池
from multiprocessing import Pool
from config import MONGO_TABLE, MONGO_DB, MONGO_URL, BASE_PATH, GROUP_END, GROUP_START, KEYWORD

# 连接服务器
coon = pymongo.MongoClient(MONGO_URL, connect=False)
# 连接数据库
db = coon[MONGO_DB]


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
    }
    # urlencode 是将字典转换为参数传到url中
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    print(url)
    response = requests.get(url)
    try:
        # 判断是否连接成功
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页失败')
        return None


# 解析json数据
def parse_page_index(html):
    # loads针对内存对象，即将Python内置数据序列化为字串
    # 把Json格式字符串解码转换成Python对象   json.loads() 传入参数必须是字典格式的字符串
    # 编码：把一个Python对象编码转换成Json字符串 json.dumps()
    # html必须是字典格式的字符串
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('url')


# 请求详情页网址
def get_page_detail(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页失败', url)
        return None


# 处理详情页数据
def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    # select_one:只查询第一个元素
    # select：查找所有元素select_one()=select().[0]但select()查询不到会报error而select_one()会返回None。
    # get_text()方法获取到tag中包含的所有文版内容包括子孙tag中的内容,并将结果作为Unicode字符串返回,即在该标签下的所有去除标签及属性的文字内容
    title = soup.select_one('title').get_text()
    # compile 生成re格式的匹配样式
    images_pattern = re.compile('content:(.*?)replace', re.S)
    # 进行正则匹配
    result = re.search(images_pattern, html)
    if result:
        # group()，同group（0）就是匹配正则表达式整体结果
        # group(1)列出第一个括号匹配部分，group(2)列出第二个括号匹配部分，group(3)列出第三个括号匹配部分。
        parse_img_pattern = re.compile(r';(http://p\d\.pstatp\.com/large/\w+)&quot;', re.S)
        images = re.findall(parse_img_pattern, result.group(1))
        for image in images:
            download_img(image, title)
        return {
            'title': title,
            'url': url,
            'images': images
        }


# 插入数据库
# 先要保证返回有数据再存储，否则mongodb会报错
# "TypeError: 'NoneType' object is not iterable"
# 函数返回值为None，并被赋给了多个变量。
def save_to_mondb(result):
    if result:
        db[MONGO_TABLE].insert(result)
        print('插入数据库成功', result)
        return True
    return False


# 下载图片
def download_img(url, title):
    print('正在下载', url)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # response.content 是返回二进制内容，图片一般用content，而网页一般用text
            save_img(response.content, title)
        return None
    except RequestException:
        print('请求图片失败', url)
        return None


def save_img(content, title):
    path_name = re.sub('\W', '', title).strip()
    file_title = os.path.join(BASE_PATH, path_name)
    if not os.path.isdir(file_title):
        os.mkdir(file_title)
    # hexdigest()是加密一种方式
    file_path = '{0}/{1}.{2}'.format(file_title, md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb')as f:
            f.write(content)
            f.close()


def main(offset, keyword, flag):
    html = get_page_index(offset, keyword)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            save_to_mondb(result)
            print('进程：' + str(flag))


if __name__ == '__main__':
    # 开启进程 设置进程数
    pool = Pool(processes=4)
    for x in range(GROUP_START, GROUP_END):
        groups = 20*x
        pool.apply_async(main, (groups, KEYWORD, x))
    # 调用join之前，先调用close函数，否则会出错。
    # 执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    pool.close()
    pool.join()
    # for x in range(GROUP_START, GROUP_END):
    #     groups = 20*x
    #     main(groups, KEYWORD, x)
