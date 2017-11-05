import scrapy
from scrapy.spider import Request
from meizitu.items import MeizituItem
from scrapy.utils.project import get_project_settings


class MeizituSpider(scrapy.Spider):
    name = 'meizitu'
    allowd_domains = ['http://www.meizitu.com']
    start_urls = ['http://www.meizit.com/']
    IMAGE_STORE = get_project_settings().get('IMAGES_STORE')
    def parse(self, response):

        meizi_list = response.xpath('//div[@class="sidebar"]/ul[1]/li')
        # print(meizi_list)
        for meizi in meizi_list:
            meizi_type = meizi.xpath('.//a/text()').extract()[0]
            meizi_type_url ='http://www.meizit.com' + meizi.xpath('.//a/@href').extract()[0]
            # print(meizi_type, meizi_type_url)

            yield Request(meizi_type_url, self.get_type_page, meta={'meizi_type': meizi_type, 'meizi_type_url':meizi_type_url})

    def get_type_page(self, response):
        meizi_page = response.xpath('//ul[@class="pagination"]/li/span/text()').extract()[0]
        meizi_type = response.meta['meizi_type']
        url = response.meta['meizi_type_url']
        page_index = int(meizi_page[-3:-1].replace('/', ''))
        for i in range(1, page_index+1):
            meizi_type_url = url + '&p=' + str(i)
            # print(meizi_type, page_index, meizi_type_url)
            yield Request(meizi_type_url, self.get_type_data, meta={'meizi_type': meizi_type})

    def get_type_data(self, response):
        meizi_list = response.xpath('//div[@class="head"]/a')
        meizi_type = response.meta['meizi_type']
        # print(meizi_list)
        for meizi in meizi_list:
            meizi_type_name = meizi.xpath('./text()').extract()[0].strip()
            meizi_url = 'http://www.meizit.com' + meizi.xpath('.//@href').extract()[0]
            yield Request(meizi_url, self.get_img_url, meta={'meizi_type': meizi_type, 'meizi_type_name':meizi_type_name})

    def get_img_url(self, respinse):
        item = MeizituItem()
        urls = []
        # names = []
        item['meizi_type'] = respinse.meta['meizi_type']
        item['meizi_type_name'] = respinse.meta['meizi_type_name']
        meizi_img_list = respinse.xpath('//div[@class="content"]/img')
        # print(item['meizi_type'], item['meizi_type_name'])
        for meizi_img in meizi_img_list:
            meizi_img_url = meizi_img.xpath('./@src').extract()[0]
            urls.append(meizi_img_url)
        item['image_urls'] = urls
        yield item


