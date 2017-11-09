
from scrapy.spiders import Request
from selenium import webdriver
from scrapy.http import HtmlResponse


class PhantomJSMiddleware(object):

    @classmethod
    def process_request(cls, request, spider):
        if request.meta.get('PhantomJS'):
            print('Selenium开始运行')
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            content = driver.page_source
            driver.quit()
            print('Selenium运行结束')
            return HtmlResponse(request.url, body=content, encoding='utf-8', request=request)