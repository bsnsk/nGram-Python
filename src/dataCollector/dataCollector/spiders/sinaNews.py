import scrapy
import os
from dataCollector.items import DatacollectorItem

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

base_directory = "../../data/"
base_url = "http://news.sina.com.cn/hotnews/"

months = [x for x in range(1, 13)]
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

class sinaNewsSpider(scrapy.Spider):
    name = "sinaNews"
    allowed_domains = ['sina.com.cn']
    start_urls = []

    for year in range(2006, 2007):
        for month in months:
            for day in xrange(1, days[month-1] + 1):
                start_urls.append(base_url + str(year) + str(month).zfill(2) \
                        + str(day).zfill(2) + ".shtml")

    def news_parse(self, response):
        item = response.meta['item']

        for sel in response.xpath('//*[contains(concat(" ", normalize-space(@id), " "), " zoom ")]'):
            text = ""
            for psg in sel.xpath('p'):
                if len(psg.xpath('text()')) > 0:
                    text += psg.xpath('text()').extract()[0]
            psg = {'title': item['title'], 'text': text}
        cur_directory = base_directory + response.url.split('/')[-2].split('-')[0] + "/"
        os.system("mkdir -p \"" + cur_directory + '/'.join(response.url.split('/')[2:-1]) + "\"")
        filename = cur_directory + '/'.join(response.url.split('/')[2:])
        filename = '.'.join(filename.split('.')[:-1] + ["txt"])
        with open(filename, "w") as f:
            f.write(psg['title'] + '\n')
            f.write(psg['text'] + '\n')

    def parse(self, response):
        for sel in response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " a01 ")]'):
            if sel.xpath('@href').extract() == [] or sel.xpath('text()').extract() == []:
                continue
            item = DatacollectorItem()
            item['url'] = sel.xpath('@href').extract()[0]
            item['title'] = sel.xpath('text()').extract()[0]
            yield scrapy.Request(url=item['url'], meta={'item': item}, callback=self.news_parse)
