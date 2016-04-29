#!/usr/bin/python
import scrapy
import os
from dataCollector.items import DatacollectorItem

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

year = 2006
base_directory = "../../data/" + str(year) + "/"
base_url = "http://news.sina.com.cn/old1000/news1000_"

months = [x for x in range(1, 13)]
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

class sinaNewsSpider(scrapy.Spider):
    name = "sinaNews"
    allowed_domains = ['sina.com.cn']
    start_urls = [
    ]

    for year in range(year, year+1):
        for month in months:
            for day in xrange(1, days[month-1] + 1):
                start_urls.append(base_url + str(year) + str(month).zfill(2) \
                        + str(day).zfill(2) + ".shtml")

    def news_parse(self, response):
        item = response.meta['item']

        if (len(response.xpath('//h1')) > 0):
            title = response.xpath('//h1/text()').extract()[0]
        elif len(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " f24 ")]') > 0):
            title = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " f24 ")]')\
                .xpath('font/text()').extract()[0]

        for sel in response.xpath('//*[contains(concat(" ", normalize-space(@id), " "), " zoom ")]'):
            text = ""
            for psg in sel.xpath('p'):
                if len(psg.xpath('text()')) > 0:
                    text += psg.xpath('text()').extract()[0]
            psg = {'title': title, 'text': text}
        os.system("mkdir -p \"" + base_directory + '/'.join(response.url.split('/')[2:-1]) + "\"")
        filename = base_directory + '/'.join(response.url.split('/')[2:])
        filename = '.'.join(filename.split('.')[:-1] + ["txt"])
        with open(filename, "w") as f:
            f.write(psg['title'].encode("utf-8") + '\n')
            f.write(psg['text'].encode("utf-8") + '\n')

    def parse(self, response):
        for sel in response.xpath('//ul/ul/ul/li/a'):
            if sel.xpath('@href').extract() == [] or sel.xpath('text()').extract() == []:
                continue
            item = DatacollectorItem()
            item['url'] = sel.xpath('@href').extract()[0]
            item['title'] = sel.xpath('text()').extract()[0]
            yield scrapy.Request(url=item['url'], meta={'item': item}, callback=self.news_parse)
