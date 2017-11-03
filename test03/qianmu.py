import re
import pymongo
import threading
import requests
import pandas as pd
from multiprocessing import Pool
from bs4 import BeautifulSoup
from requests.exceptions import RequestException



MONGO_URL = 'localhost'
MONGO_DB = 'qianmu'
MONGO_TABLE = 'qianmu'
coon = pymongo.MongoClient(MONGO_URL, connect=False)
db = coon[MONGO_DB]


def save_to_mongdb(data, name):
    if data:
        db[MONGO_TABLE].insert(data)
        print('插入数据库成功', name)
        return True
    return False


def page_index(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            a_pattern = re.compile(r'<td><a (.*?)</a>', re.S)
            a_all = re.findall(a_pattern, str(soup))
            return a_all
        return None
    except RequestException:
        print('index请求错误')
        return None


def page_href(a_all):
    for i in range(0, len(a_all)-1):
        href_pattern = re.compile(r'href="(.*)" t', re.S)
        href = re.findall(href_pattern, a_all[i])
        yield href


def page_detail(href, headers):
    # print(href)
    try:
        response = requests.get(href, headers=headers, timeout=10)
        if response.status_code == 200:
            html = response.text
            info = page_info(html)
            # print(href)
            # print(info)
            info_analysis(info)
        return None
    except RequestException:
        print('请求错误', href)
        return None


def thread_page_detail(href, headers):
    th = []
    t = threading.Thread(target=page_detail, args=(href, headers))
    th.append(t)
    t.start()


def page_info(html):
    info = {}
    if html:
        soup = BeautifulSoup(html, 'lxml')
        title = soup.select('#wikiContent > h1')[0].get_text()
        info['name'] = title
        try:
            tbody = soup.find('tbody')
            tr = tbody.find_all('tr')
            for tbs in tr:
                tds = tbs.find_all('td')
                try:
                    info[tds[0].get_text().strip()] = tds[1].get_text().strip()
                except IndexError:
                    print('表格写入错误')
            return info
        except AttributeError:
            print('没有tbody')
        return info
    else:
        pass


def info_analysis(info):
    data = {}
    if info is not None:
        data['school name'] = info.get('name', '')
        data['stu_num'] = info.get('本科生人数', '')
        data['postgraduate_num'] = info.get('研究生人数', '')
        data['pupil_ratio'] = info.get('师生比', '')
        data['stu_ratio'] = info.get('国际学生比例', '')
        data['url'] = info.get('网址', '')
        data['address'] = info.get('国家', '') + info.get('州省', '') \
                          + info.get('城市', '')
        # save_to_mongdb(data, data['school name'])
        save_csv(data, data['school name'])
        return data
    else:
        pass


def save_csv(data, title):
    dataframe = pd.DataFrame.from_dict(data, orient='index').T
    dataframe.to_csv('QM.csv', mode='a')
    print('完成' + title + '存储')


def main(url, headers):
    i = 0
    a_all = page_index(url, headers)
    href = page_href(a_all)

    for url in href:
        page_detail(url[0], headers)
        # 多进程
        # pool = Pool(2)
        # pool.apply_async(page_detail, (url[0], headers))
    # 多线程
    # for url in href:
    #     i += 1
    #     print(i)
    #     pool = Pool(2)
    #     pool.apply_async(page_detail, (url[0], headers))
    return 'SUCCESS'


if __name__ == '__main__':
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
    url = 'http://www.qianmu.org/2018USNEWS%E4%B8%96%E7%95%8C%E5%A4%A7%E5%AD%A6%E6%8E%92%E5%90%8D'
    main(url, headers)
