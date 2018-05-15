import requests
from lxml import etree
from queue import Queue

error_url = list()
need_url = list()
q = Queue()


def get_index(in_url):
    try:
        resp = requests.get(in_url)
    except Exception as e:
        error_url.append(in_url)
        print(e, in_url)
        return None
    if resp.status_code >= 300:
        error_url.append(in_url)
        print('error', in_url)
        return None
    else:
        need_url.append(in_url)
        return resp


def get_page(resp):
    if resp is not None:
        # print(resp.url)
        # print(resp.text)
        try:
            html = etree.HTML(resp.text)
        except ValueError as e:
            print('html error', e)
            return None
        all_url = html.xpath('//a/@href')
        # print(all_url)
        for one_url in all_url:
            new_url = dispose(one_url)
            # print(new_url)
            if new_url is not None and new_url not in need_url:
                new_url = new_url.strip()
                q.put(new_url)
    else:
        pass


def dispose(url):
    if url.startswith('/') and not url.endswith('/'):
        new_url = 'http://m.sohu.com{}'.format(url)
    elif 'm.sohu.com' in url and '//m.sohu.com' not in url:
        new_url = url
    elif url.startswith('//m'):
        new_url = 'http:%s' % url
    else:
        new_url = None

    return new_url


def main(url):
    print(url)
    resp = get_index(url)
    get_page(resp)


if __name__ == '__main__':
    url = 'http://m.sohu.com/'
    q.put(url)
    while q.qsize():
        print(len(need_url))
        main(q.get())
