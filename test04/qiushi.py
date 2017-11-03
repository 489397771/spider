import time
import requests
import threading
import json
from queue import Queue
from lxml import etree


class TreadCrawl(threading.Thread):
    def __init__(self, threadname, pagequeue, dataqueue):
        super(TreadCrawl, self).__init__()
        self.threadname = threadname
        self.pagequeue = pagequeue
        self.dataqueue = dataqueue
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}

    def run(self):
        print('启动' + self.threadname)
        while not CRAWL_EXIT:
            try:
                page = self.pagequeue.get(False)
                url = 'https://www.qiushibaike.com/8hr/page/' + str(page) + '/'
                html = requests.get(url, headers=self.headers).text
                time.sleep(1)
                self.dataqueue.put(html)
            except:
                pass
        print("结束" + self.threadname)


class ThreadParse(threading.Thread):
    def __init__(self, threadname, dataqueue, filename, lock):
        super(ThreadParse, self).__init__()
        self.threadname = threadname
        self.dataqueue = dataqueue
        self.filename = filename
        self.lock = lock

    def run(self):
        print('启动' + self.threadname)
        while not PARSE_EXIT:
            try:
                # print(self.dataqueue.get())
                html = self.dataqueue.get(False)
                self.parse(html)
            except:
                pass
        print('退出' + self.threadname)

    def parse(self, html):

        text = etree.HTML(html)
        node_list = text.xpath('//div[contains(@id,"qiushi_tag")]')
        # print(node_list)
        for node in node_list:
            username = node.xpath('./div/a/img/@alt')[0]
            content = node.xpath('.//div[@class="content"]/span')[0].text.strip()
            img_url = node.xpath('.//div[@class="thumb"]//@src')
            items = {
                'username': username,
                'content': content,
                'img_url': img_url,
            }
            with self.lock:
                self.filename.write(json.dumps(items, ensure_ascii=False) + "\n")

CRAWL_EXIT = False
PARSE_EXIT = False


def main():
    filename = open("duanzi.txt", 'a')

    pagequeue = Queue(20)
    for i in range(1, 21):
        pagequeue.put(i)
    dataqueue = Queue()


    # 创建锁
    lock = threading.Lock()
    crawllist = ['采集线程1号', '采集线程2号', '采集线程3号']
    threadcrawl = []
    for threadname in crawllist:
        thread = TreadCrawl(threadname, pagequeue, dataqueue)
        thread.start()
        threadcrawl.append(thread)

    parseList = ["解析线程1号", "解析线程2号", "解析线程3号"]
    threadparse = []
    for threadname in parseList:
        thread = ThreadParse(threadname, dataqueue, filename, lock)
        thread.start()
        threadparse.append(thread)

    while not pagequeue.empty():
        pass

    global CRAWL_EXIT
    CRAWL_EXIT = True
    print("pagequeue为空")

    for thread in threadcrawl:
        thread.join()
        print("1")

    while not dataqueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True

    for thread in threadparse:
        thread.join()
        print("2")

    with lock:
        # 关闭文件
        print(filename)
    print("全部结束")


if __name__ == '__main__':
    main()