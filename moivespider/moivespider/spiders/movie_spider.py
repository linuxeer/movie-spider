# -*- coding: utf-8 -*-
import scrapy
import json
from urlparse import urljoin


class MovieSpiderSpider(scrapy.Spider):
    name = "movie-spider"
    crawled_movies = []
    allowed_domains = ["https://movie.douban.com/", "http://www.dytt8.net/", 'http://www.ygdy8.net']
    start_urls = [
        "http://www.ygdy8.net/html/gndy/dyzz/index.html",
        "http://www.ygdy8.net/html/gndy/china/index.html",
        "http://www.ygdy8.net/html/gndy/oumei/index.html",
        "http://www.ygdy8.net/html/gndy/rihan/index.html"
    ]

    # 解析出所有的分页地址
    def parse(self, response):
        for sel in response.xpath('//select[@name="sldd"]//option/@value'):
            url = urljoin(response.url, sel.extract())
            yield scrapy.Request(url, callback = self.parse_movie, dont_filter = True)

    # 解析出所有的电影名和此电影的详情页地址
    def parse_movie(self, response):
        for sel in response.xpath('//div[@class="co_content8"]//td//b'):
            title = sel.xpath('a[re:test(@href,"/html/gndy/.+/\d+.html")]/text()').extract()[0].encode('utf-8')
            url = "http://www.ygdy8.net/" + sel.xpath('a[re:test(@href,"/html/gndy/.+/\d+.html")]/@href').extract()[0].encode('utf-8')
            begin = title.index("《")
            end = title.index("》")
            yield scrapy.Request('https://movie.douban.com/j/subject_suggest?q=' + title[begin + 3:end], callback = self.parse_douban_url, dont_filter = True,
                                 headers = {"User-Agent": "Mozilla/5.0"}, meta = {"name": title[begin + 3:end], "url": url})

    # 解析电影详情页地址
    def parse_douban_url(self, response):
        res = json.loads(response.body)
        url = res[0]['url']
        yield scrapy.Request(url, callback = self.parse_rating_num, headers = {"User-Agent": "Mozilla/5.0"}, dont_filter = True,
                             meta = {"name": response.meta["name"], "url": response.meta["url"]})

    # 解析打分
    def parse_rating_num(self, response):
        rate_num = float(response.xpath('//strong[contains(@class,"rating_num")]/text()').extract()[0])
        if rate_num > 8.0:
            print response.meta['name'], '[', rate_num, ']', response.meta['url']
