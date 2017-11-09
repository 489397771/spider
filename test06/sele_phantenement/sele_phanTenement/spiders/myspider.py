import re
import time
from scrapy.spiders import Spider, Request, Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from .parse_js import ParseJS
from sele_phanTenement.items import SelePhantenementItem


class MySpider(CrawlSpider):

    name = 'sel_phanTenement'
    parjs = ParseJS()
    fol_dict = parjs.parseIt()
    rules = (
        Rule(LinkExtractor(allow=('http://[a-z]+.58.com/(chuzu/pn\d+/|chuzu/)$'),
                           deny=('http://[a-z]+.58.com/chuzu/jh\w*', 'http://callback.58.com/\w*')),
             callback='parseContent', follow=True),
    )
    count = 0
    err = 0

    def start_requests(self):
        url = 'http://www.58.com/changecity.html?catepath=chuzu&catename=%E5%87%BA%E7%A7%9F&fullpath=1,37031'
        yield Request(url, self.parse, meta={'PhantomJS': True})

    def parseContent(self, response):
        # print('1.才进来--', response.url)
        item = SelePhantenementItem()
        time.sleep(2)
        if self.isExists(response):
            print('4.进来了--', response.url)
            pattern = re.compile('http://([a-z]+).58.com/\w*')
            try:
                fol_key = pattern.findall(response.url)[0]
                fol_name = self.fol_dict[fol_key]
                item['name'] = fol_name
                print('名字', fol_name)
            except Exception as e:
                print('key值错误--', e, '错误的url--', response.url)
                item['name'] = 'error'
            print('5.请求url:', response.url)
            onePage = response.xpath('//ul[@class="listUl"]/li')
            time.sleep(1)
            for one in onePage[:-1]:
                try:
                    addr = []
                    item['title'] = one.xpath('./div[@class="des"]/h2/a/text()').extract()[0].strip()
                    # href = one.xpath('./div[@class="des"]/h2/a/@href').extract()[0]
                    item['detail'] = one.xpath('./div[@class="des"]/p[@class="room"]/text()').extract()[0].strip()
                    adds = one.xpath('./div[@class="des"]/p[@class="add"]')

                    for oneadr in adds:
                        address = oneadr.xpath('string(.)').extract()[0]
                        adr_rel = re.sub('\W', '', address)
                        addr.append(adr_rel)
                    item['address'] = addr
                    item['money'] = one.xpath('./div[@class="listliright"]/div[@class="money"]/b/text()').extract()[0]
                    sendTime = one.xpath('./div[@class="listliright"]/div[@class="sendTime"]/text()').extract()[ 0].strip()
                    if not sendTime:
                        item['sendTime'] = '最近'
                    else:
                        item['sendTime'] = sendTime
                    # print('6.抓完数据--', item['name'])
                    yield item
                except Exception as e:
                    self.err += 1
                    print('爬取页面报错--', e, '错误的url--', response.url, self.err)
                    pass
            self.count += 1
            print('++++++++++++++++++', self.count)
            # if self.count % 8 == 0:
            #     print('休息中....')
            #     time.sleep(10)

    def isExists(self, res):
        # print('2.验证的url--', res.url)
        pattern = re.compile('http://([a-z]+).58.com/\w*')
        fol_key = pattern.findall(res.url)[0]
        # print(fol_key)
        if self.fol_dict.get(fol_key):
            if not res.xpath('//ul/li[@class="noresult"]'):
                # print('3.验证完了--', res.url)
                return True
            else:
                return False
        else:
            return False
