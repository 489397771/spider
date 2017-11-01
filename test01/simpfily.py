from urllib.parse import urlencode
import json
import re
from hashlib import md5
import os
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
import pymongo
from multiprocessing import Pool
from config import MONGO_TABLE, MONGO_DB, MONGO_URL, BASE_PATH, GROUP_END, GROUP_START, KEYWORD


coon = pymongo.MongoClient(MONGO_URL, connect=False)
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
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页失败')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('url')


def get_page_detail(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页失败', url)
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select_one('title').get_text()
    images_pattern = re.compile('content:(.*?)replace', re.S)
    result = re.search(images_pattern, html)
    if result:
        parse_img_pattern = re.compile(r';(http://p\d\.pstatp\.com/large/\w+)&quot;', re.S)
        images = re.findall(parse_img_pattern, result.group(1))
        for image in images:
            download_img(image, title)
        return {
            'title': title,
            'url': url,
            'images': images
        }


def save_to_mondb(result):
    if result:
        db[MONGO_TABLE].insert(result)
        print('插入数据库成功', result)
        return True
    return False


def download_img(url, title):
    print('正在下载', url)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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
    pool = Pool(processes=4)
    for x in range(GROUP_START, GROUP_END):
        groups = 20*x
        pool.apply_async(main, (groups, KEYWORD, x))
    pool.close()
    pool.join()
