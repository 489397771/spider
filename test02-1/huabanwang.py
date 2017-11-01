from urllib.parse import urlencode
import requests
from requests.exceptions import RequestException
import re
import os
from hashlib import md5
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread


SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
BASE_PATH = r'G:\data\spider\test02'
path = r'D:\python\phantomjs-2.1.1-windows\bin\phantomjs.exe'
driver = webdriver.PhantomJS(service_args=SERVICE_ARGS, executable_path=path)
wait = WebDriverWait(driver, 5)


def get_start_url(headers, num='24431205'):
    data = {
        'j9f1pnx2': '',
        'max': num,
        'limit': '20',
        'wfl': '1',
    }
    url = 'http://huaban.com/boards/favorite/beauty/?'
    url = url + urlencode(data)
    response = requests.get(url, headers=headers, timeout=10)
    try:
        if response.status_code == 200:
            boards_pattern = re.compile(r'{"board_id":.*?"extra":.*?}}', re.S)
            boards_info = boards_pattern.findall(response.text)
            return boards_info
    except RequestException:
        print('首页请求错误')
        return None


def get_page_data(info):
    board_pattern = re.compile(r'{"board_id":(.*?),.*"title":"(.*?)",.*')
    board_data = board_pattern.search(info).groups(1)
    return {
        'board_id': board_data[0],
        'title': board_data[1],
    }


def get_page_detail(boards_id, headers):
    url = 'http://huaban.com/boards/' + boards_id
    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            pin_pattern = re.compile(r'{"pin_id":.*?"tags":.*?]', re.S)
            pin_info = pin_pattern.findall(response.text)
            return pin_info
    except RequestException:
        print('详情页请求失败')
        return None


def get_detail_data(detail):
    detail_pattern = re.compile(r'pin_id":(\d+)', re.S)
    detail_data = detail_pattern.findall(str(detail))
    return detail_data


def get_pin_id(pin_id, headers):
    data = {
        'j9gmtif7': '',
        'max': pin_id,
        'limit': '20',
        'wfl': '1',
    }
    url = 'http://huaban.com/boards/27943718/?'
    url = url + urlencode(data)
    response = requests.get(url, headers)
    try:
        if response.status_code == 200:
            pin_pattern = re.compile(r'{"pin_id":.*?"tags":.*?]', re.S)
            pin_info = pin_pattern.findall(response.text)
            return pin_info
    except RequestException:
        print('请求失败')
        return None


def get_img_data(pin_id, headers, title):
    url = 'http://huaban.com/pins/' + pin_id + '/relatedboards/'
    html = get_doc(url, '#pin_view_page')
    try:
        soup = BeautifulSoup(html, 'lxml')
        img_url1 = soup.select('#baidu_image_holder > a > img')
        img_url2 = soup.select('#baidu_image_holder > img')
        url = 'http:' + (img_url1 + img_url2)[0]['src']
        download_img(url, headers, title)
        return None
    except EnvironmentError:
        print('图片html请求错误')
        return None


def get_doc(url, param):
    if url:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, param)))
        html = driver.page_source
        return html
    else:
        pass


def download_img(url, headers, title):
    if url:
        print('正在下载', url)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # response.content 是返回二进制内容，图片一般用content，而网页一般用text
                save_img(response.content, title)
                print('下载完成', url)
            return None
        except RequestException:
            print('请求图片失败', url)
            return None
    else:
        pass


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


def start_thread(pin_id_list, headers, title):
    # 先将pin_id_list处理成单个的
    if len(pin_id_list) < 0:
        print('开启线程1')
        for i in range(len(pin_id_list)):
            t = Thread(target=get_img_data, args=(pin_id_list[i], headers, title))
            t.start()
    else:
        print("未获取pin_id_list")
        pass


def main(headers):
    board_id_list = ['24431205']
    for board_id in board_id_list:
        get_start_url(headers, board_id)
        for info in get_start_url(headers, board_id):
            board_data = get_page_data(str(info[:80]))
            detail_list = get_page_detail(board_data['board_id'], headers)
            pin_id_list = get_detail_data(detail_list)
            pin_index_list = [pin_id_list[-1]]
            for pinid in pin_index_list:
                pin_id = get_pin_id(pinid, headers)
                # pin_id 为返回的列表
                pin_id_list.extend(pin_id)
                print(pin_id_list)
                print('--' * 50)
                pin_index_list.append(pin_id_list[-1])
                start_thread(pin_id_list, headers, board_data['title'])
                print(pin_index_list)
                print('-1-'*30)
        board_id_list.append(board_data.get('board_id'))
        print(board_id_list)


if __name__ == '__main__':
    headers = {
        'Cookie': '_uab_collina=150833245547769295130238; UM_distinctid=15f2f9ecca5467-0abab654d98d4e-c303767-ff000-15f2f9ecca61ef; __gads=ID=1f88c7c3cb582b81:T=1508332457:S=ALNI_Mbsu8JMfOYDy-FjE7K2CiRa6ULOnw; referer=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Dwc2Y_FzwVNWjTAWnXXyeP8RlFGNymercklZr0zg5DZ3%26wd%3D%26eqid%3Dc8e37ad0000312b10000000359f6ebbb; _f=iVBORw0KGgoAAAANSUhEUgAAADIAAAAUCAYAAADPym6aAAADRklEQVRYR%2BWVS0hUURjHf2ekDOlBVFRkGRLSiyxRW%2FTQEATptYkeLiJCXQUuFKyN0KqECIcgQi164SKEyBIpemhUlIrRovcmEyVC7EFokMyJ78y5lzvXGXXMiaCzmbnn3HPu%2F%2FV9R6G1BkgZGqK%2BtJS6sjLa8%2FJkygyt1ALgElCp4LW7EOcfDSeBdwouxLnVvF47WGtwxhrqvyQC9AD1QJ2CduMYHAYyFBy1z2Jnm1XuGbBDwYB1pB%2FYCBTb9XzPOauAViDNfqdIEuCc31VeUJUdvGe2Nd08Qt%2BmFRHmjHKkuLExmntCoGg8IhrmAwcUnLGk3DhZIvvlHAtQgF8EDtlzS4AGBUNecez%2F8w741Vefsuzhe%2B7W7mMkZbqLNa5ojUfEgk%2Bxrjmq14hb0WrEzrV6XBHiVRadKFoKCPmM4GCtmZ%2F79hNbq5u5fbaYn%2FNmJoaIVa%2Fao7obOz8RDQ7hOotG4miipkHiWZYwIjYSohpWZYnSLakJj%2BpjreV7akbA1sgzsAsosMDleKlDGYlxxJNtpyilmJuB2ZaIt2D9ayLAdwtaCt7UnT3TEcSZP22bQvxEYjdopSbT96d6z4TvkXiJ6LbObhOx%2FJws7179oOMUqD1M09vV5tyXEWvtHeWEVA2KZDTfCKi9Ki%2F7jv%2Fbuq3zhnVOlp7LN2IR2flhFak%2F5uB2rbiJhAGX%2BMFYgr0qP2d3JImuQkL6GugGtS230oDVZPoJWyHMuSSF%2BvilWlC8CK57LHXkji39y8kaWMKXGcMkjyT9AZH2SGCm9Zq50GUCnFB5ucGxnIr1rl8Ix%2BErK7vTBpOHR%2Bm9fmAxOZ9TJ0%2FEAPfFa8xYheMiUTRO6Ucda4za6CZxyJ0bUU0ofc4RQps4cux6%2BquFH2d9TRAR%2BxECgYOSdUNM6%2FsOsAhHwqTdyEUlEsXRv0PEoyoBekU5h1SMAv43HbHxksgsFbXl19%2FFHEK2E7nr0Wokqku2Cya0RsIFblrq8TDgcEeK1gH9wL3EIjpVKFTotG9zjq2jYOaTCulUawcX0ZL2BqdepqTYPWp3o0mPdS%2B474m6SlWEOdPjtF4vEbfWYIPd1ywNQu6RhBOJeQdN4ULCbvYpxDiho8Yj8hsKqYgsqQCE5wAAAABJRU5ErkJggg%3D%3D%2CWin32.1366.768.24; _hmt=1; _ga=GA1.2.251721351.1508332456; _cnzz_CV1256903590=is-logon%7Clogged-in%7C1509370781231%26urlname%7Cfl4izib8tu%7C1509370781231; __asc=1e24599415f6d7ce82a6b8fbb2b; __auc=e68e664315f2f9ec97da0f339bc; uid=22369652; sid=kPEqx8cesXBlhsuKoO4cqyyur5I.pEKbqQl5lj7nkG3KB0v%2BT6PkKjTG7ZEwbbHpq36%2BCDg; CNZZDATA1256903590=1345701567-1508330866-null%7C1509368405',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'application/json'
    }
    main(headers)
