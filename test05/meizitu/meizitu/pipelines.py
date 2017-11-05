# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline


class ImagePipeline(ImagesPipeline):
    IMAGE_STORE = get_project_settings().get('IMAGES_STORE')

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        tpye = item['meizi_type']
        tpye_name = item['meizi_type_name']
        i = request.meta['i']
        filename = u'{0}/{1}/{2}'.format(tpye, tpye_name, str(i))
        return filename

    def get_media_requests(self, item, info):
        i = 0
        for image_url in item['image_urls']:
            i += 1
            yield scrapy.Request(image_url, meta={'item': item, 'i': i})

    def item_completed(self, results, item, info):
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('no images')
        item['imagePath'] = image_paths
        return item

