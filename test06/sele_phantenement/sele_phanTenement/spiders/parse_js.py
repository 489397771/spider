import re
import os
import requests
from scrapy.utils.project import get_project_settings


class ParseJS(object):
    BASE_PATH = get_project_settings().get("BASE_PATH")

    def parseIt(self):
        js = requests.get('http://j2.58cdn.com.cn/js/v7/hp/search.js?v=30')
        comp = re.compile('dsy\.add\((.*?)\);')
        temp_result = comp.findall(js.text)
        request_dict = {}
        province_names = re.sub('"', '', temp_result[0][6:-1]).split(',')
        for i in range(len(province_names)):
            pattern = re.compile('[\w]+|[\u4e00-\u9fa5]+', re.S)
            city_list = pattern.findall(temp_result[i + 1])
            for j in range(1, len(city_list), 2):
                request_dict[city_list[j]] = '{0}\{1}'.format(province_names[i], city_list[j + 1])
        for path in request_dict.values():
            city_path = os.path.join(self.BASE_PATH, path)
            print(city_path)
            if not os.path.exists(city_path):
                os.makedirs(city_path)
            else:
                print(city_path, "已存在")
        return request_dict


if __name__ == '__main__':
    mm = ParseJS()
    mm.parseIt()
