import scrapy
import json
class zhihuSpider(scrapy.Spider):
    headers = {
        'Host': 'www.zhihu.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Referer': 'https://www.zhihu.com/people/excited-vczh/following',
        'X-UDID': 'AJBCD9iXpgyPTl5cmXmohBKioOd6n52PRnU='
    }
    cookies = {
    'aliyungf_tc': 'AQAAAMkKDBvYJwAAMcqrcwFn80lAIq8l',
    'q_c1': 'b35923c3fc804dd4814005ad1e28680a|1510118306000|1510118306000',
    '_xsrf': '87f7f822c6e5b6278710c686b8840062',
    'r_cap_id': "MWMzMjk4ZWM2M2M1NDNlOTg1MDU4MzQ3ZDIzODIyNzg=|1510118306|6106e3f57fbc75daf5c34f5bec3185127a0e4445",
    'cap_id': "MmVmYTVkZjRlMzczNGMwNWFkNzkzNDI0NjZhM2ExZTE=|1510118306|785797df37ba32fa2613a9472be2db1adca670ed",
    'd_c0': "AJBCD9iXpgyPTl5cmXmohBKioOd6n52PRnU=|1510118306",
    '_zap': '0584e8c2-3a1e-4eb7-bb88-3e67e957d354',
    '__utma': '51854390.356158762.1510118310.1510118310.1510118310.1',
    '__utmb': '51854390.0.10.1510118310',
    '__utmc': '1854390',
    '__utmz': '51854390.1510118310.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
    '__utmv': '51854390.000--|3=entry_date=20171108=1',
    'z_c0': 'Mi4xSzMtTEF3QUFBQUFBa0VJUDJKZW1EQmNBQUFCaEFsVk5hZUx2V2dER1JSbnZPVHI2bVNkTHVEc1g4ZTNTU2Vub3Fn|1510118505|0aa1d47d0bf131145f2afa0bfdf705b59b79904e',
    'n_c': '1',

    }
    name = 'ZhiHuSpider'
    #获取它关注信息
    def start_requests(self):

        yield scrapy.Request(
            #他关注的人
            # url='https://www.zhihu.com/api/v4/members/excited-vczh/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20',
            # 爬取个人粉丝(关注他的人)
            url='https://www.zhihu.com/api/v4/members/excited-vczh/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20',
            # url='https://www.zhihu.com/api/v4/members/yuanshuai1020?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics',
            headers=self.headers,
            cookies=self.cookies,

        )
    def parse(self, response):
        page=0
        data = json.loads(response.text)
        if data and 'paging' in data.keys():
            if 'totals' in data['paging'].keys():
                count = int(data['paging']['totals'])
                if count%20:
                    page = int(count/20 + 1)
                else:
                    page = int(count/20)
        print('-----一共有多少页----->',page)

        offset = 20
        for i in range(0,1):
            url='https://www.zhihu.com/api/v4/members/excited-vczh/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={0}&limit=20'.format(offset)
            offset += 20
            yield scrapy.Request(
                url = url,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.downlod_dara,
            )
    def downlod_dara(self,response):
        data = json.loads(response.text)
        if  data and 'data' in data.keys():
            fensi_info = data['data']#20条粉丝信息
            for one_info in fensi_info:
                url_token = one_info['url_token']
                print('==正在爬取{0}================'.format(url_token))

                url = 'https://www.zhihu.com/api/v4/members/{0}/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'.format(url_token)
                print(url)
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies,
                    callback=self.parse,
                    # meta={'url_token':url_token}
                )
                #拿到粉丝信息，拼接详情路由，进入到详情

    def detail_fensi(self,response):
        url_token = response.meta['url_token']
        yield scrapy.Request(
            url='https://www.zhihu.com/api/v4/members/{0}/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'.format(url_token),
            headers=self.headers,
            cookies=self.cookies,
            callback=self.parse,
        )
        # print(response.text)